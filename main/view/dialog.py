# coding: utf-8
from flask import request, session, jsonify, render_template
from model import user as muser, forum as mforum, dialog as mdialog

def _error(msg):
    return jsonify({"response":"error", "message":msg})

def _info(msg):
    return jsonify({"response":"info", "message":msg})

def _dialog(item, route):
    d = mdialog.DIALOG_AREAS[item]
    if route in d.keys():
        return jsonify(d[route])
    return _error("Zugriffspunkt nicht gefunden.")

def dialog_post_api(post_id, route):
    try:
        post_id = int(post_id)
    except:
        return _error("Ungültige Anfrage, bitte im globalen Forum melden.")
    cuser = muser.getCurrentUser()
    if not cuser.isLoggedIn():
        return _error("Nur angemeldete Benutzer können Beiträge melden.")

    if not mforum.Article.exists(post_id):
        return _error("Beitrag nicht gefunden.")
    post = mforum.Article(post_id)

    if post.isDeleted() or post.getDetail("author") == cuser.id:
        r = "post_own_or_deleted"
    elif post.isClosed():
        r = "post_closed"
    elif cuser.may("forum_closeQuestion"):
        r = "post_close_priv"
    else:
        r = "post_no_close_priv"

    if route.startswith("mod"):
        r = "post"

    return _dialog(r, route)

def dialog_post_api_fetch(post_id, route):
    try:
        post_id = int(post_id)
    except:
        return _error("Ungültige Anfrage, bitte im globalen Forum melden.")
    cuser = muser.getCurrentUser()
    if not cuser.isLoggedIn():
        return _error("Nur angemeldete Benutzer können Beiträge melden.")

    if not mforum.Article.exists(post_id):
        return _error("Beitrag nicht gefunden.")
    post = mforum.Article(post_id)

    live = bool(request.values.get("live", 0))
    if live:
        if post.isClosed() or post.isDeleted():
            return "<div style='color: #c00; font-family:  \"Open Sans\", Arial, sans-serif'>Beitrag ist bereits geschlossen oder gelöscht.</div>"


        if route not in ["flagging/closure/duplicate", "closure/duplicate"]:
            return "<div style='color: #c00; font-family:  \"Open Sans\", Arial, sans-serif'>Ein Fehler ist aufgetreten. Bitte im <a href='/f/0' target='_blank' style='color: #600; font-weight: bold;'>globalen Forum</a> melden.</div>"

        search = request.values.get("search", "").strip()
        if search == "":
            return ""


        id = None
        if search.startswith("#"):
            try:
                id = int(search[1:])
            except:
                id = None
            if not mforum.Article.exists(id):
                id = None

        if id:
            data = mforum.Article(id)
            return render_template("forum/raw_qna.html", data=data)
        else:
            return "<div style='font-family:  \"Open Sans\", Arial, sans-serif'>Bitte wähle ein Suchergebnis aus der Liste rechts.</div>"

    else:
        if post.isClosed() or post.isDeleted():
            return "[]"


        if route not in ["flagging/closure/duplicate", "closure/duplicate"]:
            return "[]"

        search = request.values.get("search", "").strip()
        if search == "":
            return "[]"
        forum = mforum.Forum(post.getDetail("forumID"))
        data = forum.getArticles(search, "score")[:80]
        data = [{"id": k.id, "title": k.getHTMLTitle(), "score": k.getScore(), "tags": k.getTags(), "closed": k.isClosed()} for k in data if not k.isDeleted()]
        return jsonify(data[:10])

def apply(app):
    app.route("/dialog/post/<post_id>/<path:route>", methods=["GET", "POST"])(dialog_post_api)
    app.route("/dialog/post/<post_id>/<path:route>/fetch", methods=["GET", "POST"])(dialog_post_api_fetch)
