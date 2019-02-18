# coding: utf-8
from flask import render_template, redirect, abort, url_for, request
from model import privileges as mprivileges, courses as mcourses, user as muser, survey as msurvey, proposal as mproposal, forum as mforum
from controller import query as cquery
import json
def courses_index():
    cuser = muser.getCurrentUser()
    course_list=mcourses.Courses.getCourseList()
    my_courses = mcourses.Courses.getFromUser(cuser)
    my_course_ids = [x.id for x in my_courses]
    now_courses = []
    for c in course_list[::-1]:
        if not c.id in my_course_ids:
            now_courses.append(c)
            if len(now_courses) == 5:
                break
    return render_template('courses/index.html', title=u"Kursüberblick", thispage="course", my_courses=my_courses, now_courses=now_courses)

def courses_propose():
    cuser = muser.getCurrentUser()
    if request.method == "GET":
        return render_template('courses/propose.html', title=u"Kurs vorschlagen", thispage="course", topic=mcourses.Topic)
    elif request.method == "POST":
        if cuser.may("course_propose"):
            data = request.json
            print(data["topic"])
            p = mproposal.Proposal.createNew(data["topic"], data["title"], data["shortdesc"], data["longdesc"], data["requirements"], cuser)
            if p:
                return url_for("proposal_show", id=p.id)
            return "javascript:issueSystemError('Ein Fehler ist aufgetreten.')"
        else:
            abort(405)

def courses_search():
    courses = []
    cnum=None
    if request.values.get("title", "") or request.values.get("shortdesc", "") or request.values.get("topic", "") or request.values.get("status", ""):
        q = []
        add = []
        if request.values.get("title", ""):
            q_, add_ = cquery.buildSFTextQuery("title", request.values.get("title"))
            q.append(q_)
            add.extend(add_)

        if request.values.get("shortdesc", ""):
            q_, add_ = cquery.buildSFTextQuery("shortdesc", request.values.get("shortdesc"))
            q.append(q_)
            add.extend(add_)

        if request.values.get("topic", ""):
            t = request.values.get("topicid", "all")
            if t != "all":
                try:
                    t = int(t)
                    q.append("topic = ?")
                    add.append(t)
                except:
                    pass

        if request.values.get("status", ""):
            s = request.values.get("status", "all")
            if s != "all":
                try:
                    s = int(s)
                    q.append("state = ?")
                    add.append(s)
                except:
                    pass

        if q == []:
            q = ["1=1"]
        q = " AND ".join(q)
        cnum = mcourses.Courses.queryNum(q, add)
        courses = mcourses.Courses.query(q, add, 0, 30)
    #print(cquery.buildSFTextQuery("text", s))
    return render_template('courses/search.html', title=u"Kurse durchsuchen", thispage="course", topic=mcourses.Topic, courses=courses, cnum=cnum)

def course_info(id,label=None):
    if not mcourses.Courses.exists(id):
        abort(404)
    course = mcourses.Courses(id)
    if course.getLabel() != label:
        return redirect(url_for("course_info", id=id, label=course.getLabel()))
    return render_template('courses/info.html', title=course.getTitle(), thispage="course", data=course)

def course_related_proposal(id,label=None):
    if not mcourses.Courses.exists(id):
        abort(404)
    course = mcourses.Courses(id)
    if course.getLabel() != label:
        return redirect(url_for("course_related_proposal", id=id, label=course.getLabel()))
    return redirect(url_for("proposal_show", id=mproposal.Proposal.byCourse(id).id))

def course_edit(id,label=None):
    if not mcourses.Courses.exists(id):
        abort(404)
    course = mcourses.Courses(id)
    cuser = muser.getCurrentUser()
    if course.getLabel() != label:
        return redirect(url_for("course_edit", id=id, label=course.getLabel()))
    if not(cuser.may("course_reviewEdits") or cuser.isMod() or course.getCourseRole(cuser) == 4):
        abort(404)
    if request.method == "POST":
        data = request.json
        print(data)
        course.setDetail("title", data["title"])
        course.setDetail("shortdesc", data["shortdesc"])
        course.setDetail("longdesc", data["longdesc"])
        course.setDetail("requirements", data["requirements"])
        return "ok"
    else:
        return render_template('courses/edit.html', title=course.getTitle(), thispage="course", data=course)

