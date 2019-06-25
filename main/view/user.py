# coding: utf-8
from flask import request, session, redirect, url_for, abort, render_template, jsonify
from model import privileges as mprivileges, tags as mtags, user as muser, reviews as mreviews, forum as mforum, post_templates as mposttemplates, courses as mcourses, badges as mbadges, proposal as mproposal
from controller import num as cnum, times as ctimes

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
        if mt and not cuser.isMod():
            return redirect(url_for("user_page", id=mt))
        if user.isDeleted():
            if not cuser.isMod():
                abort(404)
            else:
                return redirect(url_for("user_deleted_page", id=id))

        if name != user.getDetail("name"):
            return redirect(url_for("user_page", id=id, name=user.getDetail("name")))
        else:
            temp = None
            return render_template("user/view.html", data=user, thispage="user", title="Benutzer " + user.getHTMLName(False), mcourses=mcourses.Courses)
    else:
        abort(404)

def user_edit_page(id, name=None):
    try:
        id = int(id)
    except:
        abort(404)
    if muser.User.exists(id):
        user = muser.User.from_id(id)
        cuser = muser.getCurrentUser()
        mt = user.getDetail("mergeto")
        if mt and not cuser.isMod():
            return redirect(url_for("user_edit_page", id=mt))
        if user.isDeleted():
            if not cuser.isMod():
                abort(404)
        if user.id != cuser.id and not cuser.isMod() or cuser.isDisabled():
            abort(404)
        if name != user.getDetail("name"):
            return redirect(url_for("user_edit_page", id=id, name=user.getDetail("name")))
        else:
            if request.values.get("page", "profile") == "profile":
                return render_template("user/edit/profile.html", data=user, thispage="user", title="Profil bearbeiten " + user.getHTMLName(False))

            elif request.values.get("page", "profile") == "login":
                return render_template("user/edit/login.html", data=user, thispage="user", title=u"Anmeldedaten für " + user.getHTMLName(False), current_time=time.time())

            elif request.values.get("page", "profile") == "preferences":
                return render_template("user/edit/preferences.html", data=user, thispage="user", title=u"Einstellungen für " + user.getHTMLName(False))

            elif request.values.get("page", "profile") == "dev" and cuser.isDev():
                return render_template("user/edit/dev.html", data=user, thispage="user", title=u"Entwickleroptionen für " + user.getHTMLName(False), roles=muser.getRoles())

            elif request.values.get("page", "profile") == "login-alter":
                if user.id != cuser.id:
                    abort(403)

                current_time=time.time()
                if session.get("login_time", 0) + 10 * 60 <= current_time:
                    return "<p>Das Zeitfenster zur Aktualisierung von Zugangsdaten ist abgelaufen. <a href='?page=login'>Den Anweisungen hier folgen.</a></p>", 403

                if request.values.get("method") == "local_account":
                    if request.method == "POST":
                        user.setDetail("login_provider", "local_account")
                        user.setDetail("email", request.form["email"])
                        user.setDetail("password", sha1(request.form["password"]))
                        return redirect(url_for("user_edit_page", id=user.id, name=user.getDetail("name"), page="login"))
                    else:
                        return render_template("user/edit/login-alter__local-account.html", data=user, thispage="user", title=u"Anmeldedaten aktualisieren für " + user.getHTMLName(False))

                elif request.values.get("method") == "oauth:google":
                    return render_template("user/edit/login-alter__google.html", data=user, thispage="user", title=u"Anmeldedaten aktualisieren für " + user.getHTMLName(False))

            elif request.values.get("page", "profile") == "delete":
                return render_template("user/edit/delete.html", data=user, thispage="user", title=u"Konto löschen " + user.getHTMLName(False), current_time=time.time())

            else:
                abort(404)
    else:
        abort(404)


