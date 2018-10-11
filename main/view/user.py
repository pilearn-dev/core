# coding: utf-8
from flask import request, session, redirect, url_for, abort, render_template, jsonify
from model import privileges as mprivileges, tags as mtags, user as muser, reviews as mreviews, forum as mforum, post_templates as mposttemplates
from controller import num as cnum, times as ctimes
import helpdesk.model as hm

import markdown as md

from sha1 import sha1
import json, time

def user_page(id, name=None):
    try:
        id = int(id)
    except:
        abort(404)
    if muser.User.exists(id):
        user = muser.User.from_id(id)
        cuser = muser.getCurrentUser()
        mt = user.getDetail("mergeto")
        if mt and not cuser.isAdmin():
            return redirect(url_for("user_page", id=mt))
        if user.isDeleted():
            if not cuser.isAdmin():
                abort(404)
            else:
                return redirect(url_for("user_deleted_page", id=id))

        if name != user.getDetail("name"):
            return redirect(url_for("user_page", id=id, name=user.getDetail("name")))
        else:
            temp = None
            return render_template("user/view.html", data=user, thispage="user", title="Benutzer " + user.getHTMLName(False), post_templates=temp)
    else:
        abort(404)

def user_flags_page(id, name=None):
    try:
        id = int(id)
    except:
        abort(404)
    if muser.User.exists(id):
        user = muser.User.from_id(id)
        cuser = muser.getCurrentUser()
        mt = user.getDetail("mergeto")
        if mt and not cuser.isAdmin():
            return redirect(url_for("user_page", id=mt))
        if user.isDeleted():
            if not cuser.isAdmin():
                abort(404)
            else:
                return redirect(url_for("user_deleted_page", id=id))

        if name != user.getDetail("name"):
            return redirect(url_for("user_flags_page", id=id, name=user.getDetail("name")))
        else:
            closure_filter = request.values.get("closure", "all")
            closure_data = mreviews.PostClosure.getFromUser(user)
            cd = []
            closure_helpful = closure_pending = closure_declined = closure_total = 0
            for row in closure_data:
                closure_total += 1
                if row["state"] == 0:
                    closure_pending += 1
                    if closure_filter not in ["all", "pending"]:
                        continue
                elif row["state"] > 0:
                    closure_helpful += 1
                    if closure_filter not in ["all", "helpful"]:
                        continue
                elif row["state"] == -2:
                    closure_declined += 1
                    if closure_filter not in ["all", "declined"]:
                        continue
                row["item"] = mforum.Article(row["item_id"])
                cd.append(row)
            post_deletion_filter = request.values.get("post_deletion", "all")
            post_deletion_data = mreviews.PostDeletion.getFromUser(user)
            pdd = []
            post_deletion_helpful = post_deletion_pending = post_deletion_declined = post_deletion_total = 0
            for row in post_deletion_data:
                post_deletion_total += 1
                if row["state"] == 0:
                    post_deletion_pending += 1
                    if post_deletion_filter not in ["all", "pending"]:
                        continue
                elif row["state"] > 0:
                    post_deletion_helpful += 1
                    if post_deletion_filter not in ["all", "helpful"]:
                        continue
                elif row["state"] == -2:
                    post_deletion_declined += 1
                    if post_deletion_filter not in ["all", "declined"]:
                        continue
                row["item"] = mforum.Article(row["item_id"])
                pdd.append(row)
            custom_filter = request.values.get("custom", "all")
            custom_data = mreviews.CustomQueue.getFromUser(user)
            customd = []
            custom_helpful = custom_pending = custom_declined = custom_total = 0
            for row in custom_data:
              custom_total += 1
              if row["state"] == 0:
                  custom_pending += 1
                  if custom_filter not in ["all", "pending"]:
                      continue
              elif row["state"] > 0:
                  custom_helpful += 1
                  if custom_filter not in ["all", "helpful"]:
                      continue
              elif row["state"] == -2:
                  custom_declined += 1
                  if custom_filter not in ["all", "declined"]:
                      continue
              if row["item_type"] == "forum.question":
                row["item"] = mforum.Article(row["item_id"])
              elif row["item_type"] == "forum.answer":
                row["item"] = mforum.Answer(row["item_id"])
              elif row["item_type"] == "user":
                row["item"] = muser.User.from_id(row["item_id"])
              customd.append(row)
            return render_template("user/flags.html", data=user, closure_flags=cd, post_deletion_flags=pdd, custom_flags=customd, thispage="user", title="Meldungen von " + user.getHTMLName(False), closure_helpful=closure_helpful, closure_pending=closure_pending, closure_declined=closure_declined, closure_total=closure_total, post_deletion_helpful=post_deletion_helpful, post_deletion_pending=post_deletion_pending, post_deletion_declined=post_deletion_declined, post_deletion_total=post_deletion_total, custom_helpful=custom_helpful, custom_pending=custom_pending, custom_declined=custom_declined, custom_total=custom_total)
    else:
        abort(404)