def course_permissions(id,label=None):
    if not mcourses.Courses.exists(id):
        abort(404)
    course = mcourses.Courses(id)
    cuser = muser.getCurrentUser()
    if course.getLabel() != label:
        return redirect(url_for("course_edit", id=id, label=course.getLabel()))
    if not course.getCourseRole(cuser) >= 3:
        abort(404)
    if request.method == "POST":
        return "ok"
    else:
        return render_template('courses/permissions.html', title=course.getTitle(), thispage="course", data=course)

def course_publish(id,label=None):
    if not mcourses.Courses.exists(id):
        abort(404)
    course = mcourses.Courses(id)
    cuser = muser.getCurrentUser()
    if course.getLabel() != label:
        return redirect(url_for("course_publish", id=id, label=course.getLabel()))
    if not course.getCourseRole(cuser) == 4:
        abort(404)
    course.setDetail("state", 1)
    return "ok"

def course_enroll(id,label=None):
    if not mcourses.Courses.exists(id):
        abort(404)
    course = mcourses.Courses(id)
    if course.getLabel() != label:
        return redirect(url_for("course_enroll", id=id, label=course.getLabel()))
    cuser = muser.getCurrentUser()
    if course.getDetail("state") == 0 and not cuser.isMod():
        abort(403)
    if not course.isEnrolled(cuser):
        course.enroll(cuser)
        enrolled_count = course.getEnrolledCount()
        if enrolled_count < 50:
            earners = course.getEnrolledByPerm(4) + course.getEnrolledByPerm(3)
            for e in earners:
                e.setDetail("reputation", 1+e.getInfo()["reputation"])
                e.setReputationChange("enroll", "Kurs: ["+course.getTitle()+"](/c/"+str(course.id)+")", 1)
    return redirect(url_for("course_start", label=course.getLabel(), id=course.id))

def course_start(id,label=None):
    if not mcourses.Courses.exists(id):
        abort(404)
    course = mcourses.Courses(id)
    if course.getLabel() != label:
        return redirect(url_for("course_start", id=id, label=course.getLabel()))
    cuser = muser.getCurrentUser()
    if course.getDetail("state") == 0 and not (cuser.isMod() or course.getCourseRole(cuser) >= 2):
        abort(403)
    last_unit = 0
    if course.isEnrolled(cuser):
        last_unit = course.getLastVisitedUnitId(cuser)
    if last_unit == 0:
        last_unit = course.getFirstUnit(cuser.isMod() or course.getCourseRole(cuser) >= 3)
    if last_unit == 0:
        abort(403)
    return redirect(url_for("unit_show", unit_id=last_unit, course_id=course.id))

