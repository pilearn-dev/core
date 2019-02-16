# coding: utf-8
from flask import render_template, abort, request, redirect, url_for
from model import user as muser, modmsg as mmodmsg

def msg_view_single(user, thread_id):
    cuser = muser.getCurrentUser()
    if not mmodmsg.UserMsgThread.exists(thread_id):
        abort(404)
    thread = mmodmsg.UserMsgThread(thread_id)
    if thread.getDetail("contacted_user") != int(user) or (not cuser.isAdmin() and thread.getDetail("contacted_user") != cuser.id):
        abort(404)
    if request.values.get("mod", False) and cuser.isAdmin():
        return render_template('modmsg/view_single_mod.html', title=u"[mod] Nachrichtenverlauf", thispage="users", thread=thread)

    return render_template('modmsg/view_single.html', title=u"Nachrichtenverlauf", thispage="users", thread=thread)

def msg_add_response(user, thread_id):
    cuser = muser.getCurrentUser()
    if not mmodmsg.UserMsgThread.exists(thread_id):
        abort(404)
    thread = mmodmsg.UserMsgThread(thread_id)
    if thread.getDetail("contacted_user") != int(user) or (not cuser.isAdmin() and thread.getDetail("contacted_user") != cuser.id):
        abort(404)

    msgs = thread.getMessages()

    if msgs[-1].getDetail("submitted_by") == cuser.id and not cuser.isAdmin():
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

def apply(app):
    app.route("/user-message/<int:user>/thread/<int:thread_id>")(msg_view_single)
    app.route("/user-message/<int:user>/thread/<int:thread_id>/add-response", methods=["POST"])(msg_add_response)
