# coding: utf-8
from flask import Blueprint, request, session, redirect, url_for, abort, render_template, jsonify, g

from flask_babel import _

from model.teach import TeachGroup, TeachMember, TeachInvitations
from model import user as muser
from main.__init__ import db

import datetime, time, random

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
                token = "".join(["abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"[random.randint(0, 61)] for i in range(8)]),
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


@teach.route("/<team>/join/<token>", methods=["GET", "POST"])
def join_the_team(team, token):
    tg = TeachGroup.query.filter(TeachGroup.token == team).filter(TeachGroup.active == True).first_or_404()
    token = TeachInvitations.query.filter(TeachInvitations.token == token).filter(TeachInvitations.group_id == tg.id).first_or_404()

    member = TeachMember.query.filter(TeachMember.group_id == tg.id).filter(TeachMember.user_id == muser.getCurrentUser().id).filter(TeachMember.active == True).first()

    if member:
        return redirect(url_for("teach.dashboard", team=tg.token))

    invalid = None

    if token.expires_after != None and token.expires_after < datetime.datetime.fromtimestamp(time.time()):
        invalid = "expired"
    if token.left_uses_count != None and token.left_uses_count <= 0:
        invalid = "expired"

    if request.method == "POST" and not invalid:
        if token.left_uses_count != None:
            token.left_uses_count -= 1
        new_member = TeachMember(
            user_id = muser.getCurrentUser().id,
            group_id = tg.id,
            shown_name = request.form["shown_name"],
            active = True,
            is_admin = False
        )
        db.session.add(new_member)
        db.session.commit()

        return redirect(url_for("teach.join_complete", team=tg.token))
    else:
        return render_template("teach/team/join.html", title=tg.name, thispage="teach", tg=tg, token=token.token, invalid=invalid)

@teach.route("/<team>/welcome")
def join_complete(team):
    tg = TeachGroup.query.filter(TeachGroup.token == team).filter(TeachGroup.active == True).first_or_404()
    # Access control
    member = TeachMember.query.filter(TeachMember.group_id == tg.id).filter(TeachMember.user_id == muser.getCurrentUser().id).filter(TeachMember.active == True).first_or_404()

    return render_template("teach/team/welcome.html", title=_(u"Neue Lerngruppe erstellt"), thispage="teach", tg=tg)


@teach.route("/<team>/dashboard")
def dashboard(team):
    tg = TeachGroup.query.filter(TeachGroup.token == team).filter(TeachGroup.active == True).first_or_404()
    # Access control
    member = TeachMember.query.filter(TeachMember.group_id == tg.id).filter(TeachMember.user_id == muser.getCurrentUser().id).filter(TeachMember.active == True).first_or_404()

    return render_template("teach/team/dashboard.html", title=tg.name, thispage="teach", tg=tg, member=member)

@teach.route("/<team>/assignments")
def assignments(team):
    tg = TeachGroup.query.filter(TeachGroup.token == team).filter(TeachGroup.active == True).first_or_404()
    # Access control
    member = TeachMember.query.filter(TeachMember.group_id == tg.id).filter(TeachMember.user_id == muser.getCurrentUser().id).filter(TeachMember.active == True).first_or_404()

    return render_template("teach/team/assignments.html", title=tg.name, thispage="teach", tg=tg, member=member)

@teach.route("/<team>/members")
def members(team):
    tg = TeachGroup.query.filter(TeachGroup.token == team).filter(TeachGroup.active == True).first_or_404()
    # Access control
    member = TeachMember.query.filter(TeachMember.group_id == tg.id).filter(TeachMember.user_id == muser.getCurrentUser().id).filter(TeachMember.active == True).filter(TeachMember.is_admin == True).first_or_404()

    members = TeachMember.query.filter(TeachMember.group_id == tg.id).order_by(TeachMember.is_admin, TeachMember.user_id).all()

    return render_template("teach/team/members.html", title=tg.name, thispage="teach", tg=tg, members=members, member=member)

