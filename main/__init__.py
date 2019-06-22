# coding: utf-8

from flask import Flask, request, session, redirect, url_for, abort, render_template, g, make_response

import secrets, random

from controller import md, num as cnum
from model import privileges as mprivileges, tags as mtags, user as muser, forum as mforum, proposal as mproposal, courses as mcourses, reviews as mreviews, post_templates as mpost_templates
from view import auth as vauth, user as vuser, review as vreview, help as vhelp, courses as vcourses, forum as vforum, jsonapi as vjsonapi, survey as vsurvey, proposal as vproposal, tools as vtools, dialog as vdialog, modmsg as vmodmsg, helpdesk as vhelpdesk, upload, topbar as vtopbar, badges as vbadges, announcements as vannouncements

from sha1 import md5

import traceback as tb

import sqlite3 as lite
import re, json, time

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

app = Flask(__name__)

app.config.update(dict(
    SECRET_KEY='S6b9ySuzI2Uv55aY3To8',
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024
))
md.md_apply(app)
f = open("pidata.json", "r")
pidata = json.loads(f.read())
f.close()
GLOBAL_NOTIFICATION = pidata["global_note"]#### Private Beta\n\n&pi;-Learn ist gerade in der privaten Beta. Nur ausgewählte Benutzer dürfen diese Seite benutzen.\n\n----\n\nWir bieten bald auch eine öffentliche Beta an."

IS_OFFLINE = pidata["is_offline"]
OFFLINE_NOTE = pidata["offline_note"]
IN_BETA = pidata["in_beta"]
SITE_LABEL = pidata["label"]
BETA_TOKEN = pidata["beta_token"]
BETA_AUTH_KEY = pidata["register_key"]
HAS_MATHJAX = pidata["mathjax"]
SENTRY_ERROR_LOGGING = pidata["sentry_error_logging"]
if SENTRY_ERROR_LOGGING:
    sentry_sdk.init(
        dsn=pidata["sentry_logging_key"],
        integrations=[FlaskIntegration()]
    )

f = open("version.json", "r")
pivers = json.loads(f.read())
f.close()
__version__ = pivers["main"]

@app.context_processor
def prepare_template_context():
    user = muser.getCurrentUser()

    notifications = user.getNotifications()

    g.random_number = random.randint
    g.num2suff = cnum.num2suff


    if SENTRY_ERROR_LOGGING:
        with sentry_sdk.configure_scope() as scope:
            scope.user = {
                "id": user.id,
                "username": user.getHTMLName(False)
            }

    return {
        "user": user,
        "review": mreviews,
        "user_messages": notifications,
        "privileges": mprivileges,
        "global_notification": GLOBAL_NOTIFICATION,
        "in_beta": IN_BETA,
        "is_offline": IS_OFFLINE,
        "site_label": SITE_LABEL,
        "__version__": __version__,
        "cssid": md5(__version__),
        "num2suff": cnum.num2suff,
        "has_mathjax": HAS_MATHJAX,
        "needs_mathjax": False
    }

@app.before_request
def prepare_request():
    user = muser.getCurrentUser()

    def countNotifications(notif):
        count = 0
        for n in notif:
            count += 1 if (n["visibility"] == 2) else 0
        return count

    g.countNotifications = countNotifications

    if IS_OFFLINE and request.values.get("beta_auth") == BETA_TOKEN or request.values.get("beta_key")==BETA_AUTH_KEY:
        resp = redirect(url_for("index"))
        resp.set_cookie("pi-beta-auth-token", BETA_TOKEN)
        return resp
    elif IS_OFFLINE and not request.cookies.get("pi-beta-auth-token") == BETA_TOKEN and not request.path.startswith("/static"):
        abort(503)

    if not user.isLoggedIn():
        return
    if user.isDeleted():
        session.pop('login', None)
        return redirect(url_for("index"))
    elif user.isDisabled():
        uid = user.id
        session.pop('login', None)
        session["former_login"]=uid
        return redirect(url_for("youarebanned"))

@app.route("/")
def index():
    return render_template('index.html', title="Startseite", thispage="index", globalForum=mforum.Forum.from_id(0), topics=mcourses.Topic, _proposal=mproposal.Proposal, courses=mcourses.Courses)

@app.route("/hide-hero", methods=["POST"])
def hide_hero():
    resp = make_response("{ok}")
    resp.set_cookie("hide-hero-"+request.json["hero"], "yes", time.time()+100000)
    return resp


