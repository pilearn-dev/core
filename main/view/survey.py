# coding: utf-8
from flask import request, session, redirect, url_for, abort, render_template, jsonify
from model import user as muser, forum as mforum, survey as msurvey, courses as mcourses
from sha1 import sha1
import json

def survey_show(id, label=None):
    if msurvey.Survey.exists(id):
        survey = msurvey.Survey(id)
        forum = mforum.Forum(survey.getDetail("associated_forum"))
        if label != survey.getLabel():
            return redirect(url_for("survey_show", id=id, label=survey.getLabel()))
        else:
            return render_template("survey/direct.html", title="Umfrage - " + survey.getTitle(), survey=survey, forum=forum)
    else:
        abort(404)

def survey_edit(id, label=None):
    cuser = muser.getCurrentUser()
    if msurvey.Survey.exists(id):
        survey = msurvey.Survey(id)
        forum = mforum.Forum(survey.getDetail("associated_forum"))
        if not(cuser.isDev() or survey.getDetail("survey_owner") == cuser.id) or cuser.isDisabled():
            if survey.getDetail("associated_forum") == 0:
                abort(404)
            else:
                cou = mcourses.Courses(forum.id)
                if not cou.getCourseRole(cuser) > 3 or cuser.isDIsabled():
                    abort(404)
        if request.method == "GET":
            if label != survey.getLabel():
                return redirect(url_for("survey_edit", id=id, label=survey.getLabel()))
            else:
                return render_template("survey/edit.html", title="Umfrage bearbeiten - " + survey.getTitle(), survey=survey, forum=forum)
        elif request.method == "POST":
            survey.setDetail("content", request.json["content"])
            survey.setDetail("title", request.json["title"])
            survey.setDetail("state", request.json["state"])
            return "ok"
    else:
        abort(404)

def survey_submit(id, label=None):
    cuser = muser.getCurrentUser()
    if not cuser.isLoggedIn() or cuser.isDisabled(): abort(403)
    if msurvey.Survey.exists(id):
        survey = msurvey.Survey(id)
        forum = mforum.Forum(survey.getDetail("associated_forum"))
        if not survey.hasSubmission(cuser):
            survey.addSubmission(cuser, json.dumps(request.json))
        return "ok"
    else:
        abort(404)

def survey_results(id, label=None):
    cuser = muser.getCurrentUser()
    if msurvey.Survey.exists(id):
        survey = msurvey.Survey(id)
        forum = mforum.Forum(survey.getDetail("associated_forum"))
        if not(cuser.isDev() or survey.getDetail("survey_owner") == cuser.id):
            if survey.getDetail("associated_forum") == 0:
                abort(404)
            else:
                cou = mcourses.Courses(forum.id)
                if not cou.getCourseRole(cuser) > 3:
                    abort(404)
        if request.method == "GET":
            if label != survey.getLabel():
                return redirect(url_for("survey_results", id=id, label=survey.getLabel()))
            else:
                return render_template("survey/results_direct.html", title="Umfrageergebnisse - " + survey.getTitle(), survey=survey, forum=forum, int=int, len=len)
        elif request.method == "POST":
            RESULT = {}
            con = survey.getContent()
            i = 1
            for c in con:
                if c["type"] == "text-answer":
                    RESULT[i] = {"question": c["data"]["question"],"data":[], "type":"text-answer"}
                if c["type"] == "multiple-choice":
                    selc = len(c["data"]["choices"])
                    RESULT[i] = {"question": c["data"]["question"],"data":["0" for _ in range(selc)], "type":"multiple-choice", "choices": c["data"]["choices"]}
                i += 1
            subm = survey.getSubmissions()
            for s in subm:
                s = json.loads(s[0])
                for field, value in list(s.items()):
                    r = RESULT[int(field)]
                    if r["type"] == "text-answer":
                        if value:
                            r["data"].append(value)
                    elif r["type"] == "multiple-choice":
                        r["data"][int(value)] += str(int(r["data"][int(value)-1]) + 1)
            survey.setDetail("results", json.dumps(RESULT))
            return "done"
    else:
        abort(404)

def apply(app):
    app.route('/sv/<int:id>/show', methods=["GET", "POST"])(app.route('/survey/<int:id>/<label>/show', methods=["GET", "POST"])(survey_show))
    app.route('/sv/<int:id>/edit', methods=["GET", "POST"])(app.route('/survey/<int:id>/<label>/edit', methods=["GET", "POST"])(survey_edit))
    app.route('/sv/<int:id>/results', methods=["GET", "POST"])(app.route('/survey/<int:id>/<label>/results', methods=["GET", "POST"])(survey_results))
    app.route('/sv/<int:id>/submit', methods=["POST"])(app.route('/survey/<int:id>/<label>/submit', methods=["POST"])(survey_submit))
