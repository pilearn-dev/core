# coding: utf-8
from flask import render_template, redirect, abort, url_for, request, jsonify
from model import privileges as mprivileges, courses as mcourses, user as muser, survey as msurvey, proposal as mproposal, forum as mforum
from controller import query as cquery
import json, time
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
    return render_template('courses/index.html', title=u"Kursüberblick", thispage="courses", my_courses=my_courses, now_courses=now_courses)

def courses_propose():
    cuser = muser.getCurrentUser()
    if request.method == "GET":
        return render_template('courses/propose.html', title=u"Kurs vorschlagen", thispage="courses", topic=mcourses.Topic)
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
    return render_template('courses/search.html', title=u"Kurse durchsuchen", thispage="courses", topic=mcourses.Topic, courses=courses, cnum=cnum)

def course_info(id,label=None):
    if not mcourses.Courses.exists(id):
        abort(404)
    course = mcourses.Courses(id)
    if course.getLabel() != label:
        return redirect(url_for("course_info", id=id, label=course.getLabel()))
    return render_template('courses/info.html', title=course.getTitle(), thispage="courses", data=course, ForumAnnouncement=mforum.ForumAnnouncement)

def course_related_proposal(id,label=None):
    if not mcourses.Courses.exists(id):
        abort(404)
    course = mcourses.Courses(id)
    if course.getLabel() != label:
        return redirect(url_for("course_related_proposal", id=id, label=course.getLabel()))
    return redirect(url_for("proposal_show", id=mproposal.Proposal.byCourse(id).id))

def course_admin(id,label=None, page="identity"):
    if not mcourses.Courses.exists(id):
        abort(404)
    course = mcourses.Courses(id)
    cuser = muser.getCurrentUser()
    if course.getLabel() != label and request.method != "POST":
        return redirect(url_for("course_admin", id=id, label=course.getLabel()))
    if not(cuser.isMod() or course.getCourseRole(cuser) == 4):
        abort(404)
    if page == "identity":
        if request.method == "POST":

            data = request.json

            title = data["title"].strip()
            shortdesc = data["shortdesc"]
            longdesc = data["longdesc"]
            requirements = data["requirements"]

            errors = []

            if 5 <= len(title) <= 80:
                course.setDetail("title", title)
            else:
                if 5 > len(title):
                    errors.append(u"Der Titel des Kurses ist zu kurz. Mindestens 5 Zeichen erforderlich. (aktuell: %i)" % len(title))
                if 80 < len(title):
                    errors.append(u"Der Titel des Kurses ist zu lang. Höchstens 80 Zeichen möglich. (aktuell: %i)" % len(title))

            if 15 <= len(shortdesc) <= 280:
                course.setDetail("shortdesc", shortdesc)
            else:
                if 5 > len(shortdesc):
                    errors.append(u"Die Kurzbeschreibung ist zu kurz. Mindestens 15 Zeichen erforderlich. (aktuell: %i)" % len(shortdesc))
                if 280 < len(shortdesc):
                    errors.append(u"Die Kurzbeschreibung ist zu lang. Höchstens 280 Zeichen möglich. (aktuell: %i)" % len(shortdesc))

            if 50 <= len(longdesc) <= 15000:
                course.setDetail("longdesc", longdesc)
            else:
                if 5 > len(longdesc):
                    errors.append(u"Die Kurzbeschreibung ist zu kurz. Mindestens 50 Zeichen erforderlich. (aktuell: %i)" % len(longdesc))
                if 15000 < len(longdesc):
                    errors.append(u"Die Kurzbeschreibung ist zu lang. Höchstens 15000 Zeichen möglich. (aktuell: %i)" % len(longdesc))

            if 10 <= len(requirements) <= 7500:
                course.setDetail("requirements", requirements)
            else:
                if 5 > len(requirements):
                    errors.append(u"Die Kurzbeschreibung ist zu kurz. Mindestens 10 Zeichen erforderlich. (aktuell: %i)" % len(requirements))
                if 7500 < len(requirements):
                    errors.append(u"Die Kurzbeschreibung ist zu lang. Höchstens 7500 Zeichen möglich. (aktuell: %i)" % len(requirements))

            if len(errors):
                return jsonify({
                    "result": "error",
                    "errors": errors
                })
            else:
                return jsonify({
                    "result": "ok"
                })

        else:
            return render_template('courses/admin/identity.html', title=course.getTitle(), thispage="courses", course=course)
    elif page == "announcements":
        return render_template("announcements/list.html", title=course.getTitle(), forum=mforum.Forum(course.id), announcements=mforum.ForumAnnouncement.byForum(course.id, True), thispage="courses")
    elif page == "publish":
        if request.method == "POST":
            course.setDetail("state", 1)
            return "{ok}"
        else:
            return render_template('courses/admin/publish.html', title=course.getTitle(), thispage="courses", course=course)
    elif page == "membership":
        if request.method == "POST":
            if request.json["action"] == "give-role":
                user_to_receive = muser.User(request.json["user"])
                role_to_receive = request.json["role"]
                if not role_to_receive in range(1, 5):
                    return jsonify({ "result": "error", "error": u"Ungültige Ziel-Rolle" })
                if course.isEnrolled(user_to_receive):
                    course.setCourseRole(user_to_receive, role_to_receive)
                    return jsonify({ "result": "success"})
                else:
                    return jsonify({ "result": "error", "error": u"Nur möglich für Benutzer, die im Kurs eingeschrieben sind." })
            elif request.json["action"] == "revoke-role":
                user_to_receive = muser.User(request.json["user"])
                if course.isEnrolled(user_to_receive) and course.getCourseRole(user_to_receive) != 1:
                    course.setCourseRole(user_to_receive, 1)
                    return jsonify({ "result": "success"})
            elif request.json["action"] == "kick-remove":
                user_to_receive = muser.User(request.json["user"])
                if course.isEnrolled(user_to_receive) and course.getCourseRole(user_to_receive) == 1:
                    course.unenroll(user_to_receive)
                    user_to_receive.customflag(u"Benutzer von " + cuser.getHTMLName(False) + u" (#" + str(cuser.id) + u") aus dem Kurs " + course.getTitle() + u" (#" + str(course.id) + ") geworfen.", muser.User.from_id(-1))
                    return jsonify({ "result": "success"})
                else:
                    return jsonify({ "result": "error", "error": u"Nicht möglich: Benutzer nicht eingeschrieben oder Benutzer hat Rolle." })

            return jsonify({ "result": "error", "error": u"Ungültige Anfrage" })
        else:
            return render_template('courses/admin/membership.html', title=course.getTitle(), thispage="courses", course=course)
    else:
        abort(404)