@app.route("/~dev/sql", methods=['POST'])
def __dev_sql():
    cuser = muser.getCurrentUser()
    if not cuser.isDev():
        abort(404)

    if request.json["file"] in ["courses.db", "user.db", "forum.db", "election.db", "helpdesk.db", "survey.db", "helpcenter.db"] and request.json["sql"] != "":
        file = request.json["file"]
        sql = request.json["sql"]

        try:
            con = lite.connect('databases/'+file)
            cur = con.cursor()
            cur.execute(sql)
            lr = cur.fetchall()
            con.commit()
        except lite.Error as e:
            lr = [["Fehler:", str(e)]]
        except lite.Warning as e:
            lr = [["Achtung:", str(e)]]
    else:
        lr = [["Info", "Keine Abfrage gestartet"]]
        file = sql = ""

    return json.dumps(lr)

@app.route("/~dev/global-note", methods=['POST'])
def __dev_globnote():
    global GLOBAL_NOTIFICATION
    cuser = muser.getCurrentUser()
    if not cuser.isDev():
        abort(404)

    note = request.json["md"]
    GLOBAL_NOTIFICATION = note
    f = open("pidata.json", "r")
    pidata = json.loads(f.read())
    pidata["global_note"] = GLOBAL_NOTIFICATION
    f.close()
    f = open("pidata.json", "w")
    f.write(json.dumps(pidata))
    f.close()
    return ""

@app.route("/~dev/offline-note", methods=['POST'])
def __dev_offnote():
    global OFFLINE_NOTE
    cuser = muser.getCurrentUser()
    if not cuser.isDev():
        abort(404)

    note = request.json["md"]
    OFFLINE_NOTE = note
    f = open("pidata.json", "r")
    pidata = json.loads(f.read())
    pidata["offline_note"] = OFFLINE_NOTE
    f.close()
    f = open("pidata.json", "w")
    f.write(json.dumps(pidata))
    f.close()
    return ""

@app.route("/~dev/offline", methods=['POST'])
def __dev_offline():
    global IS_OFFLINE
    cuser = muser.getCurrentUser()
    if not cuser.isDev():
        abort(404)

    IS_OFFLINE = not IS_OFFLINE
    f = open("pidata.json", "r")
    pidata = json.loads(f.read())
    pidata["is_offline"] = IS_OFFLINE
    f.close()
    f = open("pidata.json", "w")
    f.write(json.dumps(pidata))
    f.close()
    return json.dumps(IS_OFFLINE)

@app.route("/~dev/beta", methods=['POST'])
def __dev_beta():
    global IN_BETA
    cuser = muser.getCurrentUser()
    if not cuser.isDev():
        abort(404)

    IN_BETA = not IN_BETA

    f = open("pidata.json", "r")
    pidata = json.loads(f.read())
    pidata["in_beta"] = IN_BETA
    f.close()
    f = open("pidata.json", "w")
    f.write(json.dumps(pidata))
    f.close()
    return json.dumps(IN_BETA)

@app.route("/~dev/new-beta-token", methods=['POST'])
def __dev_beta_token_new():
    global BETA_TOKEN
    cuser = muser.getCurrentUser()
    if not cuser.isDev():
        abort(404)

    tok = md5(str(time.time()))
    tok = "-".join(["".join(tok[i::5]) for i in range(4)])
    BETA_TOKEN = tok

    f = open("pidata.json", "r")
    pidata = json.loads(f.read())
    pidata["beta_token"] = BETA_TOKEN
    f.close()
    f = open("pidata.json", "w")
    f.write(json.dumps(pidata))
    f.close()
    return BETA_TOKEN

@app.route("/~dev/mockup/<x>")
def __devmockup(x):
    cuser = muser.getCurrentUser()
    if not cuser.isDev():
        abort(404)
    return render_template("mockup/"+x+".html", title="Mockup", thispage="dev")

@app.route("/~dev/error/<int:x>")
def __deverror(x):
    cuser = muser.getCurrentUser()
    if not cuser.isDev():
        abort(404)
    abort(x)

@app.route("/~dev/board")
def __devboard():
    cuser = muser.getCurrentUser()
    if not cuser.isDev():
        abort(404)
    return render_template("~dev/board.html", title="Entwicklerboard", thispage="dev", offline_notification=OFFLINE_NOTE, beta_access_token=BETA_TOKEN, is_offline=IS_OFFLINE)

