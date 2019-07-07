# coding: utf-8
from flask import render_template, redirect, abort, url_for, request, jsonify
from model import privileges as mprivileges, courses as mcourses, user as muser, survey as msurvey, proposal as mproposal, forum as mforum, pull_requests as mpull_requests
from controller import query as cquery
import json, time

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
        return redirect(url_for("course_view_branch", id=id, course_id=course_id, course_label=course.getLabel()))
    if not mpull_requests.Branch.exists(id):
        abort(404)
    branch = mpull_requests.Branch(id)

    if not (branch.getDetail("author") == cuser.id or cuser.isMod()) or cuser.isDisabled() or branch.getDetail("course_id") != course.id:
        abort(404)

    return render_template('courses/pull-requests/branch.html', title="Branch #" + str(branch.id) + u" für " + course.getTitle(), thispage="courses", course=course, branch=branch)


def apply(app):
    app.route("/c/<int:id>/branches")(app.route("/course/<int:id>/<label>/branches")(course_branches))
    app.route("/c/<int:id>/branches/create", methods=["POST"])(app.route("/course/<int:id>/<label>/branches/create", methods=["POST"])(course_create_branch))
    app.route("/c/<int:course_id>/branch/<int:id>")(app.route("/course/<int:course_id>/<course_label>/branch/<int:id>")(course_single_branch))