def user_rep_page(id, name=None):
    try:
        id = int(id)
    except:
        abort(404)
    if muser.User.exists(id):
        user = muser.User.from_id(id)
        cuser = muser.getCurrentUser()
        mt = user.getDetail("mergeto")
        if mt and not cuser.isAdmin():
            return redirect(url_for("user_page", id=mt))
        if user.isDeleted():
            if not cuser.isAdmin():
                abort(404)
            else:
                return redirect(url_for("user_deleted_page", id=id))

        if name != user.getDetail("name"):
            return redirect(url_for("user_rep_page", id=id, name=user.getDetail("name")))
        else:
            return render_template("user/reputation.html", data=user, thispage="user", title="Reputation von " + user.getHTMLName(False))
    else:
        abort(404)

def user_del_page(id, name=None):
    try:
        id = int(id)
    except:
        abort(404)
    if muser.User.exists(id):
        user = muser.User.from_id(id)
        cuser = muser.getCurrentUser()
        mt = user.getDetail("mergeto")
        if mt and not cuser.isAdmin():
            return redirect(url_for("user_page", id=mt))
        if user.isDeleted():
            if not cuser.isAdmin():
                abort(404)
            else:
                return redirect(url_for("user_deleted_page", id=id))

        if not cuser.isAdmin() and cuser.id != id:
            abort(404)
        if name != user.getDetail("name"):
            return redirect(url_for("user_del_page", id=id, name=user.getDetail("name")))
        else:
            return render_template("user/delete.html", data=user, thispage="user", title=u"Benutzer löschen: " + user.getHTMLName(False), current_time=time.time())
    else:
        abort(404)


def flag_user(id):
    try:
        id = int(id)
    except:
        return "Ungültige Anfrage. Bitte im globalen Forum melden!"
    data = request.json
    cuser = muser.getCurrentUser()
    if muser.User.exists(id):
        user = muser.User.from_id(id)
        if not user.isDeleted():
            if user.isTeam():
                return "Team-Mitglieder können nicht gemeldet werden."
            if data["type"] == "flag":
                if cuser.may("general_reportUser") or cuser.id == user.id:
                    reason, message = data["reason"], data["message"]
                    rL = {
                        "disturb": u"störendes Verhalten",
                        "spam": u"SPAM",
                        "offensive": u"Beleidigung",
                        "other": u"Supportanfrage",
                        "rulebreak": u"Regelverletzung"
                    }
                    reason = "**" + rL[reason] + "**: "
                    data = reason + message
                    x = user.customflag(data, cuser)
                    if x:
                        return "{ok}"
                    else:
                        return "Ein Fehler ist aufgetreten."
                else:
                    return "Dir fehlt etwas Reputation, um Nutzer zu melden."
            elif data["type"] == "ban":
                if cuser.isAdmin():
                    user.setDetail("banned", 1)
                    user.setDetail("ban_reason", data["reason"])
                    if not cuser.isTeam() and data["duration"] > 24 * 365:
                        return "Nur das Team kann Benutzer für mehr als ein Jahr sperren. Kontaktieren Sie uns über das Helpdesk."
                    ban_end = int(time.time()) + 5 + 60 * 60 * int(data["duration"])
                    user.setDetail("ban_end", ban_end)

                    user.addAnnotation("ban", "**Sperrung** wegen " + user.BAN_REASON[data["reason"]] + u" für " + ctimes.duration2text(60 * 60 * int(data["duration"])), cuser, time.time())
                    return "{ok}"
                else:
                    return "Nur Administratoren dürfen dies."
            elif data["type"] == "unban":
                if cuser.isAdmin():
                    user.setDetail("banned", 0)
                    user.setDetail("ban_reason", "")
                    user.setDetail("ban_end", 0)
                    user.addAnnotation("unban", "manual", cuser, time.time())
                    return "{ok}"
                else:
                    return "Nur Administratoren dürfen dies."

        else:
            return "Der Benutzer wurde nicht gefunden. Vielleicht wurde er bereits gelöscht."
    else:
        return "Der Benutzer wurde nicht gefunden. Vielleicht wurde er bereits gelöscht."


