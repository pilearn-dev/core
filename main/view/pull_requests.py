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

    existing_branch = mpull_requests.Branch.getByCourseAndUser(course.id, cuser.id, True)
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

    existing_branch = mpull_requests.Branch.getByCourseAndUser(course.id, cuser.id, True)
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

    return render_template('courses/pull-requests/branch.html', title="Branch #" + str(branch.id) + u" für " + course.getTitle(), thispage="courses", course=course, branch=branch)

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

    data = _mkdata(unit_id, override_id, course_id, branch)

    if branch.getDetail("pull_request") or branch.isAbandoned():
        return render_template('courses/pull-requests/item.static/' + data["type"] + '.html', title="Branch #" + str(branch.id) + u" für " + course.getTitle(), thispage="courses", course=course, branch=branch, data=data, unit_id=unit_id, override_id=override_id, int=int)
    else:
        return render_template('courses/pull-requests/item/' + data["type"] + '.html', title="Branch #" + str(branch.id) + u" für " + course.getTitle(), thispage="courses", course=course, branch=branch, data=data, unit_id=unit_id, override_id=override_id)

def branch_update_item(unit_id, override_id, branch_id, course_id,course_label=None):
    if not mcourses.Courses.exists(course_id):
        abort(404)
    course = mcourses.Courses(course_id)
    cuser = muser.getCurrentUser()
    if course.getLabel() != course_label and request.method != "POST":
        return redirect(url_for("branch_update_item", branch_id=branch_id, course_id=course_id, course_label=course.getLabel(), unit_id=unit_id, override_id=override_id))
    if not mpull_requests.Branch.exists(branch_id):
        abort(404)
    branch = mpull_requests.Branch(branch_id)

    if branch.getDetail("pull_request") or branch.isAbandoned(): abort(404)

    if not (branch.getDetail("author") == cuser.id or cuser.isMod()) or cuser.isDisabled() or branch.getDetail("course_id") != course.id:
        abort(404)

    data = _mkdata(unit_id, override_id, course_id, branch)

    data["title"] = request.json["title"]
    data["content"] = json.dumps(request.json["content"])

    result = branch.updateOrMakeOverride(unit_id, override_id, data)
    if type(result) == bool: abort(500)

    return jsonify({ "override_id": result })

def branch_revert_override(override_id, branch_id, course_id,course_label=None):
    if not mcourses.Courses.exists(course_id):
        abort(404)
    course = mcourses.Courses(course_id)
    cuser = muser.getCurrentUser()
    if course.getLabel() != course_label and request.method != "POST":
        return redirect(url_for("branch_revert_override", branch_id=branch_id, course_id=course_id, course_label=course.getLabel(), override_id=override_id))
    if not mpull_requests.Branch.exists(branch_id):
        abort(404)
    branch = mpull_requests.Branch(branch_id)

    if branch.getDetail("pull_request") or branch.isAbandoned(): abort(404)

    if not (branch.getDetail("author") == cuser.id or cuser.isMod()) or cuser.isDisabled() or branch.getDetail("course_id") != course.id:
        abort(404)

    override = branch.getSingleOverride(override_id)
    if not override or override["branch"] != branch_id:
        abort(404)
    branch.removeOverride(override_id)

    return redirect(url_for("course_single_branch", id=branch_id, course_id=course_id, course_label=course.getLabel()))

