# coding: utf-8
from flask import render_template, abort, request, redirect, url_for, jsonify
from model import user as muser, modmsg as mmodmsg
from controller import times as ctimes

import time

def msg_new_thread(user):
    cuser = muser.getCurrentUser()
    if not cuser.isMod():
        abort(404)

    u = muser.User.from_id(user)

    if request.method == "GET":
        tpl = mmodmsg.getTemplates()

        return render_template('modmsg/new-thread.html', title=u"Benutzer kontaktieren", thispage="user", u=u, templates=tpl)
    elif request.method == "POST":
        try:
            template, message, suspend, suspension_reason, suspension_length = \
            int(request.json["template"]), request.json["message"], request.json["suspend"], \
            request.json["suspension_reason"], request.json["suspension_length"]

            if suspend:
                suspension_length = int(suspension_length)

            if suspend and suspension_length > 365:
                return "javascript:alert('Nur das Team kann Benutzer für mehr als ein Jahr sperren. Kontaktieren Sie uns über das Helpdesk.')"

            prefix = "Hallo " + u.getDetail("realname") + ",\n\n"
            suffix = ""
            postfix = u"\n\nViele Grüße,\n\n&pi;-Learn Moderatorenteam"

            if suspend:
                suffix = u"\n\nUm weiteres Verhalten dieser Art zu verhindern, haben wir beschlossen, dein Konto für " + str(suspension_length) + u" Tage zu suspendieren. Während dieser Zeit wird ein Hinweis auf deinem Profil angezeigt und du wirst dich nicht anmelden können. Anschließend bist du aber ohne Einschränkungen wieder willkommen, solange du dich an die Regeln hältst."

            message = prefix + message + suffix + postfix

            thread = mmodmsg.UserMsgThread.new(cuser.id, u.id)
            URL = url_for("msg_view_single", user=u.id, thread_id=thread.id)

            mmodmsg.UserMsg.new(thread.id, cuser.id, u.id, message, template=template)
            if template != 0:
                t = mmodmsg.getTemplateById(template)
                tt = t["title"]
                u.notify("pm", "Ein Moderator hat dich wegen '" + tt + "' privat kontaktiert. Bitte beachte seine Nachricht!", URL)
                u.addAnnotation("message", "["+tt+"]("+URL+")", cuser, time.time())
            else:
                u.notify("pm", "Ein Moderator hat dich privat kontaktiert. Bitte beachte seine Nachricht!", URL)
                u.addAnnotation("message", "[anderes]("+URL+")", cuser, time.time())

            if suspend:
                u.setDetail("banned", 1)
                u.setDetail("ban_reason", suspension_reason)
                ban_end = int(time.time()) + 5 + 60 * 60 * 24 * int(suspension_length)
                u.setDetail("ban_end", ban_end)

                u.addAnnotation("ban", "**Sperrung** " + suspension_reason + u" für " + str(suspension_length) + "d", cuser, time.time())

            return URL
        except Exception as e:
            print(e)
            return "javascript:alert(\"" + repr(e) + "\")"

def msg_tpl_data(tpid):
    cuser = muser.getCurrentUser()
    if not cuser.isMod():
        abort(404)

    tpl = mmodmsg.getTemplateById(tpid)

    return jsonify(tpl)

def msg_view_single(user, thread_id):
    cuser = muser.getCurrentUser()
    if not mmodmsg.UserMsgThread.exists(thread_id):
        abort(404)
    thread = mmodmsg.UserMsgThread(thread_id)
    if thread.getDetail("contacted_user") != int(user) or (not cuser.isMod() and thread.getDetail("contacted_user") != cuser.id):
        abort(404)
    if request.values.get("mod", False) and cuser.isMod():
        return render_template('modmsg/view_single_mod.html', title=u"[mod] Nachrichtenverlauf", thispage="user", thread=thread)

    return render_template('modmsg/view_single.html', title=u"Nachrichtenverlauf", thispage="user", thread=thread)

def msg_add_response(user, thread_id):
    cuser = muser.getCurrentUser()
    if not mmodmsg.UserMsgThread.exists(thread_id):
        abort(404)
    thread = mmodmsg.UserMsgThread(thread_id)
    if thread.getDetail("contacted_user") != int(user) or (not cuser.isMod() and thread.getDetail("contacted_user") != cuser.id):
        abort(404)

    msgs = thread.getMessages()

    if msgs[-1].getDetail("submitted_by") == cuser.id and not cuser.isMod():
        abort(403)

    URL = url_for("msg_view_single", user=user, thread_id=thread_id)

    if cuser.id == thread.getDetail("contacted_user"):
        mmodmsg.UserMsg.new(thread.id, cuser.id, 0, request.form["response"])
        cu = thread.getInitiator()
        cu.notify("pm", "Neue Antwort zu privater Nachricht von " + cuser.getDetail("realname"), URL)
    else:
        mmodmsg.UserMsg.new(thread.id, cuser.id, thread.getDetail("contacted_user"), request.form["response"])
        cu = thread.getContacted()
        cu.notify("pm", "Neue Antwort zu privater Nachricht", URL)

    return redirect(URL)

def msg_close_or_reopen(user, thread_id):
    cuser = muser.getCurrentUser()
    if not mmodmsg.UserMsgThread.exists(thread_id):
        abort(404)
    thread = mmodmsg.UserMsgThread(thread_id)
    if thread.getDetail("contacted_user") != int(user):
        abort(404)

    if not cuser.isMod():
        abort(403)

    if not thread.isClosed():
        thread.setDetail("closed", 1)
    else:
        thread.setDetail("closed", 0)

    return jsonify({"result":"ok"})

def apply(app):
    app.route("/user-message/template-data/<int:tpid>", methods=["GET", "POST"])(msg_tpl_data)
    app.route("/user-message/<int:user>/new-thread", methods=["GET", "POST"])(msg_new_thread)
    app.route("/user-message/<int:user>/thread/<int:thread_id>")(msg_view_single)
    app.route("/user-message/<int:user>/thread/<int:thread_id>/add-response", methods=["POST"])(msg_add_response)
    app.route("/user-message/<int:user>/thread/<int:thread_id>/close-or-reopen", methods=["POST"])(msg_close_or_reopen)
