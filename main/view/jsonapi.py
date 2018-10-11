# coding: utf-8
from flask import render_template, redirect, abort, url_for, request, jsonify
from model import forum as mforum, user as muser

def jsex_forum_articles():
    if muser.require_login():
        abort(404)
    article_list=mforum.Article.getAll(deleted=False)
    data = []
    for a in article_list:
        aut = a.getAuthor()
        data.append({
            "id": a.id,
            "forumID": a.getDetail("forumID"),
            "title": a.getTitle(),
            "author": {
                "id": aut.id,
                "html_name": aut.getHTMLName(False),
                "name": aut.getDetail("realname"),
                "is_mod": aut.isMod() and not aut.isMod(),
                "is_admin": aut.isAdmin(),
                "reputation": aut.getReputation()
            },
            "score": a.getScore(),
            "content": a.getContent(),
            "tag": a.getTags(),
            "hasAcceptedAnswer": a.hasAccepted() != 0,
            "closed": a.isClosed(),
            "closure_reason": a.getDetail("closureReason")
        })
    return jsonify(data)

def apply(app):
    app.route("/json/forum-articles")(jsex_forum_articles)