def unit_show(unit_id,course_id,unit_label=None,course_label=None):
    if not mcourses.Courses.exists(course_id) or not mcourses.Units.exists(unit_id):
        abort(404)
    course = mcourses.Courses(course_id)
    unit = mcourses.Units(unit_id)
    cuser = muser.getCurrentUser()
    if course.getLabel() != course_label:
        x = url_for("unit_show", course_id=course_id, course_label=course.getLabel(), unit_id=unit_id, unit_label=unit_label if unit_label else unit.getLabel())
        return redirect(x)
    if unit.getLabel() != unit_label:
        return redirect(url_for("unit_show", course_id=course_id, course_label=course_label, unit_id=unit_id, unit_label=unit.getLabel()))
    if course.getDetail("state") == 0 and not (cuser.isMod() or course.getCourseRole(cuser) >= 2):
        abort(403)
    if unit.isDisabled() and not (cuser.isMod() or course.getCourseRole(cuser) >= 3):
        abort(403)
    course.setLastVisitedUnitId(cuser, unit.id)
    if unit.getType() == "info":
        return render_template('courses/unit_info.html', title=course.getTitle() + " - " + unit.getTitle(), thispage="course", course=course, data=unit)
    elif unit.getType() == "extvideo":
        return render_template('courses/unit_extvideo.html', title=course.getTitle() + " - " + unit.getTitle(), thispage="course", course=course, data=unit)
    elif unit.getType() == "survey":
        s = msurvey.Survey(unit.getJSON()["survey"])
        return render_template('courses/unit_survey.html', title=course.getTitle() + " - " + unit.getTitle(), thispage="course", course=course, data=unit, survey=s)
    elif unit.getType() == "quiz":
        try:
            return render_template('courses/unit_quiz.html', title=course.getTitle() + " - " + unit.getTitle(), thispage="course", course=course, data=unit)
        except:
            if request.values.get("re-submit", 0)=="true":
                abort(500)
            data = {"re-submit":"true", "submission-error": "incomplete"}
            return redirect(url_for("unit_show", course_id=course_id, course_label=course_label, unit_id=unit_id, unit_label=unit.getLabel(), **data))
    elif unit.getType() == "pinboard":
        aid = int(unit.getJSON())
        if aid == 0:
            a = None
        else:
            a = mforum.Article(aid)
        return render_template('courses/unit_pinboard.html', title=course.getTitle() + " - " + unit.getTitle(), thispage="course", course=course, data=unit, post=a)
    abort(500)

def unit_edit(unit_id,course_id,unit_label=None,course_label=None):
    if not mcourses.Courses.exists(course_id) or not mcourses.Units.exists(unit_id):
        abort(404)
    course = mcourses.Courses(course_id)
    unit = mcourses.Units(unit_id)
    cuser = muser.getCurrentUser()
    if not (cuser.isMod() or course.getCourseRole(cuser) >= 3):
        abort(404)
    if request.method == "POST":
        unit.setDetail("title", request.json["title"])
        unit.setDetail("availible", request.json["availible"])
        unit.setDetail("content", json.dumps(request.json["content"]))
        return "{ok}"
    else:
        if course.getLabel() != course_label:
            x = url_for("unit_edit", course_id=course_id, course_label=course.getLabel(), unit_id=unit_id, unit_label=unit_label if unit_label else unit.getLabel())
            return redirect(x)
        if unit.getLabel() != unit_label:
            return redirect(url_for("unit_edit", course_id=course_id, course_label=course_label, unit_id=unit_id, unit_label=unit.getLabel()))
        if unit.getType() == "info":
            return render_template('courses/edit_unit_info.html', title="[Bearbeiten] " + course.getTitle() + " - " + unit.getTitle(), thispage="course", course=course, data=unit)
        elif unit.getType() == "extvideo":
            return render_template('courses/edit_unit_extvideo.html', title="[Bearbeiten] " + course.getTitle() + " - " + unit.getTitle(), thispage="course", course=course, data=unit)
        elif unit.getType() == "survey":
            return render_template('courses/edit_unit_survey.html', title="[Bearbeiten] " + course.getTitle() + " - " + unit.getTitle(), thispage="course", course=course, data=unit)
        elif unit.getType() == "quiz":
            return render_template('courses/edit_unit_quiz.html', title="[Bearbeiten] " + course.getTitle() + " - " + unit.getTitle(), thispage="course", course=course, data=unit)
        elif unit.getType() == "pinboard":
            return render_template('courses/edit_unit_pinboard.html', title="[Bearbeiten] " + course.getTitle() + " - " + unit.getTitle(), thispage="course", course=course, data=unit)
        abort(500)