def delete_user(id):
    try:
        id = int(id)
    except:
        return "Ungültige Anfrage. Bitte im globalen Forum melden!"
    data = request.json
    cuser = muser.getCurrentUser()
    if muser.User.exists(id):
        user = muser.User.from_id(id)
        if not user.isDeleted():
            if user.isMod() or user.isTeam():
                return "Benutzer mit Rollen können nicht gelöscht werden."
            if cuser.isAdmin() and data["type"] == "admin.delete":
                user.setDetail("deleted", 1)
                user.addAnnotation("delete", u"Benutzerkonto wurde durch Administrator gelöscht.", cuser, time.time())
                user.setDetail("realname", "b#" + str(user.id))
                user.setDetail("reputation", "0")
                user.setDetail("profile_image", "")
                user.setDetail("frozen", "0")
                return "{ok}"
            elif cuser.isAdmin() and data["type"] == "admin.destroy":
                user.setDetail("deleted", 1)
                user.addAnnotation("delete", u"Benutzerkonto wurde durch Administrator zerstört.", cuser, time.time())
                user.setDetail("realname", "b#" + str(user.id))
                user.setDetail("name", "@")
                user.setDetail("password", "@")
                user.setDetail("reputation", "0")
                user.setDetail("aboutme", "")
                user.setDetail("labels", "[]")
                user.setDetail("profile_image", "")
                user.setDetail("frozen", "1")
                return "{ok}"
            elif cuser.id == user.id and data["type"] == "fast":
                user.setDetail("deleted", 1)
                user.setDetail("realname", "b#" + str(user.id))
                user.setDetail("reputation", "0")
                return "{ok}"
            elif cuser.id == user.id and data["type"] == "full":
                user.setDetail("deleted", 1)
                user.setDetail("realname", "b#" + str(user.id))
                user.setDetail("name", "@")
                user.setDetail("password", "@")
                user.setDetail("email", "@")
                user.setDetail("reputation", "0")
                user.setDetail("aboutme", "")
                user.setDetail("labels", "[]")
                user.setDetail("profile_image", "")
                user.setDetail("frozen", "1")
                return "{ok}"
        else:
            return "Der Benutzer wurde nicht gefunden. Vielleicht wurde er bereits gelöscht."
    else:
        return "Der Benutzer wurde nicht gefunden. Vielleicht wurde er bereits gelöscht."

def set_user(field):
    data = request.json
    if not "new_value" in data.keys():
        abort(400)
    if not "userid" in data.keys():
        abort(400)
    uid = data["userid"]
    cuser = muser.getCurrentUser()
    if uid < 0 and not cuser.isAdmin():
        abort(403)
    if not (cuser.isAdmin() or uid == cuser.id):
        abort(403)
    if cuser.isAdmin() and field in ["name"]:
        u = muser.User.from_id(uid)
        new_value = data["new_value"]
        u.setDetail(field, new_value)
    elif field in ["realname", "email", "aboutme"]:
        new_value = data["new_value"]
        if field == "realname":
            if len(new_value) > 25:
                return "Anzeigename zu lang"
            if len(new_value) < 2:
                return "Anzeigename zu kurz"
        muser.User.from_id(uid).setDetail(field, new_value)
    elif field == "password":
        new_value = data["new_value"]
        if new_value == "":
            muser.User.from_id(uid).setDetail(field, "")
        else:
            muser.User.from_id(uid).setDetail(field, sha1(new_value))
    elif field == "role" and cuser.isDev():
        new_value = data["new_value"]
        print(uid)
        print(field)
        print(data["new_value"])
        if new_value in ["administrator", "moderator", "user"]:
            muser.User.from_id(uid).setDetail("role", new_value)
    elif field in ["state", "frozen"] and cuser.isAdmin():
        new_value = data["new_value"]
        if new_value in ["1", "0", "-2"]:
            muser.User.from_id(uid).setDetail(field, new_value)
    return "ok"

