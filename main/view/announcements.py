# coding: utf-8
from flask import Blueprint, request, session, redirect, url_for, abort, render_template, jsonify
from model import user as muser, forum as mforum, courses as mcourses
from controller import num as cnum, times as ctimes

import json, time, datetime

announcements = Blueprint('announcements', __name__)

@announcements.before_request
def announcements_precondition():
    forum_id = request.view_args["forum_id"]
    cuser = muser.getCurrentUser()
    if not mforum.Forum.exists(forum_id):
        abort(404)
    if not cuser.isLoggedIn() or cuser.isDisabled(): abort(403)
    f = mforum.Forum(forum_id)
    if f.id == 0:
        if not cuser.isMod():
            abort(403)
    else:
        c = mcourses.Courses(f.id)
        if not (c.getCourseRole(cuser) or cuser.isMod()):
            abort(403)

@announcements.route("/")
def index(forum_id):
    f = mforum.Forum(forum_id)
    return render_template("announcements/list.html", title=u"Ankündigungen", forum=f, announcements=mforum.ForumAnnouncement.byForum(f.id, True))

@announcements.route("/add", methods=["GET", "POST"])
def add(forum_id):
    cuser = muser.getCurrentUser()
    if not mforum.Forum.exists(forum_id):
        abort(404)
    if not cuser.isLoggedIn() or cuser.isDisabled(): abort(403)
    f = mforum.Forum(forum_id)
    if f.id == 0:
        if not cuser.isMod():
            abort(403)
    else:
        c = mcourses.Courses(f.id)
        if not (c.getCourseRole(cuser) or cuser.isMod()):
            abort(403)
    if request.method == "POST":
        dc = lambda d: (datetime.datetime.strptime(d, "%Y-%m-%d") - datetime.datetime(1970,1,1)).total_seconds()
        link=request.form["link"]
        title=request.form["title"]
        event_from=dc(request.form["event_from"])
        if not request.form.has_key("event_until"):
            event_until=None
        else:
            event_until=dc(request.form["event_until"]) if request.form["event_until"] else None
        show_from=dc(request.form["shown_from"])
        show_until=dc(request.form["shown_until"])
        announcement = mforum.ForumAnnouncement.createNew(f.id,title,link,show_from,show_until,event_from,event_until)
        if cuser.isDev() and f.id == 0:
            is_featured_banner = request.form.has_key("is_featured_banner")
            if is_featured_banner:
                announcement.setDetail("is_featured_banner", True)
        return redirect(url_for("announcements.index", forum_id=f.id))
    else:
        return render_template("announcements/add.html", title=u"Ankündigungen", forum=f)

@announcements.route("/edit/<int:announcement_id>", methods=["GET", "POST"])
def announcements_edit(forum_id, announcement_id):
    cuser = muser.getCurrentUser()
    if not mforum.Forum.exists(forum_id):
        abort(404)
    if not cuser.isLoggedIn() or cuser.isDisabled(): abort(403)
    f = mforum.Forum(forum_id)
    if f.id == 0:
        if not cuser.isMod():
            abort(403)
    else:
        c = mcourses.Courses(f.id)
        if not (c.getCourseRole(cuser) or cuser.isMod()):
            abort(403)
    if not mforum.ForumAnnouncement.exists(announcement_id):
        abort(404)

    an = mforum.ForumAnnouncement(announcement_id)
    if an.getDetail("forum") != f.id:
        abort(404)

    if request.method == "POST":
        dc = lambda d: (datetime.datetime.strptime(d, "%Y-%m-%d") - datetime.datetime(1970,1,1)).total_seconds()
        link=request.form["link"]
        title=request.form["title"]
        event_from=dc(request.form["event_from"])
        if not request.form.has_key("event_until"):
            event_until=None
        else:
            event_until=dc(request.form["event_until"]) if request.form["event_until"] else None
        show_from=dc(request.form["shown_from"])
        show_until=dc(request.form["shown_until"])

        an.setDetail("link",link)
        an.setDetail("title",title)
        an.setDetail("start_date",event_from)
        an.setDetail("end_date",event_until)
        an.setDetail("show_from",show_from)
        an.setDetail("show_until",show_until)

        if cuser.isDev() and f.id == 0:
            is_featured_banner = request.form.has_key("is_featured_banner")
            if is_featured_banner:
                an.setDetail("is_featured_banner", True)
            else:
                an.setDetail("is_featured_banner", False)

        return redirect(url_for("announcements.index", forum_id=f.id))
    else:
        return render_template("announcements/edit.html", title=u"Ankündigungen", forum=f, a=an)