def unit_submit(unit_id,course_id,unit_label=None,course_label=None):
    if not mcourses.Courses.exists(course_id) or not mcourses.Units.exists(unit_id):
        abort(404)
    course = mcourses.Courses(course_id)
    unit = mcourses.Units(unit_id)
    cuser = muser.getCurrentUser()
    if unit.getType() == "quiz":
        MAX_SCORE = 0
        TOTAL_SCORE = 0
        RESULT_DATA = {}
        data = request.json
        master = unit.getJSON()
        k = 0
        for i in master:
            k += 1
            if i["type"] == "text-answer":
                MAX_SCORE += int(i["data"]["points"])
                if str(k) in data.keys():
                    _ = data[str(k)]
                    if _.lower() in map(lambda x:x.lower(), i["data"]["correct"]):
                        TOTAL_SCORE += int(i["data"]["points"])
                        RESULT_DATA[k] = ({"max":i["data"]["points"], "sum":i["data"]["points"], "selection":_, "correct":i["data"]["correct"]})
                    else:
                        RESULT_DATA[k] = ({"max":i["data"]["points"], "sum":0, "selection":_, "correct":i["data"]["correct"]})
            elif i["type"] == "multiple-choice":
                MAX_SCORE += int(i["data"]["points"])
                if str(k) in data.keys():
                    _ = data[str(k)]
                    if i["data"]["choices"][int(_)].startswith("*"):
                        TOTAL_SCORE += int(i["data"]["points"])
                        RESULT_DATA[k] = ({"max":i["data"]["points"], "sum":i["data"]["points"], "selection":_, "correct":i["data"]["choices"]})
                    else:
                        RESULT_DATA[k] = ({"max":i["data"]["points"], "sum":0, "selection":_, "correct":i["data"]["choices"]})
            elif i["type"] == "multiple-answer":
                MAX_SCORE += int(i["data"]["points"])
                if str(k) in data.keys():
                    _ = data[str(k)]
                    total = float(len(i["data"]["choices"]))
                    correct = 0
                    Zid=0
                    for Z in i["data"]["choices"]:
                        if Z.startswith("*") == (Zid in map(lambda x:int(x), _)):
                            correct += 1
                        Zid += 1
                    pts = (correct/total)*int(i["data"]["points"])
                    pts = round(pts, 1)
                    TOTAL_SCORE += pts
                    RESULT_DATA[k] = ({"max":i["data"]["points"], "sum":pts, "selection":_, "correct":i["data"]["choices"]})

        unit.addViewData(cuser, json.dumps({"result":RESULT_DATA, "max": MAX_SCORE, "sum": TOTAL_SCORE}))
        return "{ok}"
    abort(500)

def unit_new(course_id):
    if not mcourses.Courses.exists(course_id):
        abort(404)
    course = mcourses.Courses(course_id)
    cuser = muser.getCurrentUser()
    if not (cuser.isMod() or course.getCourseRole(cuser) >= 3):
        abort(404)
    empty_set = {
        "info":"[]",
        "quiz":"[]",
        "extvideo": '{"platform":"youtube", "embedcode": ""}',
        "pinboard": '0'
    }
    if request.json["type"] == "survey":
        s = msurvey.Survey.new(course.id, cuser.id)
        empty_set["survey"] = '{"survey":'+str(s.id)+'}'
    x = mcourses.Units.new(course.id, empty_set[request.json["type"]], request.json["type"], request.json["parent"])
    return url_for("unit_show", unit_id=x, course_id=course_id)

def topic_index():
    return render_template('topic/index.html', title=u"Themen", thispage="course", topic=mcourses.Topic)

def topic_info(name, id=None):
    if not mcourses.Topic.exists(name):
        abort(404)
    topic = mcourses.Topic.from_name(name)
    if topic.id != id:
        return redirect(url_for("topic_info", name=name, id=topic.id))
    return render_template('topic/info.html', title=topic.getTitle(), thispage="course", data=topic)

def topic_courses(name, id=None):
    if not mcourses.Topic.exists(name):
        abort(404)
    topicCourseList=mcourses.Topic.getCourseList(name)
    print(topicCourseList)
    topic = mcourses.Topic.from_name(name)
    if topic.id != id:
        return redirect(url_for("topic_courses", name=name, id=topic.id))
    return render_template('topic/courses.html', title=topic.getTitle()+u" – Kurse", thispage="course", courses=topicCourseList, data=topic)