def user_activity_page(id, name=None):
    try:
        id = int(id)
    except:
        abort(404)
    if muser.User.exists(id):
        user = muser.User.from_id(id)
        cuser = muser.getCurrentUser()
        mt = user.getDetail("mergeto")
        if mt and not cuser.isMod():
            return redirect(url_for("user_edit_page", id=mt))
        if user.isDeleted():
            if not cuser.isMod():
                abort(404)
            else:
                return redirect(url_for("user_deleted_page", id=id))
        if name != user.getDetail("name"):
            return redirect(url_for("user_activity_page", id=id, name=user.getDetail("name")))
        else:
            if request.values.get("page", "summary") == "summary":
                return render_template("user/activity/summary.html", data=user, thispage="user", title=u"Aktivität " + user.getHTMLName(False), courses=mcourses.Courses)

            elif request.values.get("page", "summary") == "courses":
                return render_template("user/activity/courses.html", data=user, thispage="user", title="Kurse von " + user.getHTMLName(False), mcourses=mcourses.Courses, mproposals=mproposal.Proposal)

            elif request.values.get("page", "summary") == "forum":
                return render_template("user/activity/forum.html", data=user, thispage="user", title=u"Forenbeiträge von " + user.getHTMLName(False), mquestions=mforum.Article, manswers=mforum.Answer, mquestion=lambda x:mforum.Article(x))

            elif request.values.get("page", "summary") == "reputation":
                return render_template("user/activity/reputation.html", data=user, thispage="user", title="Reputation von " + user.getHTMLName(False))

            elif request.values.get("page", "summary") == "badges":
                return render_template("user/activity/badges.html", data=user, thispage="user", title="Abzeichen von " + user.getHTMLName(False), getCollectedBadges=mbadges.Badge.byUser)

            elif request.values.get("page", "summary") == "flags":
                if user.id != cuser.id and not cuser.isMod():
                    abort(403)

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

                return render_template("user/activity/flags.html", data=user, closure_flags=cd, post_deletion_flags=pdd, custom_flags=customd, thispage="user", title="Meldungen von " + user.getHTMLName(False), closure_helpful=closure_helpful, closure_pending=closure_pending, closure_declined=closure_declined, closure_total=closure_total, post_deletion_helpful=post_deletion_helpful, post_deletion_pending=post_deletion_pending, post_deletion_declined=post_deletion_declined, post_deletion_total=post_deletion_total, custom_helpful=custom_helpful, custom_pending=custom_pending, custom_declined=custom_declined, custom_total=custom_total)

            else:
                abort(404)
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
        if mt and not cuser.isMod():
            return redirect(url_for("user_page", id=mt))
        if user.isDeleted():
            if not cuser.isMod():
                abort(404)
            else:
                return redirect(url_for("user_deleted_page", id=id))

        if not cuser.isMod() and cuser.id != id:
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

        else:
            return "Der Benutzer wurde nicht gefunden. Vielleicht wurde er bereits gelöscht."
    else:
        return "Der Benutzer wurde nicht gefunden. Vielleicht wurde er bereits gelöscht."


def delete_user(id):
    try:
        id = int(id)
    except:
        return "Ungültige Anfrage. Bitte im globalen Forum melden!", 400
    cuser = muser.getCurrentUser()
    if muser.User.exists(id):
        user = muser.User.from_id(id)
        if not user.isDeleted():
            if user.id != cuser.id:
                if not cuser.isMod():
                    abort(404)
                if user.isMod() or user.isTeam():
                    return "Benutzer mit Rollen können nicht gelöscht werden."
                data = request.json
                if not data["destroy"]:
                    user.setDetail("deleted", 1)
                    user.addAnnotation("delete", u"Benutzerkonto wurde durch Moderator gelöscht: " + data["reason"], cuser, time.time())
                else:
                    user.setDetail("deleted", 2)
                    user.addAnnotation("delete", u"Benutzerkonto wurde durch Moderator zerstört: " + data["reason"], cuser, time.time())
                return "{ok}"
            else:
                user.setDetail("deleted", 1)
                return "{ok}"


        else:
            if cuser.isMod() and request.values.get("action")=="prevent":
                user.setDetail("deleted", 0)
                user.addAnnotation("custom", u"Löschung des Benutzerkontos verhindert", cuser, time.time())
                return "{ok}"
            else:
                return "Der Benutzer wurde nicht gefunden. Vielleicht wurde er bereits gelöscht.", 404
    else:
        return "Der Benutzer wurde nicht gefunden. Vielleicht wurde er bereits gelöscht.", 404

