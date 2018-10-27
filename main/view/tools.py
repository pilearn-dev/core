# coding: utf-8
from flask import request, session, redirect, url_for, abort, render_template, jsonify
from model import user as muser, courses as mcourses, reviews as mreviews, forum as mforum
import time

def tools_info():
    cuser = muser.getCurrentUser()
    if not cuser.isMod():
        abort(404)
    return render_template("tools/info.html", title="Werkzeuge", thispage="tools")

def tools_courses_latest():
    cuser = muser.getCurrentUser()
    if not cuser.isAdmin():
        abort(404)
    num = int(request.values.get("num", 5))
    if num not in [5, 10, 15, 20, 25]:
        num = 5
    n = mcourses.Courses.queryNum("1=1", [])
    courses = mcourses.Courses.query("1=1", [], n-num, n)
    return render_template("tools/courses_latest.html", title="Werkzeuge - neuste Kurse", thispage="tools", courses=courses, num=num)

def tools_courses_proposalsearch():
    cuser = muser.getCurrentUser()
    if not cuser.isAdmin():
        abort(404)
    return render_template("tools/proposal_search.html", title="Werkzeuge - Vorschlagsuche", thispage="tools", num=5, page=max(0, min(10, int(request.values.get("page", "1")))), pages=10, topic=mcourses.Topic)


def tools_user_flags_index():
    cuser = muser.getCurrentUser()
    if not cuser.isAdmin():
        abort(404)

    flagged = mreviews.CustomQueue.getItems(["user"])
    def _prepare(d):
        d = dict(d)
        d["user"] = muser.User.from_id(d["item_id"])
        return d

    flagged = map(_prepare, flagged)

    return render_template("tools/user_flag_list.html", title="Werkzeuge - Benutzermeldungen", thispage="tools", flagged=flagged)

def tools_user_flags_item(id):
    cuser = muser.getCurrentUser()
    if not cuser.isAdmin():
        abort(404)

    flagged = mreviews.CustomQueue.getItemData(id)
    flagged = dict(flagged)
    flagged["user"] = muser.User.from_id(flagged["item_id"])

    if not flagged or flagged["item_type"] != "user":
        abort(404)

    flags=mreviews.CustomQueue.getItemFlags(id)
    def _prepare(d):
        d = dict(d)
        d["flagger"] = muser.User.from_id(d["flagger_id"])
        return d

    flags = map(_prepare, flags)

    has_open_flags = mreviews.CustomQueue.getItemOpenFlagsCount(id) != 0

    return render_template("tools/user_flag_item.html", title="Werkzeuge - Benutzermeldungen", thispage="tools", item=flagged, flags=flags, has_open_flags=has_open_flags)

def tools_user_flags_action(id):
    cuser = muser.getCurrentUser()
    if not cuser.isAdmin():
        abort(404)

    flagged = mreviews.CustomQueue.getItemData(id)
    flagged = dict(flagged)
    flagged["user"] = muser.User.from_id(flagged["item_id"])

    if not flagged or flagged["item_type"] != "user":
        abort(404)

    if flagged["state"] == 0:
        flags = request.json["flags"]
        for f in flags:
            mreviews.CustomQueue.manageFlag(id, f, request.json["result"], request.json["response"])
        if mreviews.CustomQueue.getItemOpenFlagsCount(id) == 0:
            return "{ok:last}"
        return "{ok}"
    return "{ok:last}"

def tools_user_flags_finish(id):
    cuser = muser.getCurrentUser()
    if not cuser.isAdmin():
        abort(404)

    flagged = mreviews.CustomQueue.getItemData(id)
    flagged = dict(flagged)
    flagged["user"] = muser.User.from_id(flagged["item_id"])

    if not flagged or flagged["item_type"] != "user":
        abort(404)

    if flagged["state"] == 0:
        mreviews.CustomQueue.completeReview(id)
    return "{ok}"




def tools_forum_flags_index():
    cuser = muser.getCurrentUser()
    if not cuser.isAdmin():
        abort(404)

    flagged = mreviews.CustomQueue.getItems(["forum.question", "forum.answer"])
    def _prepare(d):
        d = dict(d)
        if d["item_type"] == "forum.question":
          d["post"] = mforum.Article(d["item_id"])
        elif d["item_type"] == "forum.answer":
          d["post"] = mforum.Answer(d["item_id"])
        return d

    flagged = map(_prepare, flagged)

    return render_template("tools/forum_flag_list.html", title="Werkzeuge - Beitragsmeldungen", thispage="tools", flagged=flagged)



def tools_forum_flags_item(id):
    cuser = muser.getCurrentUser()
    if not cuser.isAdmin():
        abort(404)

    flagged = mreviews.CustomQueue.getItemData(id)
    flagged = dict(flagged)

    if not flagged or (flagged["item_type"] != "forum.question" and flagged["item_type"] != "forum.answer"):
      abort(404)

    if flagged["item_type"] == "forum.question":
      flagged["post"] = mforum.Article(flagged["item_id"])
    elif flagged["item_type"] == "forum.answer":
      flagged["post"] = mforum.Answer(flagged["item_id"])


    flags=mreviews.CustomQueue.getItemFlags(id)
    def _prepare(d):
        d = dict(d)
        d["flagger"] = muser.User.from_id(d["flagger_id"])
        return d

    flags = map(_prepare, flags)

    has_open_flags = mreviews.CustomQueue.getItemOpenFlagsCount(id) != 0

    return render_template("tools/forum_flag_item.html", title="Werkzeuge - Beitragsmeldungen", thispage="tools", item=flagged, flags=flags, has_open_flags=has_open_flags)