@teach.route("/<team>/members/invitations", methods=["GET", "POST"])
def member_invitations(team):
    tg = TeachGroup.query.filter(TeachGroup.token == team).filter(TeachGroup.active == True).first_or_404()
    # Access control
    member = TeachMember.query.filter(TeachMember.group_id == tg.id).filter(TeachMember.user_id == muser.getCurrentUser().id).filter(TeachMember.active == True).filter(TeachMember.is_admin == True).first_or_404()

    new_code = None

    if request.method == "POST":
        if request.form.get("action", "") == "new":
            expires_after, uses_count = request.form["expires_after"], request.form["uses_count"]

            if len(uses_count) == 0:
                uses_count = None
            else:
                uses_count = int(uses_count)

            if expires_after == "-":
                expires_after = None
            else:
                EXPIRE_LENGTHS = {
                    "1h":      1 * 3600,
                    "2h":      2 * 3600,
                    "1d": 1 * 24 * 3600,
                    "2d": 2 * 24 * 3600,
                    "7d": 7 * 24 * 3600
                }
                expires_after = time.time() + EXPIRE_LENGTHS[expires_after]

                expires_after = datetime.datetime.fromtimestamp(expires_after);

            ti = TeachInvitations(
                token = "".join(["abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"[random.randint(0, 61)] for i in range(50)]),
                group_id = tg.id,
                expires_after = expires_after,
                left_uses_count = uses_count
            )

            new_code = ti.token

            db.session.add(ti)
            db.session.commit()
        elif request.json.get("action", "") == "remove":

            ti = TeachInvitations.query.filter(TeachInvitations.id == request.json["invitation_id"]).first_or_404()

            db.session.delete(ti)
            db.session.commit()

            return jsonify({"result": "success"})

    invitations = TeachInvitations.query.filter(TeachInvitations.group_id == tg.id).all()

    return render_template("teach/team/invitations.html", title=tg.name, thispage="teach", tg=tg, invitations=invitations, member=member, new_code=new_code, now=datetime.datetime.fromtimestamp(time.time()))

@teach.route("/<team>/members/actions", methods=["POST"])
def member_actions(team):
    tg = TeachGroup.query.filter(TeachGroup.token == team).filter(TeachGroup.active == True).first_or_404()
    # Access control + admin
    TeachMember.query.filter(TeachMember.group_id == tg.id).filter(TeachMember.user_id == muser.getCurrentUser().id).filter(TeachMember.active == True).filter(TeachMember.is_admin == True).first_or_404()

    member_id = request.json["member_id"]
    action = request.json["action"]

    # Validate that member is in the group
    member = TeachMember.query.filter(TeachMember.group_id == tg.id).filter(TeachMember.user_id == member_id).first_or_404()

    member_user = muser.User.from_id(member.user_id)

    if action == "remove":
        if not member.active:
            db.session.delete(member)
            db.session.commit()

            return jsonify({"result": "success"})
        else:
            return jsonify({"result": "error", "message": _(u"Zu löschendes Mitglied ist nicht inaktiv.")})

    elif action == "deactivate":
        if member.active:
            member.active = False
            db.session.commit()

            return jsonify({"result": "success"})
        else:
            return jsonify({"result": "error", "message": _(u"Zu deaktivierendes Mitglied ist nicht aktiv.")})

    elif action == "activate":
        if not member.active:
            member.active = True
            db.session.commit()

            return jsonify({"result": "success"})
        else:
            return jsonify({"result": "error", "message": _(u"Zu aktivierendes Mitglied ist nicht inaktiv.")})

    elif action == "grantadmin":
        if member.active and not member.is_admin:
            member.is_admin = True
            db.session.commit()

            return jsonify({"result": "success"})
        else:
            return jsonify({"result": "error", "message": _(u"Zu adminisierendes Mitglied ist nicht aktiv/bereits Admin.")})

    elif action == "revokeadmin":
        if member.active and member.is_admin:
            member.is_admin = False
            db.session.commit()

            return jsonify({"result": "success"})
        else:
            return jsonify({"result": "error", "message": _(u"Zu deadminisierendes Mitglied ist nicht aktiv/Admin.")})

@teach.route("/<team>/admin")
def admin(team):
    tg = TeachGroup.query.filter(TeachGroup.token == team).filter(TeachGroup.active == True).first_or_404()
    # Access controll
    member = TeachMember.query.filter(TeachMember.group_id == tg.id).filter(TeachMember.user_id == muser.getCurrentUser().id).filter(TeachMember.active == True).filter(TeachMember.is_admin == True).first_or_404()

    return render_template("teach/team/admin.html", title=tg.name, thispage="teach", tg=tg, member=member)

@teach.route("/<team>/profile", methods=["GET", "POST"])
def my_profile(team):
    tg = TeachGroup.query.filter(TeachGroup.token == team).filter(TeachGroup.active == True).first_or_404()
    # Access controll
    member = TeachMember.query.filter(TeachMember.group_id == tg.id).filter(TeachMember.user_id == muser.getCurrentUser().id).filter(TeachMember.active == True).first_or_404()

    saved = False
    if request.method == "POST":
        member.shown_name = request.form["shown_name"]
        db.session.commit()
        saved = True

    return render_template("teach/team/profile.html", title=tg.name, thispage="teach", tg=tg, member=member, saved=saved)