def edit_user(id):
    if not muser.User.exists(id):
        abort(404)
    cuser = muser.getCurrentUser()
    id = int(id)
    if id < 0 and not cuser.isMod():
        abort(403)
    if not (cuser.isMod() or id == cuser.id) or cuser.isDisabled():
        abort(403)

    user = muser.User(id)

    data = request.json

    user_name = data["name"].strip()
    profile_text = data["profile_text"]
    profile_image = data["profile_image"]
    profile_place = data["profile_place"]
    profile_website = data["profile_website"]
    profile_twitter = data["profile_twitter"]
    profile_projects = data["profile_projects"]

    errors = []
    if 3 <= len(user_name) <= 40 and u"♦" not in user_name:
        user.setDetail("realname", user_name)
        user.setDetail("name", user_name)
    else:
        if u"♦" in user_name:
            errors.append(u"Der Benutzername darf das ♦-Zeichen nicht enthalten!")
        if 3 > len(user_name):
            errors.append(u"Der Benutzername ist zu kurz. Mindestens drei Zeichen erforderlich. (aktuell: %i)" % len(user_name))
        if 40 < len(user_name):
            errors.append(u"Der Benutzername ist zu lang. Höchstens 40 Zeichen möglich. (aktuell: %i)" % len(user_name))

    if len(profile_text) <= 5000:
        user.setDetail("aboutme", profile_text)
    else:
        errors.append(u"Der Profiltext ist zu lang. Höchstens 5000 Zeichen möglich. (aktuell: %i)" % len(profile_text))

    if "javascript:" not in profile_image and len(profile_image) <= 5000:
        user.setDetail("profile_image", profile_image)
    else:
        if "javascript:" in profile_image:
            errors.append(u"Der Link für das Profilbild enthält unerlaubte Zeichenfolgen.")
        if len(profile_image) > 5000:
            errors.append(u"Der Link für das Profilbild ist zu lang. Höchstens 5000 Zeichen möglich. (aktuell: %i)" % len(profile_image))

    if len(profile_place) <= 100:
        user.setDetail("profile_place", profile_place)
    else:
        errors.append(u"Die Eingabe für den Wohnort ist zu lang. Höchstens 100 Zeichen möglich. (aktuell: %i)" % len(profile_place))

    if len(profile_website) > 8 and profile_website.startswith("http://"):
        profile_website = profile_website[len("http://"):]
    elif len(profile_website) > 8 and profile_website.startswith("https://"):
        profile_website = profile_website[len("https://"):]

    if len(profile_website) <= 150:
        user.setDetail("profile_website", profile_website)
    else:
        errors.append(u"Die Eingabe für die Webseite ist zu lang. Höchstens 150 Zeichen möglich. (aktuell: %i)" % len(profile_website))

    if profile_twitter == "":
        user.setDetail("profile_twitter", profile_twitter)
    elif 2 <= len(profile_twitter) <= 150 and profile_twitter[0] == "@":
        user.setDetail("profile_twitter", profile_twitter)
    else:
        if 2 > len(profile_twitter):
            errors.append(u"Die Eingabe für den Twitter-Account ist zu kurz. Mindestens zwei Zeichen nötig. (aktuell: %i)" % len(profile_twitter))
        elif profile_twitter[1] != "@":
            errors.append(u"Die Eingabe für den Twitter-Account ist ungültig. Es fehlt das @-Zeichen")
        if 150 < len(profile_twitter):
            errors.append(u"Die Eingabe für den Twitter-Account ist zu lang. Höchstens 150 Zeichen möglich. (aktuell: %i)" % len(profile_twitter))

    if len(profile_projects) <= 750:
        user.setDetail("profile_projects", profile_projects)
    else:
        errors.append(u"Die Eingabe für deine Projekte ist zu lang. Höchstens 750 Zeichen möglich. (aktuell: %i)" % len(profile_projects))

    if len(errors):
        return jsonify({
            "result": "error",
            "errors": errors
        })
    else:
        return jsonify({
            "result": "ok"
        })


def preferences_for_user(id):
    if not muser.User.exists(id):
        abort(404)
    cuser = muser.getCurrentUser()
    id = int(id)
    if id < 0 and not cuser.isMod():
        abort(403)
    if not (cuser.isMod() or id == cuser.id):
        abort(403)

    user = muser.User(id)

    data = request.json

    VALID_PREFERENCES = ["darkTheme", "autoSave"]

    if data["key"] not in VALID_PREFERENCES:
        return jsonify({
            "result": "error",
            "error": "Ungültige Einstellung"
        })

    user.setPref(data["key"], data["value"])

    return jsonify({
        "result": "ok"
    })


def devtools_for_user(id):
    if not muser.User.exists(id):
        abort(404)
    cuser = muser.getCurrentUser()
    id = int(id)
    if not cuser.isDev():
        abort(403)

    user = muser.User(id)

    data = request.json

    if data["action"] == "update-role":
        user.setDetail("role", data["role"])
        return "ok"
    elif data["action"] == "override-delete":
        if user.isDeleted():
            user.setDetail("reputation", 0)
            return "ok"
        else:
            return "account not deleted", 400
    elif data["action"] == "reget-reputation":
        user.regetRep(data["global"])
        return "ok"

    return "no action found",400

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
        if not user.isDeleted() or not cuser.isMod():
            abort(404)
        elif cuser.isMod():
            return render_template("user/deleted-user-page.html", data=user, title="Benutzerkonto entfernt")
    else:
        abort(404)

def user_deletion_carried_out_page():
    return render_template("user/deletion-carried-out-page.html", title="Benutzerkonto entfernt")


def apply(app):
    app.route('/u/<id>')(app.route('/user/<id>')(app.route('/user/<id>/<name>')(user_page)))
    app.route('/u/<id>/del')(app.route('/user/<id>/<name>/delete')(user_del_page))
    app.route('/user/<id>/delete', methods=["POST"])(delete_user)
    app.route('/user/<id>/edit', methods=["POST"])(edit_user)
    app.route('/user/<id>/dev-tools', methods=["POST"])(devtools_for_user)
    app.route('/user/<id>/preferences', methods=["POST"])(preferences_for_user)
    app.route('/u/<id>/edit', methods=["GET","POST"])(app.route('/user/<id>/<name>/edit', methods=["GET","POST"])(user_edit_page))
    app.route('/u/<id>/activity', methods=["GET","POST"])(app.route('/user/<id>/<name>/activity', methods=["GET","POST"])(user_activity_page))
    app.route('/user/<id>/flag', methods=["GET", "POST"])(flag_user)
    app.route("/user/reputation-audit", methods=["GET", "POST"])(user_reputation_audit)
    app.route("/user/notification-clear", methods=["GET", "POST"])(user_notification_clear)
    app.route("/deleted-user/<id>")(user_deleted_page)
    app.route("/user/deleted")(user_deletion_carried_out_page)
