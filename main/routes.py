# coding: utf-8

from model.settings import Settings as S

from model import privileges as mprivileges, tags as mtags, user as muser, forum as mforum, proposal as mproposal, courses as mcourses, reviews as mreviews, post_templates as mpost_templates

if S.get("enable-teaching-teams") == "yes":
    from model.teach import TeachGroup, TeachMember

from view import auth as vauth, user as vuser, review as vreview, help as vhelp, courses as vcourses, forum as vforum, jsonapi as vjsonapi, survey as vsurvey, tools as vtools, dialog as vdialog, modmsg as vmodmsg, helpdesk as vhelpdesk, upload, topbar as vtopbar, badges as vbadges, announcements as vannouncements, pull_requests as vpull_requests, admin as vadmin
import view

import traceback as tb

import sqlite3 as lite
import re, json, time

from flask_babel import _

from flask import request, session, redirect, url_for, abort, render_template, g, make_response

from __init__ import app

@app.route("/")
def index():
    teach_mine=None
    has_teach = S.get("enable-teaching-teams") == "yes"

    if has_teach:
        teach_mine = TeachGroup.query.join(TeachMember).filter(TeachMember.user_id == muser.getCurrentUser().id, TeachMember.active == True, TeachGroup.active == True).all()

    return render_template('index.html', title=_("Startseite"), thispage="index", globalForum=mforum.Forum.from_id(0), topics=mcourses.Topic, _proposal=mproposal.Proposal, courses=mcourses.Courses, has_teach=has_teach, teach_mine=teach_mine)

@app.route("/hide-hero", methods=["POST"])
def hide_hero():
    resp = make_response("{ok}")
    resp.set_cookie("hide-hero-"+request.json["hero"], "yes", time.time()+100000)
    return resp



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
vcourses.apply(app)
vpull_requests.apply(app)
vforum.apply(app)
vjsonapi.apply(app)
vsurvey.apply(app)
vtools.apply(app)
vdialog.apply(app)
vmodmsg.apply(app)
upload.apply(app)

app.register_blueprint(view.about, url_prefix='/about')
app.register_blueprint(view.admin, url_prefix='/admin')
app.register_blueprint(view.announcements, url_prefix='/announcements/<int:forum_id>')
app.register_blueprint(view.badges, url_prefix='/badges')
app.register_blueprint(view.help, url_prefix='/help')
app.register_blueprint(view.helpdesk, url_prefix='/contact')
app.register_blueprint(view.legal, url_prefix='/legal')
app.register_blueprint(view.proposal, url_prefix='/course/proposal')
app.register_blueprint(view.topbar, url_prefix='/topbar')

# Teach should only be loaded, when activated:
if S.get("enable-teaching-teams") == "yes":
    app.register_blueprint(view.teach, url_prefix='/teach')

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
