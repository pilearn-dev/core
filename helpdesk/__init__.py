# coding: utf-8

from flask import Flask, request, session, redirect, url_for, abort, render_template, g

import secrets, random

from main.controller import md, times as ctimes, num as cnum
from main.model import privileges as mprivileges, tags as mtags, user as muser, reviews as mreviews
from model import Ticket, Response
import traceback as tb, json
import time

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
__version__ = pivers["helpdesk"]

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
        return redirect("/help/redirected/helpdesk")

@app.route('/')
def index():
    cuser = muser.getCurrentUser()
    if not cuser.isDev():
        return redirect(url_for("mine"))
    return redirect(url_for("list_"))

@app.route('/ticket/list')
def list_():
    cuser = muser.getCurrentUser()
    if not cuser.isDev():
        abort(404)
    return render_template("list.html", title=u"Tickets (alle)", thispage="list", data=Ticket.getAll())

@app.route('/ticket/mine')
def mine():
    cuser = muser.getCurrentUser()
    return render_template("list.html", title=u"Tickets (eigene)", thispage="ticket", data=Ticket.getByUser(cuser))

@app.route('/ticket/new', methods=["GET", "POST"])
def new():
    if request.method == "GET":
        return render_template("new.html", title=u"Neues Ticket", thispage="new")
    else:
        data = request.json
        cuser = muser.getCurrentUser()
        if cuser.isAdmin():
            if cuser.isDev():
                if not data["action"] in ["support", "dsgvo", "other", "pm", "ping", "legal"]:
                    return "Ungültiger Ticket-Typ"
            else:
                if not data["action"] in ["support", "dsgvo", "other", "pm"]:
                    return "Ungültiger Ticket-Typ"
        else:
            if not data["action"] in ["support", "dsgvo", "other"]:
                return "Ungültiger Ticket-Typ"
        t = Ticket.new(data["title"], data["action"])
        i = Response.new(t.id, data["message"], t.isDisciplinary(), cuser.id)
        if data["action"] == "pm":
            xu = muser.User.from_id(data["user_id"])
            t.addViewer(xu)
            xu.notify("pm", "Ein Administrator hat dich kontaktiert. Bitte beachte seine Nachricht", "/helpdesk/ticket/"+str(t.id))
            t.setDetail("assoc", cuser.id)
            t.setDetail("department", "&pi;-Learn Administratoren-Team")
        elif data["action"] == "ping":
            if data["group"] == "mod":
                xus = muser.User.getByRole("m")
            elif data["group"] == "admin":
                xus = muser.User.getByRole("a")
            elif data["group"] == "both":
                xus = muser.User.getByRole("m") + muser.User.getByRole("a")
            for xu in xus:
                t.addViewer(xu)
                xu.notify("ping", "Ein Entwickler bittet dich, diesen PING anzuschauen: " + data["title"], "/helpdesk/ticket/"+str(t.id))

            t.setDetail("assoc", cuser.id)
            t.setDetail("department", "&pi;-Learn Team")
        elif data["action"] == "legal":
            t.setDetail("assoc", cuser.id)
            t.setDetail("department", "&pi;-Learn Team")
        else:
            t.addViewer(cuser)
            t.setDetail("department", "&pi;-Learn Team")
        t.setDetail("last_response_id", i)
        return str(t.id)

@app.route('/ticket/<int:id>')
def ticket(id):
    if not Ticket.exists(id):
        abort(404)
    t = Ticket(id)
    cuser = muser.getCurrentUser()
    if not (t.isDisciplinary() and cuser.isAdmin()) and not cuser.isDev() and not t.isViewer(cuser):
        abort(404)
    resp = viewer = None
    if t.isLegal():
        resp = Response.get_by_user(cuser, t.id)
        viewer = list(map(muser.User.from_id, t.getViewer()))
    return render_template("ticket.html", title=u"Ticket", thispage="ticket", data=t, responses=t.getHistory(), resp=resp, viewer=viewer)