@app.route("/~dev/answer-revision-management", methods=["GET", "POST"])
def __devanswrevman():
    cuser = muser.getCurrentUser()
    if not cuser.isDev():
        abort(404)
    if request.method == "GET":
        return render_template("~dev/answer-revision-management.html", title="Antwortenversionsverwaltung", thispage="dev")
    else:
        data = request.json
        if data["action"] == "get":
            con = lite.connect('databases/forum.db')
            cur = con.cursor()
            cur.execute("SELECT id, type, editor, new_content, comment FROM answer_revisions WHERE id=?", (data["id"],))
            lr = cur.fetchone()
            con.commit()
            lr = {
                "id": lr[0],
                "type": lr[1],
                "editor": lr[2],
                "content": lr[3],
                "comment": lr[4]
            }
            return json.dumps(lr)
        elif data["action"] == "update":
            con = lite.connect('databases/forum.db')
            cur = con.cursor()
            cur.execute("UPDATE answer_revisions SET type=?, editor=?, new_content=?, comment=? WHERE id=?", (data["data"]["type"], data["data"]["editor"], data["data"]["content"], data["data"]["comment"],data["id"],))
            con.commit()
            return "ok"

@app.route("/~dev/question-revision-management", methods=["GET", "POST"])
def __devquesrevman():
    cuser = muser.getCurrentUser()
    if not cuser.isDev():
        abort(404)
    if request.method == "GET":
        return render_template("~dev/question-revision-management.html", title="Fragenversionsverwaltung", thispage="dev")
    else:
        data = request.json
        if data["action"] == "get":
            con = lite.connect('databases/forum.db')
            cur = con.cursor()
            cur.execute("SELECT id, type, editor, new_content, new_title, new_tags, comment FROM article_revisions WHERE id=?", (data["id"],))
            lr = cur.fetchone()
            con.commit()
            lr = {
                "id": lr[0],
                "type": lr[1],
                "editor": lr[2],
                "content": lr[3],
                "title": lr[4],
                "tags": lr[5],
                "comment": lr[6]
            }
            return json.dumps(lr)
        elif data["action"] == "update":
            con = lite.connect('databases/forum.db')
            cur = con.cursor()
            cur.execute("UPDATE article_revisions SET type=?, editor=?, new_content=?, comment=?, new_title=?, new_tags=? WHERE id=?", (data["data"]["type"], data["data"]["editor"], data["data"]["content"], data["data"]["comment"],data["data"]["title"],data["data"]["tags"],data["id"]))
            con.commit()
            return "ok"

@app.route("/notification/<int:id>")
def notification(id):
    cuser = muser.getCurrentUser()
    not_data = cuser.getNotification(id)
    if not_data is None:
        abort(400)
    else:
        cuser.hideNotification(id)
        link = not_data["link"]
        return redirect(link)

@app.route("/tour")
def tour():
    return render_template("tour/pi-learn.html", title="Tour", topic=mcourses.Topic)

@app.route("/ban-notice")
def youarebanned():
    uid = session.get("former_login", 0)
    if not muser.User.exists(uid):
        abort(404)
    data = muser.User.from_id(uid)
    if not data.isDisabled():
        abort(404)
    print(data.getDetail("ban_reason"))
    return render_template("ban-notification.html", title="Du wurdest gesperrt", data=data, templ=mpost_templates)

vauth.apply(app, pidata)
vuser.apply(app)
vreview.apply(app)
vhelp.apply(app)
vcourses.apply(app)
vforum.apply(app)
vjsonapi.apply(app)
vsurvey.apply(app)
vproposal.apply(app)
vtools.apply(app)
vdialog.apply(app)
vmodmsg.apply(app)
vhelpdesk.apply(app)
upload.apply(app)
vtopbar.apply(app)
vbadges.apply(app)
vannouncements.apply(app)

@app.errorhandler(404)
def error404(x):
    return render_template('error404.html', title="404 Nicht gefunden"), 404

@app.errorhandler(405)
def error405(x):
    return render_template('error405.html', title=u"405 Ungültiger Zugriff"), 405

@app.errorhandler(418)
def error418(x):
    return render_template('error418.html', title=u"418 Der Kaffee ist alle"), 418

@app.errorhandler(403)
def error403(x):
    return render_template('error403.html', title=u"403 Zugriff verboten"), 403

@app.errorhandler(500)
@app.errorhandler(502)
@app.errorhandler(504)
@app.errorhandler(505)
def error500(x):
    data = tb.format_exc()
    data = data.decode("utf-8") # for python 2
    return render_template('error500.html', data=data, title="500 Server-Fehler"), 500

@app.errorhandler(503)
def errorDown(x):
    return render_template('error503.html', title="Webseite im Offlinemodus", message=OFFLINE_NOTE, beta_token=BETA_TOKEN), 503

if __name__ == '__main__':
    DebuggedApplication(app, evalex=True, console_path="/~dev/console", pin_security=False, show_hidden_frames=False)
    run_simple('0.0.0.0', 80, app, use_reloader=True)
#    help(app)