def branch_new_item(branch_id, course_id,course_label=None):
    if not mcourses.Courses.exists(course_id):
        abort(404)
    course = mcourses.Courses(course_id)
    cuser = muser.getCurrentUser()
    if course.getLabel() != course_label and request.method != "POST":
        return redirect(url_for("branch_new_item", branch_id=branch_id, course_id=course_id, course_label=course.getLabel()))
    if not mpull_requests.Branch.exists(branch_id):
        abort(404)
    branch = mpull_requests.Branch(branch_id)

    if branch.getDetail("pull_request") or branch.isAbandoned(): abort(404)

    if not (branch.getDetail("author") == cuser.id or cuser.isMod()) or cuser.isDisabled() or branch.getDetail("course_id") != course.id:
        abort(404)

    empty_set = {
        "info":"[]",
        "quiz":"[]",
        "extvideo": '{"platform":"youtube", "embedcode": ""}'
    }

    x = branch.newUnitOverride("Neue Seite", empty_set[request.json["type"]], request.json["type"])

    return url_for("branch_item", branch_id=branch_id, course_id=course_id, course_label=course.getLabel(), unit_id="-", override_id=x)

def branch_unit_reorder(branch_id, course_id,course_label=None):
    if not mcourses.Courses.exists(course_id):
        abort(404)
    course = mcourses.Courses(course_id)
    cuser = muser.getCurrentUser()
    if course.getLabel() != course_label and request.method != "POST":
        return redirect(url_for("branch_unit_reorder", branch_id=branch_id, course_id=course_id, course_label=course.getLabel()))
    if not mpull_requests.Branch.exists(branch_id):
        abort(404)
    branch = mpull_requests.Branch(branch_id)

    if branch.getDetail("pull_request") or branch.isAbandoned(): abort(404)

    if request.method == "POST":
        datar = (request.json)
        for item in datar:
            unit_id, override_id = item["id"].split("/")

            data = _mkdata(unit_id, override_id, course_id, branch)

            unit_id = int(unit_id) if unit_id != "-" else 0
            if data["parent_unit"] != 0 or data["parent_override"] != 0 or data["unit_order"] != item["order"]:
                data["parent_unit"] = 0
                data["parent_override"] = 0
                data["unit_order"] = item["order"]

                data["content"] = json.dumps(data["content"])
                branch.updateOrMakeOverride(unit_id, override_id, data)


            for subitem in item["subitems"]:
                sub_unit_id, sub_override_id = subitem["id"].split("/")
                data = _mkdata(sub_unit_id, sub_override_id, course_id, branch)

                sub_unit_id = int(sub_unit_id) if sub_unit_id != "-" else 0
                parent_unit, parent_override = unit_id, int(override_id) if override_id != "-" else 0

                if data["parent_unit"] != parent_unit or data["parent_override"] != parent_override or data["unit_order"] != subitem["order"]:
                    data["parent_unit"] = parent_unit
                    data["parent_override"] = parent_override
                    data["unit_order"] = subitem["order"]

                    data["content"] = json.dumps(data["content"])
                    branch.updateOrMakeOverride(sub_unit_id, sub_override_id, data)

        return "ok"
    else:
        return render_template('courses/pull-requests/reorder.html', title="Branch #" + str(branch.id) + u" für " + course.getTitle(), thispage="courses", course=course, branch=branch)

def branch_submit(branch_id, course_id,course_label=None):
    if not mcourses.Courses.exists(course_id):
        abort(404)
    course = mcourses.Courses(course_id)
    cuser = muser.getCurrentUser()
    if course.getLabel() != course_label and request.method != "POST":
        return redirect(url_for("branch_submit", branch_id=branch_id, course_id=course_id, course_label=course.getLabel()))
    if not mpull_requests.Branch.exists(branch_id):
        abort(404)
    branch = mpull_requests.Branch(branch_id)

    if branch.getDetail("pull_request") or branch.isAbandoned(): abort(404)

    if request.method == "POST":
        if course.getCourseRole(cuser) < 3:
            branch.calculateRepDelta()
        else:
            branch.setDetail("delta_factor", 0)
        pr = mpull_requests.PullRequest.new(course.id, branch.id, cuser.id, request.json["title"], request.json["description"])
        branch.setDetail("pull_request", pr.id)
        return jsonify({"url": url_for("course_single_pr", id=pr.id, course_id=course.id, course_label=course.getLabel())})
    else:
        return render_template('courses/pull-requests/submit.html', title="Neues Pull Request zu Branch #" + str(branch.id) + u" für " + course.getTitle(), thispage="courses", course=course, branch=branch)

