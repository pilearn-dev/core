# coding: utf-8

from flask import Flask, request, session, redirect, url_for, abort, render_template, g, jsonify, Response

import secrets, random

from main.controller import md, num as cnum
from main.model import privileges as mprivileges, tags as mtags, user as muser, reviews as mreviews, forum as mforum
from model import Election, Nomination, Question, Vote
import traceback as tb, json, datetime, time

app = Flask(__name__)
app.config.update(dict(
    SECRET_KEY='S6b9ySuzI2Uv55aY3To8'
))
md.md_apply(app)

f = open("pidata.json", "r")
pidata = json.loads(f.read())
f.close()
SITE_LABEL = pidata["label"]
SENTRY_ERROR_LOGGING = pidata["sentry_error_logging"]
MATOMO_SITE_ID = pidata["matomo_site_id"]
if SENTRY_ERROR_LOGGING:
    sentry_sdk.init(
        dsn=pidata["sentry_logging_key"],
        integrations=[FlaskIntegration()]
    )

f = open("version.json", "r")
pivers = json.loads(f.read())
f.close()
__version__ = pivers["election"]

IS_INACCESSIBLE = False

@app.context_processor
def prepare_template_context():
    user = muser.getCurrentUser()
    if user.isDeleted():
        session.pop('login', None)
        user = muser.User.blank()

    notifications = user.getNotifications()

    g.random_number = random.randint
    g.num2suff = cnum.num2suff

    if SENTRY_ERROR_LOGGING:
        with sentry_sdk.configure_scope() as scope:
            scope.user = {
                "id": user.id,
                "username": user.getHTMLName(False)
            }

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
        "privileges": mprivileges,
        "global_notification": "",
        "in_beta": False,
        "is_offline": False,
        "site_label": SITE_LABEL,
        "__version__": __version__,
        "num2suff": cnum.num2suff,
        "matomo_site_id": MATOMO_SITE_ID,
        "featured_announcements": mforum.ForumAnnouncement.byForumFeatured(0)
    }

@app.before_request
def prepare_request():
    user = muser.getCurrentUser()
    if not user.isLoggedIn():
        return redirect("/help/redirected/elections")

@app.route('/')
def index():
    return render_template("list.html", title=u"Wahlen", thispage="elections", data=Election.getAll(), Nomination=Nomination)

@app.route('/<int:id>')
def vote(id):
    if not Election.exists(id):
        abort(404)
    e = Election(id)

    e.updateByTime()

    cuser = muser.getCurrentUser()
    votes = Vote.from_user(e.id, cuser)
    if votes is not None:
        votes = votes.as_list()
    else:
        votes = (0, 0, 0)
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
            "is2": lambda x:x == votes[1],
            "is3": lambda x:x == votes[2]
        },
        vote_scheduler=e.getScheduleDatetime)

@app.route('/new')
def new():
    cuser = muser.getCurrentUser()
    if not cuser.isDev():
        abort(404)
    newid = Election.new()
    return redirect(url_for("edit", id=newid))

@app.route('/<int:id>/edit')
def edit(id):
    if not Election.exists(id):
        abort(404)
    e = Election(id)
    e.updateByTime()
    cuser = muser.getCurrentUser()
    if not cuser.isDev():
        abort(404)
    return render_template(
        "editpage.html",
        title="Bearbeiten: " + e.getTitle(),
        thispage="elections",
        vote_name=e.getTitle(),
        vote_message=e.getMessage(),
        vote_places=e.getPlaces(),
        vote_state=e.getState(),
        vote_position=e.getPosition(),
        vote_id=id,
        vote_candidate=e.getCandidates(),
        election_start_date=e.getRelativeTime(0))

@app.route('/<int:id>/texts')
def texts(id):
    if not Election.exists(id):
        abort(404)
    e = Election(id)
    e.updateByTime()
    cuser = muser.getCurrentUser()
    if not cuser.isDev():
        abort(404)
    return render_template(
        "election-forum-templates.html",
        title=u"Textvorschläge: " + e.getTitle(),
        thispage="elections", e=e, Nomination=Nomination)

@app.route('/<int:id>/get-ballot-data/<filename>', methods=["GET", "POST"])
def get_ballot_data(id, filename=None):
    cuser = muser.getCurrentUser()
    if not cuser.isDev():
        abort(404)
    if not Election.exists(id):
        abort(404)
    e = Election(id)
    name = e.getTitle()
    candidates = e.getCandidates()
    places = e.getPlaces()
    ballots = e.tallyVotes()
    print(ballots)

    candidate_assoc = {}
    i=1
    for candidate in candidates:
        candidate_assoc[candidate.id] = [i, candidate]
        i+=1

    header = "%i %i" % (len(candidates), places)
    main = []
    for b in ballots:
        main.append(" ".join(map(str, b)) + " 0")


    cl = []
    items = sorted(candidate_assoc.values(), key=lambda x:x[0])
    for i in items:
        c = i[1].getCandidate()
        cl.append('"' + c.getDetail('name') + '.' + str(c.id) + '@pilearn.de"')

    file = header +"\n"+ ("\n".join(main)) + "\n0\n" + ("\n".join(cl)) + "\n" + '"'+name+'"'
    return Response(file, mimetype='text/blt')

@app.route('/<int:id>/add-nomination', methods=["GET", "POST"])
def candidate(id):
    if not Election.exists(id):
        abort(404)
    e = Election(id)
    e.updateByTime()
    cuser = muser.getCurrentUser()
    if request.method == "POST":
        if not Nomination.exists(id, cuser):
            if cuser.getReputation() >= e.getMinCandRep():
                Nomination.new(id, cuser, request.form["message"])
        else:
            nom = Nomination.from_user(id, cuser)
            nom.setDetail("message", request.form["message"])
        return redirect(url_for("vote", id=id))
    else:
        pretext = ""
        if Nomination.exists(id, cuser):
            pretext = Nomination.from_user(id, cuser).getDetail("message")
        return render_template("add-nomination.html", vote_name=e.getTitle(), vote_id=id, title=e.getTitle() + u" - Kandidatur bearbeiten", pretext=pretext, candminrep=e.getMinCandRep())

@app.route('/<int:id>/api', methods=["POST"])
def api(id):
    if not Election.exists(id):
        abort(404)
    e = Election(id)
    e.updateByTime()
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
        date = command["election_start_date"]
        date = datetime.datetime.strptime(command["election_start_date"], "%Y-%m-%d")
        date = time.mktime(date.timetuple())
        e.setDetail("election_start_date", date)
    elif action == "vote":
        v = Vote.from_user(e.id, cuser)
        if v == None:
            v = Vote.new(e.id, cuser)
        if command["vote"] == 1:
            v.setFirstVote(command["candidate"])
        elif command["vote"] == 3:
            v.setThirdVote(command["candidate"])
        else:
            v.setSecondVote(command["candidate"])
    elif action == "tally" and cuser.isDev():
        if command["results"] == "":
            ids = []
        else:
            ids = command["results"].split(",")
            ids = [s.strip()[:-len("@pilearn.de")] for s in ids]
            ids = [s.split(".")[1] for s in ids]
            ids = map(int, ids)
        cand = e.getCandidates()
        for c in cand:
            if c.getDetail("state") == 1:
                c.setDetail("state", 0)
            if c.getCandidate().id in ids:
                c.setDetail("state", 1)
    elif action == "untally" and cuser.isDev():
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
