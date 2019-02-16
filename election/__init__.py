# coding: utf-8

from flask import Flask, request, session, redirect, url_for, abort, render_template, g, jsonify

import secrets, random

from main.controller import md, num as cnum
from main.model import privileges as mprivileges, tags as mtags, user as muser, reviews as mreviews
from model import Election, Nomination, Question, Vote
import traceback as tb, json

app = Flask(__name__)
app.config.update(dict(
    SECRET_KEY='S6b9ySuzI2Uv55aY3To8'
))
md.md_apply(app)

f = open("pidata.json", "r")
pidata = json.loads(f.read())
f.close()
SITE_LABEL = pidata["label"]

f = open("version.json", "r")
pivers = json.loads(f.read())
f.close()
__version__ = pivers["election"]

@app.context_processor
def prepare_template_context():
    user = muser.getCurrentUser()
    if user.isDeleted():
        session.pop('login', None)
        user = muser.User.blank()

    notifications = user.getNotifications()
    moderator_tags = mtags.moderator_only

    g.random_number = random.randint
    g.num2suff = cnum.num2suff

    def countNotifications(notif):
        count = 0
        for n in notif:
            count += 1 if (n["visibility"] == 2) else 0
        return count

    g.countNotifications = countNotifications

    return {
        "user": user,
        "review": mreviews,
        "user_messages": notifications,
        "moderator_tags": moderator_tags,
        "privileges": mprivileges,
        "global_notification": "",
        "in_beta": False,
        "is_offline": False,
        "site_label": SITE_LABEL,
        "__version__": __version__,
        "num2suff": cnum.num2suff
    }

@app.before_request
def prepare_request():
    user = muser.getCurrentUser()
    if not user.isLoggedIn():
        return redirect("/help/redirected/elections")

@app.route('/')
def index():
    return redirect("/election/list")

@app.route('/list')
def list():
    return render_template("list.html", title=u"Wahlen", thispage="elections", data=Election.getAll())

@app.route('/vote/<int:id>')
def vote(id):
    if not Election.exists(id):
        abort(404)
    e = Election(id)
    cuser = muser.getCurrentUser()
    votes = Vote.from_user(e.id, cuser)
    if votes is not None:
        votes = votes.as_list()
    else:
        votes = (0, 0)
    return render_template(
        "votepage.html",
        title=e.getTitle(),
        thispage="elections",
        vote_name=e.getTitle(),
        vote_message=e.getMessage(),
        candminrep=e.getMinCandRep(),
        vote_places=e.getPlaces(),
        vote_state=e.getState(),
        vote_position=e.getPosition(),
        vote_id=id,
        vote_candidate=Nomination.from_election(id),
        user_vote={
            "is1": lambda x:x == votes[0],
            "is2": lambda x:x == votes[1]
        })

@app.route('/editor')
def editor():
    cuser = muser.getCurrentUser()
    if not cuser.isDev():
        abort(404)
    return render_template("editor.html", title=u"Bearbeiten", thispage="editor", data=Election.getAll())

@app.route('/new')
def new():
    cuser = muser.getCurrentUser()
    if not cuser.isDev():
        abort(404)
    newid = Election.new()
    return redirect(url_for("edit", id=newid))

@app.route('/edit/<int:id>')
def edit(id):
    if not Election.exists(id):
        abort(404)
    e = Election(id)
    cuser = muser.getCurrentUser()
    if not cuser.isDev():
        abort(404)
    return render_template(
        "editpage.html",
        title="[Bearbeiten]" + e.getTitle(),
        thispage="elections",
        vote_name=e.getTitle(),
        vote_message=e.getMessage(),
        vote_places=e.getPlaces(),
        vote_state=e.getState(),
        vote_position=e.getPosition(),
        vote_id=id,
        vote_candidate=e.getCandidates())

@app.route('/tally/<int:id>', methods=["GET", "POST"])
def tally(id):
    cuser = muser.getCurrentUser()
    if not cuser.isDev():
        abort(404)
    if not Election.exists(id):
        abort(404)
    e = Election(id)
    results = e.tallyVotes()
    return jsonify(results)

@app.route('/candidate/<int:id>', methods=["POST"])
def candidate(id):
    if not Election.exists(id):
        abort(404)
    e = Election(id)
    cuser = muser.getCurrentUser()
    if not Nomination.exists(id, cuser):
        if cuser.getReputation() >= e.getMinCandRep():
            Nomination.new(id, cuser, request.json["message"])
    else:
        Nomination.from_user(id, cuser).setDetail("message", request.json["message"])
    return ""

@app.route('/api/<int:id>', methods=["POST"])
def api(id):
    if not Election.exists(id):
        abort(404)
    e = Election(id)
    cuser = muser.getCurrentUser()
    command = request.json
    if not command.get("action", False):
        return ""
    action = command["action"]
    if action == "retract":
        nomination = Nomination(command["candidate"])
        if (nomination.getCandidate() == cuser.id or cuser.isDev()) and nomination.getDetail("state") == 0:
            nomination.setDetail("state", -2)
    elif action == "ask":
        n = Nomination(command["candidate"])
        if e.getState() == 3 and cuser.id != n.getCandidate().id:
            Question.new(e.id, n.id, cuser, command["message"], False)
    elif action == "answer":
        n = Nomination(command["candidate"])
        quest = Question(command["question"])
        if e.getState() in [3, 4] and cuser.id == n.getCandidate().id:
            if quest.getNomId() == n.id:
                quest.setA(command["answer"])
                if command["answer"] == "":
                    quest.setState(0)
                elif quest.isLate():
                    quest.setState(1)
                else:
                    quest.setState(2)
    elif action == "update" and cuser.isDev():
        e.setDetail("title", command["name"])
        e.setDetail("position", command["position"])
        e.setDetail("message", command["message"])
        e.setDetail("places", command["places"])
        e.setDetail("state", command["state"])
    elif action == "vote":
        v = Vote.from_user(e.id, cuser)
        if v == None:
            v = Vote.new(e.id, cuser)
        if command["vote"] == 1:
            v.setFirstVote(command["candidate"])
        else:
            v.setSecondVote(command["candidate"])
    elif action == "tally":
        results = e.tallyVotes()
        for el in results["elected"]:
            Nomination(el).setDetail("state", 1)
    elif action == "untally":
        cand = e.getCandidates()
        for c in cand:
            if c.getDetail("state") == 1:
                c.setDetail("state", 0)
    return ""

@app.errorhandler(404)
def error404(x):
    return render_template('error404.html', title="404 Nicht gefunden"), 404

@app.errorhandler(500)
def error500(x):
    data = tb.format_exc()
    data = data.decode("utf-8")
    return render_template('error500.html', data=data, title="500 Server-Fehler"), 500