def user_toggle_priv(uid):
    data = request.json
    try:
        uid = int(uid)
    except:
        return "ok"
    if not "privilege" in data.keys():
        abort(400)
    priv = data["privilege"]
    cuser = muser.getCurrentUser()
    if uid < 0 and not cuser.isAdmin():
        abort(403)
    if priv not in mprivileges.getAll():
        return "ok"
    user = muser.User.from_id(uid)
    old = user.getDetail("suspension")
    if priv in old:
        old.remove(priv)
    else:
        old.append(priv)
    user.setDetail("suspension", json.dumps(old))
    return "ok"

def user_toggle_label(uid):
    data = request.json
    try:
        uid = int(uid)
    except:
        return "ok"
    if not "label" in data.keys():
        abort(400)
    label = data["label"]
    cuser = muser.getCurrentUser()
    if not cuser.isAdmin():
        abort(403)
    user = muser.User.from_id(uid)
    if label not in user.possibleLabels:
        return "ok"
    old = user.getDetail("labels")
    if label in old:
        old.remove(label)
    else:
        old.append(label)
    user.setDetail("labels", json.dumps(old))
    return "ok"

def user_reputation_audit():
    cuser = muser.getCurrentUser()
    k = []
    u = []
    for x in cuser.getReputationChanges():
        x["amount_text"] = cnum.num2suff(x["amount"])
        x["message_html"] = md.markdown(x["message"])
        if x["recognized"] == 1:
            k.append(x)
            if len(k) == 5:
                break
        else:
            u.append(x)
    dat = {
        "delta": u,
        "reputation": cnum.num2suff(cuser.getReputation()),
        "latest": k,
        "userid": cuser.id
    }
    d = jsonify(dat)
    cuser.knowReputationChanges()
    return d

def user_notification_clear():
    cuser = muser.getCurrentUser()
    cuser.hideNotifications()
    return "{ok}"

def user_deleted_page(id):
    try:
        id = int(id)
    except:
        abort(404)
    if muser.User.exists(id):
        user = muser.User.from_id(id)
        cuser = muser.getCurrentUser()
        if not user.isDeleted() or not cuser.isAdmin():
            abort(404)
        elif cuser.isAdmin():
            return render_template("user/deleted-user-page.html", data=user, title="Benutzerkonto entfernt")
    else:
        abort(404)


def apply(app):
    app.route('/u/<id>')(app.route('/user/<id>')(app.route('/user/<id>/<name>')(user_page)))
    app.route('/u/<id>/flags')(app.route('/user/<id>/<name>/flags')(user_flags_page))
    app.route('/u/<id>/rep')(app.route('/user/<id>/<name>/reputation')(user_rep_page))
    app.route('/u/<id>/del')(app.route('/user/<id>/<name>/delete')(user_del_page))
    app.route('/user/<id>/deletion', methods=["POST"])(delete_user)
    app.route('/user/set/<field>', methods=["GET", "POST"])(set_user)
    app.route('/user/<id>/flag', methods=["GET", "POST"])(flag_user)
    app.route("/user/<uid>/toggle-privilege", methods=["GET", "POST"])(user_toggle_priv)
    app.route("/user/<uid>/toggle-label", methods=["GET", "POST"])(user_toggle_label)
    app.route("/user/reputation-audit", methods=["GET", "POST"])(user_reputation_audit)
    app.route("/user/notification-clear", methods=["GET", "POST"])(user_notification_clear)
    app.route("/deleted-user/<id>")(user_deleted_page)