def branch_cancel(branch_id, course_id,course_label=None):
    if not mcourses.Courses.exists(course_id):
        abort(404)
    course = mcourses.Courses(course_id)
    cuser = muser.getCurrentUser()
    if course.getLabel() != course_label and request.method != "POST":
        return redirect(url_for("branch_submit", branch_id=branch_id, course_id=course_id, course_label=course.getLabel()))
    if not mpull_requests.Branch.exists(branch_id):
        abort(404)
    branch = mpull_requests.Branch(branch_id)

    if branch.getDetail("pull_request") or branch.isAbandoned(): abort(404)

    if request.method == "POST":
        branch.setDetail("abandoned", 1)
        branch.setDetail("abandoned_date", time.time())
        return jsonify({"url": url_for("course_single_branch", id=branch.id, course_id=course.id, course_label=course.getLabel())})
    else:
        return render_template('courses/pull-requests/cancel.html', title="Verwerfen: Branch #" + str(branch.id) + u" für " + course.getTitle(), thispage="courses", course=course, branch=branch)


def course_prs(course_id,course_label=None):
    if not mcourses.Courses.exists(course_id):
        abort(404)
    course = mcourses.Courses(course_id)
    cuser = muser.getCurrentUser()
    if course.getLabel() != course_label and request.method != "POST":
        return redirect(url_for("course_prs", course_id=course_id, course_label=course.getLabel()))

    open_prs, closed_prs = mpull_requests.PullRequest.getByCourse(course.id, True), mpull_requests.PullRequest.getByCourse(course.id, False)

    return render_template('courses/pull-requests/prs.html', title=u"Pull Requests für " + course.getTitle(), thispage="courses", course=course, open_prs=open_prs, closed_prs=closed_prs)


def course_single_pr(id, course_id,course_label=None):
    if not mcourses.Courses.exists(course_id):
        abort(404)
    course = mcourses.Courses(course_id)
    cuser = muser.getCurrentUser()
    if course.getLabel() != course_label and request.method != "POST":
        return redirect(url_for("course_single_pr", id=id, course_id=course_id, course_label=course.getLabel()))
    if not mpull_requests.PullRequest.exists(id):
        abort(404)
    pr = mpull_requests.PullRequest(id)
    branch = pr.getBranch()

    if pr.isHiddenAsSpam() and not cuser.isLoggedIn() or pr.getDetail("course_id") != course.id:
        abort(404)

    return render_template('courses/pull-requests/pr.html', title="PR #" + str(pr.id) + u" für " + course.getTitle(), thispage="courses", course=course, pr=pr, branch=branch)

def course_decide_pr(id, course_id,course_label=None):
    if not mcourses.Courses.exists(course_id):
        abort(404)
    course = mcourses.Courses(course_id)
    cuser = muser.getCurrentUser()
    if course.getLabel() != course_label and request.method != "POST":
        return redirect(url_for("course_single_pr", id=id, course_id=course_id, course_label=course.getLabel()))
    if not mpull_requests.PullRequest.exists(id):
        abort(404)
    pr = mpull_requests.PullRequest(id)
    branch = pr.getBranch()

    if pr.isHiddenAsSpam() and not cuser.isLoggedIn() or pr.getDetail("course_id") != course.id:
        abort(404)

    if pr.getState() != 0:
        abort(404)

    if not(cuser.isMod() or course.getCourseRole(cuser) >= 3):
        abort(403)

    if request.json["decision"] not in range(-1, 2):
        abort(400)

    if request.json["as_abuse"] not in [True, False]:
        abort(400)

    pr.setDetail("decision", request.json["decision"])
    pr.setDetail("decision_date", time.time())
    pr.setDetail("hide_as_spam", request.json["as_abuse"])

    branch.setDetail("decision", request.json["decision"])
    branch.setDetail("decision_date", time.time())
    branch.setDetail("hide_as_spam", request.json["as_abuse"])

    if request.json["decision"] == 1:
        au = branch.getAuthor()
        au.setReputationChange("pr", u"[Pull Request #"+str(pr.id)+ u" für " + course.getTitle() + "](/c/"+str(course.id)+"/pull-request/" + str(pr.id) + ")", branch.getDetail("delta_factor"))
        au.regetRep()
        branch.apply()

    return "ok"

