# coding: utf-8
from flask import Blueprint, request, session, redirect, url_for, abort, render_template, jsonify, g

from flask_babel import _

import time

teach = Blueprint('teach', __name__)

@teach.route("/")
def index():
    return render_template("teach/index.html", title=_(u"Über Teach"), thispage="teach")

@teach.route("/try", methods=["GET", "POST"])
@teach.route("/create", methods=["GET", "POST"])
def guided_creation():
    TIMEOUT = 3600

    if session.get("teach-creation-last_activity", 0) + TIMEOUT < time.time() or request.values.has_key("start-from-beginning"):
        if session.has_key("teach-creation-step"):
            del session["teach-creation-step"]

    session["teach-creation-last_activity"] = time.time()
    if not session.has_key("teach-creation-step"):
        if request.method == "POST":
            name = request.form.get("group_name")

            session["teach-creation--name"] = name

            session["teach-creation-step"] = 2

            return redirect(url_for("teach.guided_creation"))
        else:
            return render_template("teach/create.html", title=_(u"Neue Lerngruppe erstellen"), thispage="teach", step=1)

    elif session.get("teach-creation-step") == 2:
        if request.method == "POST":
            org_name = request.form.get("org_name")
            org_rep_name = request.form.get("org_rep_name")
            org_email = request.form.get("org_email")

            session["teach-creation--org_name"] = org_name
            session["teach-creation--org_rep_name"] = org_rep_name
            session["teach-creation--org_email"] = org_email

            session["teach-creation-step"] = 3

            return redirect(url_for("teach.guided_creation"))
        else:
            return render_template("teach/create.html", title=_(u"Neue Lerngruppe erstellen"), thispage="teach", step=2)

    elif session.get("teach-creation-step") == 3:
        return render_template("teach/create.html", title=_(u"Neue Lerngruppe erstellen"), thispage="teach", step=3)

    abort(500)