def course_edit_overview(id,label=None):
    if not mcourses.Courses.exists(id):
        abort(404)
    course = mcourses.Courses(id)
    cuser = muser.getCurrentUser()
    if course.getLabel() != label and request.method != "POST":
        return redirect(url_for("course_edit_overview", id=id, label=course.getLabel()))
    if not(cuser.isMod() or course.getCourseRole(cuser) >= 3):
        abort(404)

    return render_template('courses/edit/index.html', title=course.getTitle(), thispage="courses", course=course)


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
        return render_template('courses/units/info.html', title=course.getTitle() + " - " + unit.getTitle(), thispage="courses", course=course, data=unit)
    elif unit.getType() == "extvideo":
        return render_template('courses/units/extvideo.html', title=course.getTitle() + " - " + unit.getTitle(), thispage="courses", course=course, data=unit)
    elif unit.getType() == "survey":
        s = msurvey.Survey(unit.getJSON()["survey"])
        return render_template('courses/units/survey.html', title=course.getTitle() + " - " + unit.getTitle(), thispage="courses", course=course, data=unit, survey=s)
    elif unit.getType() == "quiz":
        try:
            return render_template('courses/units/quiz.html', title=course.getTitle() + " - " + unit.getTitle(), thispage="courses", course=course, data=unit, int=int)
        except Exception as e:
            if request.values.get("re-submit", 0)=="true":
                raise e
            data = {"re-submit":"true", "submission-error": "incomplete"}
            return redirect(url_for("unit_show", course_id=course_id, course_label=course_label, unit_id=unit_id, unit_label=unit.getLabel(), **data))
    elif unit.getType() == "pinboard":
        aid = int(unit.getJSON())
        if aid == 0:
            a = None
        else:
            a = mforum.Article(aid)
        return render_template('courses/units/pinboard.html', title=course.getTitle() + " - " + unit.getTitle(), thispage="courses", course=course, data=unit, post=a)
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
            return render_template('courses/edit/unit-info.html', title=course.getTitle() + " - " + unit.getTitle(), thispage="courses", course=course, data=unit)
        elif unit.getType() == "extvideo":
            return render_template('courses/edit/unit-extvideo.html', title=course.getTitle() + " - " + unit.getTitle(), thispage="courses", course=course, data=unit)
        elif unit.getType() == "survey":
            return render_template('courses/edit/unit-survey.html', title=course.getTitle() + " - " + unit.getTitle(), thispage="courses", course=course, data=unit)
        elif unit.getType() == "quiz":
            return render_template('courses/edit/unit-quiz.html', title=course.getTitle() + " - " + unit.getTitle(), thispage="courses", course=course, data=unit)
        elif unit.getType() == "pinboard":
            return render_template('courses/edit/unit-pinboard.html', title=course.getTitle() + " - " + unit.getTitle(), thispage="courses", course=course, data=unit)
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
    elif unit.getType() == "pinboard":
        aid = int(unit.getJSON())
        if aid == 0:
            abort(500)
        else:
            a = mforum.Article(aid)

        data = request.json
        answer = mforum.Answer.createNew(a.getDetail("forumID"), aid, data["comment"], muser.User(-1))
        answer.addRevision(data["comment"], cuser, u"Ursprüngliche Version")

        a.setDetail("last_activity_date", time.time())
        answer.setDetail("last_activity_date", time.time())
        answer.setDetail("creation_date", time.time())
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
    return render_template('topic/index.html', title=u"Themen", thispage="courses", topic=mcourses.Topic)