def _mkdata(unit_id, override_id, course_id, branch):
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
        if not override or (unit_id != "-" and override["overrides"] != unit_id) or override["branch"] != branch.id:
            abort(404)
        data["title"] = override["title"]

        # Do not allow arbitrary changing the type
        if not data["type"]:
            data["type"] = override["type"]

        data["content"] = json.loads(override["content"])
        data["parent_unit"] = override["parent_unit"]
        data["parent_override"] = override["parent_override"]
        data["unit_order"] = override["unit_order"]

    return data

def apply(app):
    app.route("/c/<int:id>/branches")(app.route("/course/<int:id>/<label>/branches")(course_branches))
    app.route("/c/<int:id>/branches/create", methods=["POST"])(app.route("/course/<int:id>/<label>/branches/create", methods=["POST"])(course_create_branch))
    app.route("/c/<int:course_id>/branch/<int:id>")(app.route("/course/<int:course_id>/<course_label>/branch/<int:id>")(course_single_branch))
    app.route("/c/<int:course_id>/branch/<int:branch_id>/item/<unit_id>/<override_id>")(app.route("/course/<int:course_id>/<course_label>/branch/<int:branch_id>/item/<unit_id>/<override_id>")(branch_item))
    app.route("/c/<int:course_id>/branch/<int:branch_id>/update/<unit_id>/<override_id>", methods=["POST"])(app.route("/course/<int:course_id>/<course_label>/branch/<int:branch_id>/update/<unit_id>/<override_id>", methods=["POST"])(branch_update_item))
    app.route("/c/<int:course_id>/branch/<int:branch_id>/revert/<int:override_id>", methods=["GET", "POST"])(app.route("/course/<int:course_id>/<course_label>/branch/<int:branch_id>/revert/<int:override_id>", methods=["GET", "POST"])(branch_revert_override))
    app.route("/c/<int:course_id>/branch/<int:branch_id>/new-item", methods=["POST"])(app.route("/course/<int:course_id>/<course_label>/branch/<int:branch_id>/new-item", methods=["POST"])(branch_new_item))
    app.route("/c/<int:course_id>/branch/<int:branch_id>/reorder", methods=["GET", "POST"])(app.route("/course/<int:course_id>/<course_label>/branch/<int:branch_id>/reorder", methods=["GET", "POST"])(branch_unit_reorder))

    app.route("/c/<int:course_id>/branch/<int:branch_id>/submit", methods=["GET", "POST"])(app.route("/course/<int:course_id>/<course_label>/branch/<int:branch_id>/submit", methods=["GET", "POST"])(branch_submit))
    app.route("/c/<int:course_id>/branch/<int:branch_id>/cancel", methods=["GET", "POST"])(app.route("/course/<int:course_id>/<course_label>/branch/<int:branch_id>/cancel", methods=["GET", "POST"])(branch_cancel))

    app.route("/c/<int:course_id>/pull-requests")(app.route("/course/<int:course_id>/<course_label>/pull-requests")(course_prs))
    app.route("/c/<int:course_id>/pull-request/<int:id>")(app.route("/course/<int:course_id>/<course_label>/pull-request/<int:id>")(course_single_pr))
    app.route("/c/<int:course_id>/pull-request/<int:id>/add-decision", methods=["POST"])(app.route("/course/<int:course_id>/<course_label>/pull-request/<int:id>/add-decision", methods=["POST"])(course_decide_pr))
