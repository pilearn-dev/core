# coding: utf-8

from flask import Flask, request, session, redirect, url_for, abort, render_template, g, make_response

import secrets, random

from .model.settings import Settings as S

from .controller import md, num as cnum
from .model import privileges as mprivileges, tags as mtags, user as muser, forum as mforum, proposal as mproposal, courses as mcourses, reviews as mreviews, post_templates as mpost_templates
from .sha1 import md5

import json

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from flask_babel import Babel, _

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

f = open("pidata.json", "r")
pidata = json.loads(f.read())
f.close()

app.config.update(dict(
    SECRET_KEY = 'S6b9ySuzI2Uv55aY3To8',
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024,
    BABEL_TRANSLATION_DIRECTORIES = '../translations',
    SQLALCHEMY_DATABASE_URI = pidata["db_host"],
    SQLALCHEMY_TRACK_MODIFICATIONS = False
))
md.md_apply(app)
babel = Babel(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

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

    g.site_name = S.get("site-name")
    g.site_short_name = S.get("site-short-name")

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
        "matomo_site_url": S.get("logging-matomo-url"),
        "featured_announcements": mforum.ForumAnnouncement.byForumFeatured(0),
        "language": S.get("site-language", "de"),
        "limit_course_creation": S.get("limit-course-creation")=="yes"
    }

@babel.localeselector
def babel_select_language():
    lang = S.get("site-language", "de")
    return lang

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

    if S.get("access-private") == "1" and not request.path.startswith("/static/"):
        token = S.get("access-private-token")
        if token != request.cookies.get("pi-beta-auth-token"):
            if token != request.values.get("beta_access_token"):
                if S.get("access-allow-password") != "1" or S.get("access-allow-password-value") != request.values.get("beta_key"):
                    abort(503)

            resp = redirect(request.path)
            resp.set_cookie("pi-beta-auth-token", token)
            return resp

    if request.values.get("global_identity_verification", "") != "" or request.form.get("global_identity_verification", "") != "":
        return "Request rejected for reasons of moderation.", 400

    if not user.isLoggedIn():
        return
    if user.isDeleted():
        session.pop('login', None)
        return redirect(url_for("index"))

from .routes import *

if __name__ == '__main__':
    DebuggedApplication(app, evalex=True, console_path="/~dev/console", pin_security=False, show_hidden_frames=False)
    run_simple('0.0.0.0', 80, app, use_reloader=True)
