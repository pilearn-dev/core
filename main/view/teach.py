# coding: utf-8
from flask import Blueprint, request, session, redirect, url_for, abort, render_template, jsonify, g

from flask_babel import _

from model.teach import TeachGroup, TeachMember, TeachInvitations, TeachAssignments, TeachAssignmentTypes, TeachAssignmentCompletions
from model import user as muser, courses as mcourses
from main.__init__ import db

import datetime, time, random

teach = Blueprint('teach', __name__)

@teach.route("/")
def index():
    return render_template("teach/index.html", title=_("Über Teach"), thispage="teach")

@teach.route("/try", methods=["GET", "POST"])
@teach.route("/create", methods=["GET", "POST"])
def guided_creation():
    TIMEOUT = 3600

    if session.get("teach-creation-last_activity", 0) + TIMEOUT < time.time() or "start-from-beginning" in request.values:
        if "teach-creation-step" in session:
            del session["teach-creation-step"]

    session["teach-creation-last_activity"] = time.time()
    if "teach-creation-step" not in session:
        if request.method == "POST":
            name = request.form.get("group_name")

            session["teach-creation--name"] = name

            session["teach-creation-step"] = 2

            return redirect(url_for("teach.guided_creation"))
        else:
            return render_template("teach/create.html", title=_("Neue Lerngruppe erstellen"), thispage="teach", step=1)

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
            return render_template("teach/create.html", title=_("Neue Lerngruppe erstellen"), thispage="teach", step=2)

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

            cuser = muser.getCurrentUser()

            new_member = TeachMember(
                user_id = cuser.id,
                group_id = tg.id,
                shown_name = cuser.getDetail("realname"),
                active = True,
                is_admin = True
            )
            
            db.session.add(new_member)
            
            db.session.commit()

            del session["teach-creation-step"]

            return redirect(url_for("teach.creation_complete", team=tg.token))
        else:
            return render_template("teach/create.html", title=_("Neue Lerngruppe erstellen"), thispage="teach", step=3)

    abort(500)


@teach.route("/welcome/<team>")
def creation_complete(team):
    tg = TeachGroup.query.filter(TeachGroup.token == team).filter(TeachGroup.active == True).first_or_404()
    return render_template("teach/welcome.html", title=_("Neue Lerngruppe erstellt"), thispage="teach", tg=tg)


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
    tg, member, cuser = team_access_control(team, muser.getCurrentUser())

    return render_template("teach/team/welcome.html", title=_("Neue Lerngruppe erstellt"), thispage="teach", tg=tg)


@teach.route("/<team>/dashboard")
def dashboard(team):
    tg, member, cuser = team_access_control(team, muser.getCurrentUser())

    return render_template("teach/team/dashboard.html", title=tg.name, thispage="teach", tg=tg, member=member)

@teach.route("/<team>/assignments")
def assignments(team):
    tg, member, cuser = team_access_control(team, muser.getCurrentUser())

    assignments = TeachAssignments.query.filter(TeachAssignments.team_id == tg.id, TeachAssignments.active).all()

    excluded_items = []
    own_assignment_completions = TeachAssignmentCompletions.query.filter(TeachAssignmentCompletions.team_id == tg.id, TeachAssignmentCompletions.user_id == cuser.id)

    excluded_items += [item.assignment_id for item in own_assignment_completions]


    for item in assignments:
        if item.id in excluded_items:
            assignments.remove(item)


    return render_template("teach/team/assignments.html", title=tg.name, thispage="teach", tg=tg, member=member, assignments=assignments, course_maker=mcourses.Courses.__init__, TeachAssignmentTypes=TeachAssignmentTypes)

@teach.route("/<team>/assignments/<assignment>", methods=["GET", "POST"])
def assignment_complete(team, assignment):
    tg, member, cuser = team_access_control(team, muser.getCurrentUser())

    assignment = TeachAssignments.query.filter(TeachAssignments.team_id == tg.id, TeachAssignments.active, TeachAssignments.token == assignment).first_or_404()

    if request.method == "POST":
        if assignment.type == TeachAssignmentTypes.CLICK_TO_RESOLVE:
            ac = TeachAssignmentCompletions(
                team_id = tg.id,
                assignment_id = assignment.id,
                user_id = cuser.id,
                token = "".join(["abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"[random.randint(0, 61)] for i in range(16)])
            )
            ac.submission_at = datetime.datetime.now()
            ac.is_submission_late = (assignment.to_be_completed_before is not None and ac.submission_at > assignment.to_be_completed_before)
            ac.points_for_submission = assignment.max_points_for_completion

            db.session.add(ac)
            db.session.commit()
            return redirect(url_for("teach.assignments", team=tg.token))

    return render_template("teach/team/assignment_single.html", title=tg.name, thispage="teach", tg=tg, member=member, assignment=assignment, course_maker=mcourses.Courses.__init__, TeachAssignmentTypes=TeachAssignmentTypes)

