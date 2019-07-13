# coding: utf-8
from flask import render_template, redirect, abort, url_for, request, jsonify
from model import privileges as mprivileges, courses as mcourses, user as muser, survey as msurvey, proposal as mproposal, forum as mforum, pull_requests as mpull_requests
from controller import query as cquery
import json, time, base64

def course_branches(id,label=None):
    if not mcourses.Courses.exists(id):
        abort(404)
    course = mcourses.Courses(id)
    cuser = muser.getCurrentUser()
    if course.getLabel() != label and request.method != "POST":
        return redirect(url_for("course_branches", id=id, label=course.getLabel()))
    if not cuser.isLoggedIn() or cuser.isDisabled():
        abort(404)

    existing_branch = mpull_requests.Branch.getByCourseAndUser(course.id, cuser.id)
    if existing_branch:
        return redirect(url_for("course_single_branch", course_id=id, course_label=course.getLabel(), id=existing_branch.id))

    return render_template('courses/pull-requests/branches.html', title=course.getTitle(), thispage="courses", course=course)

def course_create_branch(id,label=None):
    if not mcourses.Courses.exists(id):
        abort(404)
    course = mcourses.Courses(id)
    cuser = muser.getCurrentUser()
    if not cuser.isLoggedIn() or cuser.isDisabled():
        abort(404)

    existing_branch = mpull_requests.Branch.getByCourseAndUser(course.id, cuser.id)
    if existing_branch:
        abort(400)

    mpull_requests.Branch.new(course.id, cuser.id)
    return "okay"

def course_single_branch(id, course_id,course_label=None):
    if not mcourses.Courses.exists(course_id):
        abort(404)
    course = mcourses.Courses(course_id)
    cuser = muser.getCurrentUser()
    if course.getLabel() != course_label and request.method != "POST":
        return redirect(url_for("course_single_branch", id=id, course_id=course_id, course_label=course.getLabel()))
    if not mpull_requests.Branch.exists(id):
        abort(404)
    branch = mpull_requests.Branch(id)

    if not (branch.getDetail("author") == cuser.id or cuser.isMod()) or cuser.isDisabled() or branch.getDetail("course_id") != course.id:
        abort(404)

    return render_template('courses/pull-requests/branch.html', title="Branch #" + str(branch.id) + u" für " + course.getTitle(), thispage="courses", course=course, branch=branch, _encoder=base64.b64encode)

def branch_item(unit_id, override_id, branch_id, course_id,course_label=None):
    if not mcourses.Courses.exists(course_id):
        abort(404)
    course = mcourses.Courses(course_id)
    cuser = muser.getCurrentUser()
    if course.getLabel() != course_label and request.method != "POST":
        return redirect(url_for("branch_item", branch_id=branch_id, course_id=course_id, course_label=course.getLabel(), unit_id=unit_id, override_id=override_id))
    if not mpull_requests.Branch.exists(branch_id):
        abort(404)
    branch = mpull_requests.Branch(branch_id)

    if not (branch.getDetail("author") == cuser.id or cuser.isMod()) or cuser.isDisabled() or branch.getDetail("course_id") != course.id:
        abort(404)

    if unit_id == "-":
        data = {
            "title": "",
            "type": "",
            "content": None
        }
    else:
        unit_id = int(unit_id)
        unit = mcourses.Units(unit_id)
        if not unit or unit.getDetail("courseid") != course_id:
            abort(404)

        data = {
            "title": unit.getTitle(),
            "type": unit.getType(),
            "content": unit.getJSON()
        }

    if override_id != "-":
        override_id = int(override_id)
        override = branch.getSingleOverride(override_id)
        if override[2] != unit_id: abort(404)
        data["title"] = override["title"]
        if not data["type"]:
            data["type"] = override["type"]
        data["content"] = json.loads(override["content"])

    return render_template('courses/pull-requests/item/' + data["type"] + '.html', title="Branch #" + str(branch.id) + u" für " + course.getTitle(), thispage="courses", course=course, branch=branch, _encoder=base64.b64encode, data=data, unit_id=unit_id, override_id=override_id)

def branch_update_item(unit_id, override_id, branch_id, course_id,course_label=None):
    if not mcourses.Courses.exists(course_id):
        abort(404)
    course = mcourses.Courses(course_id)
    cuser = muser.getCurrentUser()
    if course.getLabel() != course_label and request.method != "POST":
        return redirect(url_for("branch_item", branch_id=branch_id, course_id=course_id, course_label=course.getLabel(), unit_id=unit_id, override_id=override_id))
    if not mpull_requests.Branch.exists(branch_id):
        abort(404)
    branch = mpull_requests.Branch(branch_id)

    if not (branch.getDetail("author") == cuser.id or cuser.isMod()) or cuser.isDisabled() or branch.getDetail("course_id") != course.id:
        abort(404)

    if unit_id == "-":
        data = {
            "title": "",
            "type": "",
            "content": None,
            "parent_unit": 0,
            "parent_override": 0,
            "unit_order": 0
        }
    else:
        unit_id = int(unit_id)
        unit = mcourses.Units(unit_id)
        if not unit or unit.getDetail("courseid") != course_id:
            abort(404)

        data = {
            "title": unit.getTitle(),
            "type": unit.getType(),
            "content": unit.getJSON(),
            "parent_unit": unit.getDetail("parent"),
            "parent_override": 0,
            "unit_order": unit.getDetail("unit_order")
        }

    if override_id != "-":
        override_id = int(override_id)
        override = branch.getSingleOverride(override_id)
        data["title"] = override["title"]

        # Do not allow arbitrary changing the type
        if not data["type"]:
            data["type"] = override["type"]

        data["content"] = override["content"]
        data["parent_unit"] = override["parent_unit"]
        data["parent_override"] = override["parent_override"]
        data["unit_order"] = override["unit_order"]

    data["title"] = request.json["title"]
    data["content"] = json.dumps(request.json["content"])

    result = branch.updateOrMakeOverride(unit_id, override_id, data)
    if type(result) == bool: abort(500)

    return jsonify({ "override_id": result })


def apply(app):
    app.route("/c/<int:id>/branches")(app.route("/course/<int:id>/<label>/branches")(course_branches))
    app.route("/c/<int:id>/branches/create", methods=["POST"])(app.route("/course/<int:id>/<label>/branches/create", methods=["POST"])(course_create_branch))
    app.route("/c/<int:course_id>/branch/<int:id>")(app.route("/course/<int:course_id>/<course_label>/branch/<int:id>")(course_single_branch))
    app.route("/c/<int:course_id>/branch/<int:branch_id>/item/<unit_id>/<override_id>")(app.route("/course/<int:course_id>/<course_label>/branch/<int:branch_id>/item/<unit_id>/<override_id>")(branch_item))
    app.route("/c/<int:course_id>/branch/<int:branch_id>/update/<unit_id>/<override_id>", methods=["GET", "POST"])(app.route("/course/<int:course_id>/<course_label>/branch/<int:branch_id>/update/<unit_id>/<override_id>", methods=["GET", "POST"])(branch_update_item))