def topic_edit(name, id=None):
    if not mcourses.Topic.exists(name):
        abort(404)
    topic = mcourses.Topic.from_name(name)
    if topic.id != id:
        return redirect(url_for("topic_edit", name=name, id=topic.id))
    cuser = muser.getCurrentUser()
    if not cuser.isAdmin():
        abort(404)
    if request.method == "GET":
        return render_template('topic/edit.html', title=topic.getTitle()+u" – Bearbeiten", thispage="course", data=topic)
    else:
        data = request.json
        print(data)
        topic.setDetail("title", data["title"])
        topic.setDetail("excerpt", data["excerpt"])
        topic.setDetail("description", data["description"])
        topic.setDetail("name", data["name"])
        topic.setDetail("giveable", data["giveable"])
        return "ok"

def course_unit_reorder(id,label=None):
    if not mcourses.Courses.exists(id):
        abort(404)
    course = mcourses.Courses(id)
    cuser = muser.getCurrentUser()
    if course.getLabel() != label:
        return redirect(url_for("course_unit_reorder", id=id, label=course.getLabel()))
    if not(course.getCourseRole(cuser) == 4):
        abort(404)
    if request.method == "POST":
        return "ok"
    else:
        return render_template('courses/unit_reorder.html', title="Kursmodule neu anordnen: " + course.getTitle(), thispage="course", data=course)

def apply(app):
    app.route("/courses")(courses_index)
    app.route("/course/propose", methods=["GET", "POST"])(courses_propose)
    app.route("/c/search")(app.route("/course/search")(courses_search))
    app.route("/c/<int:id>")(app.route("/c/<int:id>/info")(app.route("/course/<int:id>/<label>/details")(course_info)))
    app.route("/c/<int:id>/proposal")(app.route("/course/<int:id>/<label>/proposal")(course_related_proposal))
    app.route("/c/<int:id>/edit", methods=["GET", "POST"])(app.route("/course/<int:id>/<label>/edit", methods=["GET", "POST"])(course_edit))
    app.route("/@/c/<int:id>/permissions", methods=["GET", "POST"])(app.route("/@/course/<int:id>/<label>/permissions", methods=["GET", "POST"])(course_permissions))
    app.route("/c/<int:id>/publish", methods=["GET", "POST"])(app.route("/course/<int:id>/<label>/publish", methods=["GET", "POST"])(course_publish))
    app.route("/c/<int:id>/enroll")(app.route("/course/<int:id>/<label>/enroll")(course_enroll))
    app.route("/c/<int:id>/start")(app.route("/course/<int:id>/<label>/start")(course_start))
    app.route("/c/<int:course_id>/<int:unit_id>", methods=["GET", "POST"])(app.route("/c/<int:course_id>/u/<int:unit_id>", methods=["GET", "POST"])(app.route("/course/<int:course_id>/<course_label>/unit/<int:unit_id>/<unit_label>/show", methods=["GET", "POST"])(unit_show)))
    app.route("/c/<int:course_id>/u/<int:unit_id>/edit", methods=["GET", "POST"])(app.route("/course/<int:course_id>/<course_label>/unit/<int:unit_id>/<unit_label>/edit", methods=["GET", "POST"])(unit_edit))
    app.route("/c/<int:course_id>/u/<int:unit_id>/submit", methods=["POST"])(app.route("/course/<int:course_id>/<course_label>/unit/<int:unit_id>/<unit_label>/submit", methods=["POST"])(unit_submit))
    app.route("/c/<int:course_id>/u/new", methods=["GET", "POST"])(app.route("/course/<int:course_id>/<course_label>/unit/new", methods=["GET", "POST"])(unit_new))
    app.route("/topics")(topic_index)
    app.route("/t/<name>")(app.route("/t/<name>/info")(app.route("/topic/<int:id>/<name>/info")(topic_info)))
    app.route("/t/<name>/c")(app.route("/t/<name>/courses")(app.route("/topic/<int:id>/<name>/courses")(topic_courses)))
    app.route("/t/<name>/e", methods=["GET", "POST"])(app.route("/topic/<int:id>/<name>/edit", methods=["GET", "POST"])(topic_edit))
    app.route("/c/<int:id>/unit_reorder", methods=["GET", "POST"])(app.route("/course/<int:id>/<label>/unit_reorder", methods=["GET", "POST"])(course_unit_reorder))