def tools_forum_flags_action(id):
    cuser = muser.getCurrentUser()
    if not cuser.isAdmin():
        abort(404)

    flagged = mreviews.CustomQueue.getItemData(id)
    flagged = dict(flagged)

    if not flagged or (flagged["item_type"] != "forum.question" and flagged["item_type"] != "forum.answer"):
      abort(404)

    if flagged["item_type"] == "forum.question":
      flagged["post"] = mforum.Article(flagged["item_id"])
    elif flagged["item_type"] == "forum.answer":
      flagged["post"] = mforum.Answer(flagged["item_id"])


    if flagged["state"] == 0:
        flags = request.json["flags"]
        for f in flags:
            mreviews.CustomQueue.manageFlag(id, f, request.json["result"], request.json["response"])
        if mreviews.CustomQueue.getItemOpenFlagsCount(id) == 0:
            return "{ok:last}"
        return "{ok}"
    return "{ok:last}"

def tools_forum_flags_finish(id):
    cuser = muser.getCurrentUser()
    if not cuser.isAdmin():
        abort(404)

    flagged = mreviews.CustomQueue.getItemData(id)
    flagged = dict(flagged)

    if not flagged or (flagged["item_type"] != "forum.question" and flagged["item_type"] != "forum.answer"):
      abort(404)

    if flagged["item_type"] == "forum.question":
      flagged["post"] = mforum.Article(flagged["item_id"])
    elif flagged["item_type"] == "forum.answer":
      flagged["post"] = mforum.Answer(flagged["item_id"])

    if flagged["state"] == 0:
        mreviews.CustomQueue.completeReview(id)
    return "{ok}"


def tools_user_ops_index(uid):
    cuser = muser.getCurrentUser()
    if not cuser.isAdmin():
        abort(404)
    if not muser.User.exists(uid):
        abort(404)
    data = muser.User.from_id(uid)
    action = request.values.get("action", "init")
    if action == "init":
        return render_template("tools/user_ops.html", title="Werkzeuge - Benutzerfunktionen", thispage="tools", data=data)
    elif action == "lookup-annotations":
        return render_template("tools/user_ops_lookup-annotation.html", title="Werkzeuge - Benutzerfunktionen", thispage="tools", data=data)
    elif action == "add-annotation":
        return render_template("tools/user_ops_add-annotation.html", title="Werkzeuge - Benutzerfunktionen", thispage="tools", data=data)
    elif action == "merge":
        if request.method == "POST":
            mid = str(request.json["otherid"])
            if int(mid) == 0:
                data.setDetail("mergeto", None)
                data.setDetail("deleted", 0)
                data.addAnnotation("merge", "Un-Merge - " + request.json["reason"], cuser, time.time())
                return render_template("tools/user_ops_merge.html", title="Werkzeuge - Benutzerfunktionen", thispage="tools", data=data)
            elif muser.User.exists(mid):
                to = muser.User.from_id(mid)
                if to.getDetail("mergeto") or data.isMod() or data.isTeam():
                    return render_template("tools/user_ops_merge.html", title="Werkzeuge - Benutzerfunktionen", thispage="tools", data=data, error=1)
            else:
                return render_template("tools/user_ops_merge.html", title="Werkzeuge - Benutzerfunktionen", thispage="tools", data=data, error=1)
            data.setDetail("mergeto", mid)
            data.setDetail("deleted", 1)
            data.addAnnotation("merge", "Master: [#" +mid+"](/u/"+mid+") - " + request.json["reason"], cuser, time.time())
            pass
        else:
            return render_template("tools/user_ops_merge.html", title="Werkzeuge - Benutzerfunktionen", thispage="tools", data=data)
    elif action == "access-pii":
        show_data = False
        if request.method == "POST":
            if request.form["reason"] and len(request.form["reason"]) > 15:
                data.addAnnotation("accessdata", request.form["reason"], cuser, time.time())
                show_data = True
        return render_template("tools/user_ops_access-pii.html", title="Werkzeuge - Benutzerfunktionen", thispage="tools", data=data, show_data=show_data)
    elif action == "ban":
        return render_template("tools/user_ops_ban.html", title="Werkzeuge - Benutzerfunktionen", thispage="tools", data=data)
    return redirect(url_for("tools_user_ops_index", uid=uid))

def apply(app):
    app.route("/tools")(tools_info)
    app.route("/tools/courses/latest")(tools_courses_latest)
    app.route("/tools/courses/proposal-search")(tools_courses_proposalsearch)
    app.route("/tools/user/flags", methods=["GET", "POST"])(tools_user_flags_index)
    app.route("/tools/user/flags/<int:id>", methods=["GET", "POST"])(tools_user_flags_item)
    app.route("/tools/user/flags/<int:id>/validate", methods=["POST"])(tools_user_flags_action)
    app.route("/tools/user/flags/<int:id>/finish", methods=["POST"])(tools_user_flags_finish)
    app.route("/tools/user/ops/<uid>", methods=["GET", "POST"])(tools_user_ops_index)

    app.route("/tools/forum/flags", methods=["GET", "POST"])(tools_forum_flags_index)
    app.route("/tools/forum/flags/<int:id>", methods=["GET", "POST"])(tools_forum_flags_item)
    app.route("/tools/forum/flags/<int:id>/validate", methods=["POST"])(tools_forum_flags_action)
    app.route("/tools/forum/flags/<int:id>/finish", methods=["POST"])(tools_forum_flags_finish)