@teach.route("/<team>/assignments/<assignment>/grade")
def assignment_grade(team, assignment):
    abort(404)

@teach.route("/<team>/assignments/<assignment>/edit")
def assignment_edit(team, assignment):
    abort(404)

@teach.route("/<team>/members")
def members(team):
    tg, member, cuser = team_access_control(team, muser.getCurrentUser(), True)

    members = TeachMember.query.filter(TeachMember.group_id == tg.id).order_by(TeachMember.is_admin, TeachMember.user_id).all()

    return render_template("teach/team/members.html", title=tg.name, thispage="teach", tg=tg, members=members, member=member)

@teach.route("/<team>/members/invitations", methods=["GET", "POST"])
def member_invitations(team):
    tg, member, cuser = team_access_control(team, muser.getCurrentUser(), True)

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
    tg, member, cuser = team_access_control(team, muser.getCurrentUser(), True)

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
            return jsonify({"result": "error", "message": _("Zu löschendes Mitglied ist nicht inaktiv.")})

    elif action == "deactivate":
        if member.active:
            member.active = False
            db.session.commit()

            return jsonify({"result": "success"})
        else:
            return jsonify({"result": "error", "message": _("Zu deaktivierendes Mitglied ist nicht aktiv.")})

    elif action == "activate":
        if not member.active:
            member.active = True
            db.session.commit()

            return jsonify({"result": "success"})
        else:
            return jsonify({"result": "error", "message": _("Zu aktivierendes Mitglied ist nicht inaktiv.")})

    elif action == "grantadmin":
        if member.active and not member.is_admin:
            member.is_admin = True
            db.session.commit()

            return jsonify({"result": "success"})
        else:
            return jsonify({"result": "error", "message": _("Zu adminisierendes Mitglied ist nicht aktiv/bereits Admin.")})

    elif action == "revokeadmin":
        if member.active and member.is_admin:
            member.is_admin = False
            db.session.commit()

            return jsonify({"result": "success"})
        else:
            return jsonify({"result": "error", "message": _("Zu deadminisierendes Mitglied ist nicht aktiv/Admin.")})

@teach.route("/<team>/admin", methods=["GET", "POST"])
def admin(team):
    tg, member, cuser = team_access_control(team, muser.getCurrentUser(), True)

    saved = False
    if request.method == "POST":
        tg.name = request.form["name"]
        tg.org_name = request.form["org_name"]
        tg.org_rep_name = request.form["org_rep_name"]
        tg.org_email = request.form["org_email"]
        db.session.commit()
        saved = True

    return render_template("teach/team/admin.html", title=tg.name, thispage="teach", tg=tg, member=member, saved=saved)

@teach.route("/<team>/profile", methods=["GET", "POST"])
def my_profile(team):
    tg, member, cuser = team_access_control(team, muser.getCurrentUser())

    saved = False
    if request.method == "POST":
        member.shown_name = request.form["shown_name"]
        db.session.commit()
        saved = True

    return render_template("teach/team/profile.html", title=tg.name, thispage="teach", tg=tg, member=member, saved=saved)



# Helper functions

def team_access_control(team_token, current_user, requires_admin=False):
    """
        HELPER team_access_control (string team_token, model.User current_user, boolean requires_admin[default=False]) -> db[teach_group], db[teach_member], model.User current_user

        Takes the team token and current user object and returns db objects for teach group and teach membership and the passed user object if authentication succeeded. Fails with 404 otherwise.

        (Optionally) Also require admin rights in the team for successful validation.

    """
    tg = TeachGroup.query.filter(TeachGroup.token == team_token, TeachGroup.active == True).first_or_404()

    if requires_admin:
        member = TeachMember.query.filter(TeachMember.group_id == tg.id, TeachMember.user_id == current_user.id, TeachMember.active == True, TeachMember.is_admin == True).first_or_404()
    else:
        member = TeachMember.query.filter(TeachMember.group_id == tg.id, TeachMember.user_id == current_user.id, TeachMember.active == True).first_or_404()

    return tg, member, current_user
