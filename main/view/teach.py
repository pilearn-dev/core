# coding: utf-8
from flask import Blueprint, request, session, redirect, url_for, abort, render_template, jsonify, g

from flask_babel import _

from model.teach import TeachGroup
from main.__init__ import db

import time, random

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
        if request.method == "POST":
            tg = TeachGroup(
                token = "".join(["abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"[random.randint(0, 62)] for i in range(8)]),
                name = session["teach-creation--name"],
                org_name = session["teach-creation--org_name"],
                org_rep_name = session["teach-creation--org_rep_name"],
                org_email = session["teach-creation--org_email"],
                active = True,
                is_demo = True
            )

            db.session.add(tg)
            db.session.commit()

            del session["teach-creation-step"]

            return redirect(url_for("teach.creation_complete", team=tg.token))
        else:
            return render_template("teach/create.html", title=_(u"Neue Lerngruppe erstellen"), thispage="teach", step=3)

    abort(500)


@teach.route("/welcome/<team>")
def creation_complete(team):
    tg = TeachGroup.query.filter(TeachGroup.token == team).filter(TeachGroup.active == True).first_or_404()
    return render_template("teach/welcome.html", title=_(u"Neue Lerngruppe erstellt"), thispage="teach", tg=tg)

@teach.route("/<team>/dashboard")
def dashboard(team):
    tg = TeachGroup.query.filter(TeachGroup.token == team).filter(TeachGroup.active == True).first_or_404()
    return render_template("teach/team/dashboard.html", title=tg.name, thispage="teach", tg=tg)

@teach.route("/<team>/assignments")
def assignments(team):
    tg = TeachGroup.query.filter(TeachGroup.token == team).filter(TeachGroup.active == True).first_or_404()
    return render_template("teach/team/assignments.html", title=tg.name, thispage="teach", tg=tg)

@teach.route("/<team>/members")
def members(team):
    tg = TeachGroup.query.filter(TeachGroup.token == team).filter(TeachGroup.active == True).first_or_404()
    return render_template("teach/team/members.html", title=tg.name, thispage="teach", tg=tg)

@teach.route("/<team>/admin")
def admin(team):
    tg = TeachGroup.query.filter(TeachGroup.token == team).filter(TeachGroup.active == True).first_or_404()
    return render_template("teach/team/admin.html", title=tg.name, thispage="teach", tg=tg)