@app.route('/api/<int:id>', methods=["POST"])
def api(id):
    if not Ticket.exists(id):
        abort(404)
    t = Ticket(id)
    cuser = muser.getCurrentUser()
    command = request.json
    if not command.get("action", False):
        return ""
    action = command["action"]
    if action == "open":
        if (t.isDisciplinary() and cuser.isAdmin() or cuser.isDev()):
            t.setDetail("closed", 0)
    elif action == "close":
        if (t.isDisciplinary() and cuser.isAdmin() or cuser.isDev()):
            t.setDetail("closed", 1)
    elif action == "repro":
        if (t.isDisciplinary() and cuser.isAdmin() or cuser.isDev()):
            t.setDetail("repro", 1)
    elif action == "norepro":
        if (t.isDisciplinary() and cuser.isAdmin() or cuser.isDev()):
            t.setDetail("repro", -1)
    elif action == "defer":
        if (t.isDisciplinary() and cuser.isAdmin() or cuser.isDev()):
            t.setDetail("deferred", 1)
    elif action == "undefer":
        if (t.isDisciplinary() and cuser.isAdmin() or cuser.isDev()):
            t.setDetail("deferred", 0)
    elif action == "assoc":
        if (t.isDisciplinary() and cuser.isAdmin() or cuser.isDev()):
            t.setDetail("assoc", command["userid"])
    elif action == "department":
        if (t.isDisciplinary() and cuser.isAdmin() or cuser.isDev()):
            t.setDetail("department", command["department"])
    elif action == "add-viewer":
        if (t.isDisciplinary() and cuser.isAdmin() or cuser.isDev()):
            xu =muser.User.from_id(command["userid"])
            t.addViewer(xu)
            xu.notify("helpdesk", "Bitte nehmen Sie an der Bearbeitung des Helpdesk-Tickets \"" + t.getTitle() + "\" teil.", "/helpdesk/ticket/"+str(t.id))
    elif action == "answer":
        if not t.isLegal():
            i = Response.new(t.id, command["answer"], t.isDisciplinary() and cuser.isAdmin() or cuser.isDev(), cuser.id)
            t.setDetail("last_response_id", i)
            viewer = t.getViewer()
            for v in viewer:
                if v != cuser.id:
                    muser.User.from_id(v).notify("helpdesk", "Es gibt eine neue Antwort auf den Support-Beitrag " + t.getTitle(), "/helpdesk/ticket/"+str(t.id))
        else:
            resp = Response.get_by_user(cuser, t.id)
            if resp is not None:
                return ""
            if command["answer"] == "accept":
                i = Response.new(t.id, "["+cuser.getDetail("realname") + "](/u/"+str(cuser.id)+") hat diese Vereinbarung am " + ctimes.stamp2german(time.time()) + " **akzeptiert**.", False, cuser.id)
                t.getAssoc().notify("helpdesk", cuser.getDetail("realname") + " hat die Vereinbarung akzeptiert: " + t.getTitle(), "/helpdesk/ticket/"+str(t.id))
            else:
                i = Response.new(t.id, "["+cuser.getDetail("realname") + "](/u/"+str(cuser.id)+") hat diese Vereinbarung am " + ctimes.stamp2german(time.time()) + " **abgelehnt**.", False, cuser.id)
                t.getAssoc().notify("helpdesk", cuser.getDetail("realname") + " hat die Vereinbarung abgelehnt: " + t.getTitle(), "/helpdesk/ticket/"+str(t.id))
            t.setDetail("last_response_id", i)
    return ""

@app.errorhandler(404)
def error404(x):
    return render_template('error404.html', title="404 Nicht gefunden"), 404

@app.errorhandler(500)
def error500(x):
    data = tb.format_exc()
    data = data.decode("utf-8")
    return render_template('error500.html', data=data, title="500 Server-Fehler"), 500
