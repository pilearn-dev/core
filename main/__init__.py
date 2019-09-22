# coding: utf-8

from flask import Flask, request, session, redirect, url_for, abort, render_template, g, make_response

import secrets, random

from model.settings import Settings as S

from controller import md, num as cnum
from model import privileges as mprivileges, tags as mtags, user as muser, forum as mforum, proposal as mproposal, courses as mcourses, reviews as mreviews, post_templates as mpost_templates
from view import auth as vauth, user as vuser, review as vreview, help as vhelp, courses as vcourses, forum as vforum, jsonapi as vjsonapi, survey as vsurvey, proposal as vproposal, tools as vtools, dialog as vdialog, modmsg as vmodmsg, helpdesk as vhelpdesk, upload, topbar as vtopbar, badges as vbadges, announcements as vannouncements, about as vabout, pull_requests as vpull_requests

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

if S.get("logging-errors-sentry-key"):
    sentry_sdk.init(
        dsn=S.get("logging-errors-sentry-key"),
        integrations=[FlaskIntegration()]
    )

f = open("version.json", "r")
pivers = json.loads(f.read())
f.close()
__version__ = pivers["main"]

IS_INACCESSIBLE = False

@app.context_processor
def prepare_template_context():
    user = muser.getCurrentUser()

    notifications = user.getNotifications()

    g.random_number = random.randint
    g.num2suff = cnum.num2suff


    if S.get("logging-errors-sentry-key"):
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
        "is_offline": S.get("access-private") == "1",
        "site_label": S.get("site-label"),
        "site_name": S.get("site-name"),
        "site_short_name": S.get("site-short-name"),
        "__version__": __version__,
        "cssid": md5(__version__),
        "num2suff": cnum.num2suff,
        "has_mathjax": S.get("enable-mathjax") == "1",
        "mathjax_block_delim": S.get("enable-mathjax-tokens-block", "::( )::").split(" "),
        "mathjax_inline_delim": S.get("enable-mathjax-tokens-inline", ":( ):").split(" "),
        "needs_mathjax": False,
        "matomo_site_id": S.get("logging-matomo-id"),
        "featured_announcements": mforum.ForumAnnouncement.byForumFeatured(0)
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

    if IS_INACCESSIBLE and not request.path.startswith("/static"):
        session.pop('login', None)
        return render_template("inaccessible.html"), 503

    if S.get("access-private") == "1":
        token = S.get("access-private-token")
        if token != request.cookies.get("pi-beta-auth-token"):
            if token != request.values.get("beta_key"):
                if not S.get("access-private-allow-password") == "1" or S.get("access-private-allow-password-value") != request.values.get("beta_auth"):
                    abort(503)

            resp = redirect(url_for("index"))
            resp.set_cookie("pi-beta-auth-token", BETA_TOKEN)
            return resp

    if not user.isLoggedIn():
        return
    if user.isDeleted():
        session.pop('login', None)
        return redirect(url_for("index"))

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

    if request.json["file"] in ["pilearn.db", "pilearn.db", "pilearn.db", "pilearn.db", "helpdesk.db", "pilearn.db", "pilearn.db"] and request.json["sql"] != "":
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

@app.route("/~dev/inaccessible", methods=['POST'])
def __dev_inaccessible():
    global IS_INACCESSIBLE
    cuser = muser.getCurrentUser()
    if not cuser.isDev():
        abort(404)

    IS_INACCESSIBLE = not IS_INACCESSIBLE
    return json.dumps(IS_INACCESSIBLE)

@app.route("/~dev/new-beta-token", methods=['POST'])
def __dev_beta_token_new():
    global BETA_TOKEN
    cuser = muser.getCurrentUser()
    if not cuser.isDev():
        abort(404)

    tok = md5(str(time.time()))
    tok = "-".join(["".join(tok[i::5]) for i in range(4)])

    S.set("access-private-token", tok)
    return tok

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
    return render_template("~dev/board.html", title="Entwicklerboard", thispage="dev", offline_notification=S.get("access-private-notice"), beta_access_token=S.get("access-private-token"), is_offline=S.get("access-private") == "1")

@app.route("/notification/<int:id>")
def notification(id):
    cuser = muser.getCurrentUser()
    not_data = cuser.getNotification(id)
    if not_data is None or not_data["user_id"] != cuser.id:
        abort(400)
    else:
        cuser.hideNotification(id)
        link = not_data["link"]
        return redirect(link)

@app.route("/tour")
def tour():
    return render_template("tour/pi-learn.html", title="Tour", topic=mcourses.Topic)

vauth.apply(app)
vuser.apply(app)
vreview.apply(app)
vhelp.apply(app)
vcourses.apply(app)
vpull_requests.apply(app)
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
vabout.apply(app)

@app.route("/404")
@app.errorhandler(404)
def error404(x=None):
    return render_template('error404.html', title="404 Nicht gefunden"), 404

@app.errorhandler(405)
def error405(x=None):
    return render_template('error405.html', title=u"405 Ungültiger Zugriff"), 405

@app.route("/wp-login.php")
@app.route("/backend")
@app.route("/contao")
@app.route("/wp-admin")
@app.errorhandler(418)
def error418(x=None):
    return render_template('error418.html', title=u"418 Der Kaffee ist alle"), 418

@app.route("/forbidden")
@app.errorhandler(403)
def error403(x=None):
    return render_template('error403.html', title=u"403 Zugriff verboten"), 403

@app.route("/error")
@app.errorhandler(500)
@app.errorhandler(502)
@app.errorhandler(504)
@app.errorhandler(505)
def error500(x=None):
    data = tb.format_exc()
    data = data.decode("utf-8") # for python 2
    return render_template('error500.html', data=data, title="500 Server-Fehler"), 500

@app.errorhandler(503)
def errorDown(x):
    return render_template('error503.html', title="Webseite im Offlinemodus", message=S.get("access-private-notice"), beta_token=S.get("access-private-token"), allow_password=S.get("access-allow-password") == "1"), 503

if __name__ == '__main__':
    DebuggedApplication(app, evalex=True, console_path="/~dev/console", pin_security=False, show_hidden_frames=False)
    run_simple('0.0.0.0', 80, app, use_reloader=True)