def topic_view(name):
    if not mcourses.Topic.exists(name):
        abort(404)
    topicCourseList=mcourses.Topic.getCourseList(name)
    topic = mcourses.Topic.from_name(name)
    return render_template('topic/courses.html', title=topic.getTitle()+u" – Kurse", thispage="courses", courses=topicCourseList, data=topic)

def topic_edit(name):
    if not mcourses.Topic.exists(name):
        abort(404)
    topic = mcourses.Topic.from_name(name)
    cuser = muser.getCurrentUser()
    if not cuser.isMod():
        abort(404)
    if request.method == "GET":
        return render_template('topic/edit.html', title=topic.getTitle()+u" – Bearbeiten", thispage="courses", data=topic)
    else:
        data = request.json
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
    if not(course.getCourseRole(cuser) == 4):
        abort(404)
    if request.method == "POST":
        data = (request.json)
        for item in data:
            u = mcourses.Units(item["id"])
            if u.getDetail("courseid") != id:
                return "invalid"
            u.setDetail("unit_order", item["order"])
            u.setDetail("parent", 0)
            for subitem in item["subitems"]:
                u = mcourses.Units(subitem["id"])
                if u.getDetail("courseid") != id:
                    return "invalid"
                u.setDetail("unit_order", subitem["order"])
                u.setDetail("parent", item["id"])
        return "ok"
    else:
        if course.getLabel() != label:
            return redirect(url_for("course_unit_reorder", id=id, label=course.getLabel()))
        return render_template('courses/edit/reorder.html', title="Kursmodule neu anordnen: " + course.getTitle(), thispage="courses", data=course)

def apply(app):
    app.route("/courses")(courses_index)
    app.route("/course/propose", methods=["GET", "POST"])(courses_propose)
    app.route("/c/search")(app.route("/course/search")(courses_search))
    app.route("/c/<int:id>")(app.route("/c/<int:id>/info")(app.route("/course/<int:id>/<label>/details")(app.route("/course/<int:id>/<label>")(course_info))))
    app.route("/c/<int:id>/proposal")(app.route("/course/<int:id>/<label>/proposal")(course_related_proposal))
    app.route("/c/<int:id>/admin", methods=["GET", "POST"])(app.route("/course/<int:id>/<label>/admin", methods=["GET", "POST"])(app.route("/course/<int:id>/<label>/admin/<page>", methods=["GET", "POST"])(course_admin)))
    app.route("/c/<int:id>/enroll")(app.route("/course/<int:id>/<label>/enroll")(course_enroll))
    app.route("/c/<int:id>/start")(app.route("/course/<int:id>/<label>/start")(course_start))
    app.route("/c/<int:course_id>/<int:unit_id>", methods=["GET", "POST"])(app.route("/c/<int:course_id>/u/<int:unit_id>", methods=["GET", "POST"])(app.route("/course/<int:course_id>/<course_label>/unit/<int:unit_id>/<unit_label>/show", methods=["GET", "POST"])(unit_show)))
    app.route("/c/<int:id>/edit", methods=["GET", "POST"])(app.route("/course/<int:id>/<label>/edit", methods=["GET", "POST"])(course_edit_overview))
    app.route("/c/<int:course_id>/edit/unit/<int:unit_id>", methods=["GET", "POST"])(app.route("/course/<int:course_id>/<course_label>/edit/unit/<int:unit_id>/<unit_label>", methods=["GET", "POST"])(unit_edit))
    app.route("/c/<int:course_id>/u/<int:unit_id>/submit", methods=["POST"])(app.route("/course/<int:course_id>/<course_label>/unit/<int:unit_id>/<unit_label>/submit", methods=["POST"])(unit_submit))
    app.route("/c/<int:course_id>/edit/add", methods=["POST"])(app.route("/course/<int:course_id>/<course_label>/edit/add", methods=["POST"])(unit_new))
    app.route("/topics")(topic_index)
    app.route("/t/<name>")(app.route("/topic/<name>")(topic_view))
    app.route("/t/<name>/edit", methods=["GET", "POST"])(app.route("/topic/<name>/edit", methods=["GET", "POST"])(topic_edit))
    app.route("/c/<int:id>/edit/reorder", methods=["GET", "POST"])(app.route("/course/<int:id>/<label>/edit/reorder", methods=["GET", "POST"])(course_unit_reorder))
