# coding: utf-8
from flask import request, session, redirect, url_for, abort, render_template, jsonify
from model import privileges as mprivileges, tags as mtags, user as muser, forum as mforum
from controller import diff as cdiff
from sha1 import sha1
import time

def forum_list(id, label=None):
    try:
        id = int(id)
    except:
        abort(404)
    if mforum.Forum.exists(id):
        forum = mforum.Forum.from_id(id)
        cuser = muser.getCurrentUser()
        if label != forum.getDetail("label"):
            return redirect(url_for("forum_list", id=id, label=forum.getDetail("label")))
        else:
            return render_template("forum/list.html", tagged=None, forum=forum, thispage="courses" if id != 0 else "forum", title=forum.getDetail("name"), search=request.values.get("query", False), ForumAnnouncement=mforum.ForumAnnouncement)
    else:
        abort(404)

def forum_tag_view(id, tag, label=None):
    try:
        id = int(id)
    except:
        abort(404)
    if mforum.Forum.exists(id):
        forum = mforum.Forum.from_id(id)
        cuser = muser.getCurrentUser()
        if label != forum.getDetail("label"):
            return redirect(url_for("forum_tag_view", id=id, tag=tag, label=forum.getDetail("label")))
        else:
            tagged = mtags.ForumTag.byName(tag)
            if not tagged:
                tagged = mtags.ForumTag.byName(tag, id)
            if not tagged:
                tagged = mtags.blankTag(tag)
            return render_template("forum/list.html", tagged=tagged, forum=forum, thispage="courses" if id != 0 else "forum", title=forum.getDetail("name"), search=request.values.get("query", False), ForumAnnouncement=mforum.ForumAnnouncement)
    else:
        abort(404)

def forum_tag_options(id, tag, label=None):
    try:
        id = int(id)
    except:
        abort(404)
    if mforum.Forum.exists(id):
        forum = mforum.Forum.from_id(id)
        cuser = muser.getCurrentUser()
        if label != forum.getDetail("label"):
            return redirect(url_for("forum_tag_options", id=id, tag=tag, label=forum.getDetail("label")))
        else:
            if not cuser.isMod():
                abort(404)
            tagged = mtags.ForumTag.byName(tag)
            if not tagged:
                tagged = mtags.ForumTag.byName(tag, id)
            if not tagged:
                abort(404)
            if request.method == "POST":


                data = request.json

                excerpt = data["excerpt"].strip()
                deprecation_notice = data["deprecation_notice"].strip()
                applicable = data["applicable"]

                if cuser.isDev():
                    mod_only = data["mod_only"]

                errors = []

                if len(excerpt) > 300:
                    errors.append(u"Die Kurzbeschreibung ist zu lang. Maximal 300 Zeichen möglich. (aktuell: %i)" % len(excerpt))
                else:
                    tagged.setDetail("excerpt", excerpt)

                if len(deprecation_notice) > 150:
                    errors.append(u"Die Kurzbeschreibung ist zu lang. Maximal 150 Zeichen möglich. (aktuell: %i)" % len(deprecation_notice))
                else:
                    tagged.setDetail("deprecation_notice", deprecation_notice)


                tagged.setDetail("applicable", applicable)

                if cuser.isDev():
                    tagged.setDetail("mod_only", mod_only)

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
                return render_template("forum/tag_options.html", tag=tagged, forum=forum, thispage="courses" if id != 0 else "forum", title=forum.getDetail("name"))
    else:
        abort(404)

def forum_new(id, label=None):
    try:
        id = int(id)
    except:
        abort(404)
    if muser.require_login() or muser.getCurrentUser().isDisabled(): abort(403)
    if mforum.Forum.exists(id):
        forum = mforum.Forum.from_id(id)
        cuser = muser.getCurrentUser()
        if label != forum.getDetail("label"):
            return redirect(url_for("forum_new", id=id, label=forum.getDetail("label")))
        else:
            if request.method == "GET":
                return render_template("forum/new.html", forum=forum, thispage="courses" if id != 0 else "forum", title=forum.getDetail("name"))
            elif request.method == "POST":

                data = request.json

                title = data["title"].strip()
                body = data["body"].strip()
                tags = data["tags"]

                errors, warnings = _validateQuestion(title, body, tags, cuser, id)

                if len(errors):
                    return jsonify({
                        "result": "error",
                        "errors": errors,
                        "warnings": warnings
                    })
                elif len(warnings) and request.values.get("ignore-warnings", 0) != "yes":
                    return jsonify({
                        "result": "warnings",
                        "warnings": warnings
                    })
                else:
                    article = mforum.Article.createNew(id, title, body, "|".join(["["+t+"]" for t in tags]), cuser)
                    article.setDetail("last_activity_date", time.time())
                    article.setDetail("creation_date", time.time())

                    article.addRevision(title, body, "|".join(["["+t+"]" for t in tags]), cuser, u"Ursprüngliche Version")

                    for t in tags:

                        tagged = mtags.ForumTag.byName(t)
                        if not tagged:
                            tagged = mtags.ForumTag.byName(t, id)
                        if not tagged:
                            tagged = mtags.ForumTag.byName(t, "any")
                            if tagged:
                                tagged.setDetail("forum_id", None)
                        if not tagged:
                            tagged = mtags.ForumTag.createNew(t, id)

                        tagged.addAssoc(article.id)

                    return jsonify({
                        "result": "ok",
                        "url": "/f/"+str(id)+"/"+str(article.id)
                    })
    else:
        abort(404)

def forum_post_answer(forum_id, post_id, forum_label=None):
    try:
        forum_id = int(forum_id)
    except:
        abort(404)
    try:
        post_id = int(post_id)
    except:
        abort(404)
    if muser.require_login() or muser.getCurrentUser().isDisabled(): abort(403)
    if mforum.Forum.exists(forum_id):
        forum = mforum.Forum.from_id(forum_id)
        cuser = muser.getCurrentUser()
        if mforum.Article.exists(forum_id, post_id):
            article = mforum.Article(post_id)
            data = request.json

            body = data["body"].strip()

            errors, warnings = _validateBody(body, cuser, id)

            if len(errors):
                return jsonify({
                    "result": "error",
                    "errors": errors,
                    "warnings": warnings
                })
            elif len(warnings) and request.values.get("ignore-warnings", 0) != "yes":
                return jsonify({
                    "result": "warnings",
                    "warnings": warnings
                })
            else:

                answer = mforum.Answer.createNew(forum_id, post_id, body, cuser)
                answer.addRevision(body, cuser, u"Ursprüngliche Version")

                article.setDetail("last_activity_date", time.time())
                answer.setDetail("last_activity_date", time.time())
                answer.setDetail("creation_date", time.time())

                au = article.getAuthor()
                if au.id == -1:
                    answer.setDetail("author", -1)
                    answer.addRevComm("anonymized", cuser, "-1")
                elif au.id != -3:
                    au.notify("answered", "Es gibt eine neue Antwort auf deinen Foren-Beitrag \"" + article.getTitle() + "\"", "/f/"+str(forum_id)+"/"+str(article.id) + "#answer-" + str(answer.id))

                return jsonify({
                    "result": "ok",
                    "url": "/f/"+str(forum_id)+"/"+str(article.id) + "#answer-" + str(answer.id)
                })
        else:
            abort(404)
    else:
        abort(404)

def forum_view(forum_id, id, forum_label=None, label=None):
    try:
        id = int(id)
    except:
        abort(404)
    try:
        forum_id = int(forum_id)
    except:
        abort(404)
    if mforum.Forum.exists(forum_id):
        forum = mforum.Forum.from_id(forum_id)
        cuser = muser.getCurrentUser()
        if forum_label != forum.getDetail("label"):
            return redirect(url_for("forum_view", forum_id=forum_id, forum_label=forum.getDetail("label"), label=label, id=id))
        else:
            if mforum.Article.exists(forum_id, id):
                article = mforum.Article(id)
                if label != article.getLabel():
                    return redirect(url_for("forum_view", forum_id=forum_id, forum_label=forum_label, label=article.getLabel(), id=id))
                else:
                    if not article.mayBeSeen(cuser):
                        abort(404)
                    return render_template("forum/view.html", forum=forum, post=article, thispage="courses" if forum_id != 0 else "forum", title=forum.getDetail("name"), ForumAnnouncement=mforum.ForumAnnouncement)
            else:
                abort(404)
    else:
        abort(404)

def forum_post_mod(forum_id, post_id, forum_label=None):
    try:
        forum_id = int(forum_id)
    except:
        abort(404)
    try:
        post_id = int(post_id)
    except:
        abort(404)
    if "property" not in request.json.keys():
        abort(404)
    property = request.json["property"]
    if "new_value" not in request.json.keys():
        abort(404)
    new_value = request.json["new_value"]
    if mforum.Forum.exists(forum_id):
        if mforum.Article.exists(forum_id, post_id):
            cuser = muser.getCurrentUser()
            if not cuser.isMod():
                abort(404)
            article = mforum.Article(post_id)
            article.setDetail(property, new_value)
            if property == "moderatorNotice":
                article.addRevComm("notice", cuser, new_value)
            elif property == "author":
                if new_value == -1:
                    article.addRevComm("anonymized", cuser, new_value)
                else:
                    article.addRevComm("transferred", cuser, new_value)
            elif property == "frozen":
                if new_value == 1:
                    article.setDetail("frozenBy", cuser.id)
                    if article.getDetail("frozenAsLock"):
                        article.addRevComm("locked", cuser, article.getFrozenMessage())
                    else:
                        article.addRevComm("frozen", cuser, article.getFrozenMessage())
                else:
                    if article.getDetail("frozenAsLock"):
                        article.addRevComm("unlocked", cuser, "")
                        article.setDetail("frozenAsLock", 0)
                    else:
                        article.addRevComm("unfrozen", cuser, "")
    abort(404)

def forum_post_edit(forum_id, post_id, forum_label=None):
    try:
        forum_id = int(forum_id)
        post_id = int(post_id)
    except:
        abort(404)
    if muser.require_login() or muser.getCurrentUser().isDisabled(): abort(403)
    if mforum.Forum.exists(forum_id):
        forum = mforum.Forum.from_id(forum_id)
        if forum_label != forum.getDetail("label"):
            return redirect(url_for("forum_post_edit", forum_id=forum_id, forum_label=forum.getDetail("label"), post_id=post_id))
        if mforum.Article.exists(forum_id, post_id):
            cuser = muser.getCurrentUser()
            article = mforum.Article(post_id)
            if not article.mayBeSeen(cuser):
                abort(404)
            if request.method == "GET":
                return render_template("forum/edit-post.html", title="Beitrag bearbeiten", thispage="courses" if forum_id != 0 else "forum", forum=forum, article=article)
            elif request.method == "POST":
                data = request.json
                title = data["title"].strip()
                body = data["body"].strip()
                tags = data["tags"]
                comment = data["comment"]
                errors, warnings = _validateQuestion(title, body, tags, cuser, forum.id)

                if len(errors):
                    return jsonify({
                        "result": "error",
                        "errors": errors,
                        "warnings": warnings
                    })
                elif len(warnings) and request.values.get("ignore-warnings", 0) != "yes":
                    return jsonify({
                        "result": "warnings",
                        "warnings": warnings
                    })
                else:

                    if cuser.may("forum_reviewEdits") or cuser.id == article.getAuthor().id:

                        article.setDetail("title", title)
                        article.setDetail("content", body)
                        oldtags = article.getTagObjects()
                        article.setDetail("tags", "|".join(["["+t+"]" for t in tags]))

                        article.setDetail("last_edit_date", time.time())
                        article.setDetail("last_activity_date", time.time())

                        article.addRevision(title, body, "|".join(["["+t+"]" for t in tags]), cuser, comment or "Beitrag bearbeitet")

                        for t in oldtags:
                            t.removeAssoc(article.id)

                        for t in tags:

                            tagged = mtags.ForumTag.byName(t)
                            if not tagged:
                                tagged = mtags.ForumTag.byName(t, forum.id)
                            if not tagged:
                                tagged = mtags.ForumTag.byName(t, "any")
                                if tagged:
                                    tagged.setDetail("forum_id", None)
                            if not tagged:
                                tagged = mtags.ForumTag.createNew(t, forum.id)

                            tagged.addAssoc(article.id)

                        return jsonify({
                            "result": "ok",
                            "url": "/f/"+str(forum.id)+"/"+str(article.id)
                        })
    abort(404)

def forum_post_dialog(post_id):
    post_id = post_id.split("-")
    if len(post_id) != 2: abort(404)
    if post_id[0] not in ["post", "answer"]: abort(404)
    try: post_id[1] = int(post_id[1])
    except: abort(404)
    if muser.require_login() or muser.getCurrentUser().isDisabled(): abort(403)
    cuser = muser.getCurrentUser()
    el = mforum.Article if post_id[0] == "post" else mforum.Answer
    if el.exists(post_id[1]):
        E = el(post_id[1])

        if not E.mayBeSeen(cuser):
            abort(404)

        type = request.values.get("type")

        if type == "flag":
            return render_template("forum/dialog/flag.html", type = post_id[0], post=E)
        elif type == "close" and cuser.may("forum_closeQuestion"):
            return render_template("forum/dialog/closure.html", type = post_id[0], post=E, forum=mforum.Forum(E.getDetail("forumID")))
        elif type == "mod" and cuser.isMod():
            return render_template("forum/dialog/mod.html", type = post_id[0], post=E, forum=mforum.Forum(E.getDetail("forumID")))


        return jsonify({
            "result": "error",
            "error": "Ungültiger ?type-Parameter für den Dialog."
        })
    return jsonify({
        "result": "error",
        "error": "Der Beitrag wurde nicht gefunden. Vielleicht wurde er bereits gelöscht."
    })

    return "ok"

def forum_post_revision(forum_id, post_id, forum_label=None):
    try:
        forum_id = int(forum_id)
    except:
        abort(404)
    try:
        post_id = int(post_id)
    except:
        abort(405)
    if mforum.Forum.exists(forum_id):
        if mforum.Article.exists(forum_id, post_id):
            cuser = muser.getCurrentUser()
            article = mforum.Article(post_id)
            forum = mforum.Forum.from_id(forum_id)
            if not article.mayBeSeen(cuser):
                abort(404)
            return render_template("forum/revision-post.html", title="Beitragsversionen", thispage="courses" if forum_id != 0 else "forum", forum=forum, post=article, generate_diff=cdiff.generate_diff)
    abort(404)


def forum_post_rollback(forum_id, post_id, rev, forum_label=None):
    try:
        forum_id = int(forum_id)
    except:
        abort(404)
    try:
        rev = int(rev)
    except:
        abort(404)
    try:
        post_id = int(post_id)
    except:
        abort(404)
    cuser = muser.getCurrentUser()
    if not (cuser.may("forum_reviewEdits") or cuser.id == article.getAuthor().id):
        abort(403)
    if mforum.Forum.exists(forum_id):
        if mforum.Article.exists(forum_id, post_id):
            article = mforum.Article(post_id)
            forum = mforum.Forum.from_id(forum_id)
            if not article.mayBeSeen(cuser):
                abort(404)
            form = dict(request.form)
            try:
                rev = article.getRevisionById(rev)
            except Exception as e:
                print("#", e)
                abort(404)
            if form == {}:
                rev["tags"] = [i[1:-1] for i in rev["tags"].split("|")]
                return render_template("forum/rollback-post.html", title="Beitragsversion wiederherstellen", thispage="courses" if forum_id != 0 else "forum", rev=rev, forum=forum, article=article)
            else:
                comment = request.form["comment"]
                article.setDetail("content", rev["content"])
                article.setDetail("title", rev["title"])
                article.setDetail("tags", rev["tags"])
                print(rev)
                article.addRevision(rev["title"], rev["content"], rev["tags"], cuser, u"Wiederherstellung einer früheren Version: " + comment)
            return redirect(url_for("forum_view", id=post_id, forum_id=forum_id))
    abort(404)


def forum_post_protect(forum_id, post_id, forum_label=None):
    try:
        forum_id = int(forum_id)
    except:
        abort(404)
    try:
        post_id = int(post_id)
    except:
        abort(404)
    if mforum.Forum.exists(forum_id):
        if mforum.Article.exists(forum_id, post_id):
            cuser = muser.getCurrentUser()
            if not cuser.may("forum_setProtection"):
                abort(404)
            article = mforum.Article(post_id)
            if not article.isProtected() and (not article.isFrozen() or cuser.isMod()):
                data = request.json["type"]
                if data == 1:
                    article.setDetail("protected", 1)
                    article.setDetail("protectionBy", cuser.id)
                    article.addRevComm("protected", cuser, "answer")
                elif data == 2:
                    if not cuser.isMod():
                        abort(404)
                    article.setDetail("protected", 2)
                    article.setDetail("protectionBy", cuser.id)
                    article.addRevComm("protected", cuser, "wiki")
            return "ok"
    abort(404)

def forum_post_unprotect(forum_id, post_id, forum_label=None):
    try:
        forum_id = int(forum_id)
    except:
        abort(404)
    try:
        post_id = int(post_id)
    except:
        abort(404)
    if mforum.Forum.exists(forum_id):
        if mforum.Article.exists(forum_id, post_id):
            cuser = muser.getCurrentUser()
            if not cuser.may("forum_setProtection"):
                abort(404)
            article = mforum.Article(post_id)
            if article.isProtected() and (not article.isFrozen() or cuser.isMod()):
                data = article.getDetail("protected")
                if data == 1:
                    article.setDetail("protected", 0)
                    article.setDetail("protectionBy", 0)
                    article.addRevComm("unprotected", cuser, "")
                elif data == 2:
                    if not cuser.isMod():
                        abort(404)
                    article.setDetail("protected", 0)
                    article.setDetail("protectionBy", 0)
                    article.addRevComm("unprotected", cuser, "")
            return "ok"
    abort(404)


def forum_answer_mod(forum_id, answer_id, forum_label=None):
    try:
        forum_id = int(forum_id)
    except:
        abort(404)
    try:
        answer_id = int(answer_id)
    except:
        abort(404)
    if "property" not in request.json.keys():
        abort(404)
    property = request.json["property"]
    if "new_value" not in request.json.keys():
        abort(404)
    new_value = request.json["new_value"]
    if mforum.Forum.exists(forum_id):
        if mforum.Answer.exists(forum_id, answer_id):
            cuser = muser.getCurrentUser()
            if not cuser.isMod():
                abort(404)
            answer = mforum.Answer(answer_id)
            answer.setDetail(property, new_value)
            if property == "moderatorNotice":
                answer.addRevComm("notice", cuser, new_value)
            elif property == "author":
                if new_value == -1:
                    answer.addRevComm("anonymized", cuser, new_value)
                else:
                    answer.addRevComm("transferred", cuser, new_value)
            elif property == "frozen":
                if new_value == 1:
                    answer.setDetail("frozenBy", cuser.id)
                    answer.addRevComm("frozen", cuser, answer.getFrozenMessage())
                else:
                    answer.addRevComm("unfrozen", cuser, "")
    abort(404)

def forum_answer_edit(forum_id, answer_id, forum_label=None):
    try:
        forum_id = int(forum_id)
    except:
        abort(404)
    try:
        answer_id = int(answer_id)
    except:
        abort(404)
    if muser.require_login() or muser.getCurrentUser().isDisabled(): abort(403)
    if mforum.Forum.exists(forum_id):
        if mforum.Answer.exists(forum_id, answer_id):
            cuser = muser.getCurrentUser()
            answer = mforum.Answer(answer_id)
            article = answer.getArticle()
            forum = mforum.Forum.from_id(forum_id)
            if not answer.mayBeSeen(cuser):
                abort(404)
            if request.method == "GET":
                return render_template("forum/edit-answer.html", title="Antwort bearbeiten", thispage="courses" if forum_id != 0 else "forum", forum=forum, art=article, answer=answer)
            elif request.method == "POST":
                data = request.json
                body = data["body"].strip()
                comment = data["comment"].strip()
                errors, warnings = _validateBody(body, cuser, forum.id)

                if len(errors):
                    return jsonify({
                        "result": "error",
                        "errors": errors,
                        "warnings": warnings
                    })
                elif len(warnings) and request.values.get("ignore-warnings", 0) != "yes":
                    return jsonify({
                        "result": "warnings",
                        "warnings": warnings
                    })
                else:

                    if cuser.may("forum_reviewEdits") or cuser.id == article.getAuthor().id:

                        answer.setDetail("content", body)

                        answer.setDetail("last_edit_date", time.time())
                        answer.setDetail("last_activity_date", time.time())
                        article.setDetail("last_activity_date", time.time())

                        answer.addRevision(body, cuser, comment or "Beitrag bearbeitet")

                        return jsonify({
                            "result": "ok",
                            "url": "/f/"+str(forum.id)+"/"+str(article.id)+"#answer-" + str(answer.id)
                        })
    abort(404)

def forum_answer_revision(forum_id, answer_id, forum_label=None):
    try:
        forum_id = int(forum_id)
    except:
        abort(404)
    try:
        answer_id = int(answer_id)
    except:
        abort(405)
    if mforum.Forum.exists(forum_id):
        if mforum.Answer.exists(forum_id, answer_id):
            cuser = muser.getCurrentUser()
            answer = mforum.Answer(answer_id)
            article = mforum.Article(answer.getDetail("articleID"))
            forum = mforum.Forum.from_id(forum_id)
            if not answer.mayBeSeen(cuser):
                abort(404)
            return render_template("forum/revision-answer.html", title="Beitragsversionen", thispage="courses" if forum_id != 0 else "forum", forum=forum, post=answer, article=article, generate_diff=cdiff.generate_diff)
    abort(404)


def forum_answer_rollback(forum_id, answer_id, rev, forum_label=None):
    try:
        forum_id = int(forum_id)
    except:
        abort(404)
    try:
        rev = int(rev)
    except:
        abort(404)
    try:
        answer_id = int(answer_id)
    except:
        abort(404)
    cuser = muser.getCurrentUser()
    if not (cuser.may("forum_reviewEdits") or cuser.id == answer.getAuthor().id):
        abort(403)
    if mforum.Forum.exists(forum_id):
        if mforum.Answer.exists(forum_id, answer_id):
            answer = mforum.Answer(answer_id)
            article = mforum.Article(answer.getDetail("articleID"))
            forum = mforum.Forum.from_id(forum_id)
            if not answer.mayBeSeen(cuser):
                abort(404)
            form = dict(request.form)
            try:
                rev = answer.getRevisionById(rev)
            except:
                abort(404)
            if form == {}:
                return render_template("forum/rollback-answer.html", title="Beitragsversion wiederherstellen", thispage="courses" if forum_id != 0 else "forum", rev=rev, forum=forum, answer=answer, article=article)
            else:
                comment = request.form["comment"]
                answer.setDetail("content", rev["content"])
                answer.addRevision(rev["content"], cuser, u"Wiederherstellung einer früheren Version: " + comment)
            return redirect(url_for("forum_view", id=article.id, forum_id=forum_id) + "#answer-" + str(answer.id))
    abort(404)


def forum_post_flag(forum_id, post_id):
    post_id = post_id.split("-")
    if len(post_id) != 2: abort(404)
    if post_id[0] not in ["post", "answer"]: abort(404)
    try: post_id[1] = int(post_id[1])
    except: abort(404)
    if muser.require_login() or muser.getCurrentUser().isDisabled(): abort(403)
    data = request.json
    cuser = muser.getCurrentUser()
    el = mforum.Article if post_id[0] == "post" else mforum.Answer
    if el.exists(post_id[1]):
        E = el(post_id[1])
        if E.getDetail("forumID") != forum_id: abort(404)
        cuser = muser.getCurrentUser()
        article = E
        if not article.mayBeSeen(cuser):
            abort(404)

        data = request.json

        flag_type = data["flag-type"]
        comment = data["comment"]

        possible_list = ["custom"]
        if not article.isDeleted():
            possible_list += ["spam", "abuse"]
            if post_id[0] == "answer":
                possible_list += ["naa"]

        if not flag_type in possible_list: abort(400)

        message = flag_type if flag_type != "custom" else comment

        E.customflag(message, cuser)

        return "okay"
    abort(404)


def forum_post_vote(post_id):
    post_id = post_id.split("-")
    if len(post_id) != 2: abort(404)
    if post_id[0] not in ["post", "answer"]: abort(404)
    try: post_id[1] = int(post_id[1])
    except: abort(404)
    if muser.require_login() or muser.getCurrentUser().isDisabled():
        return jsonify({
            "result": "errpr",
            "error": "Du bist nicht angemeldet."
        })
    data = request.json
    cuser = muser.getCurrentUser()
    el = mforum.Article if post_id[0] == "post" else mforum.Answer
    if el.exists(post_id[1]):
        E = el(post_id[1])
        cuser = muser.getCurrentUser()
        if (not E.isDeleted() or E.mayBeSeen(cuser)) and not E.isFrozen():
            type = data["type"]

            if type == "up":
                if not E.getAuthor().id == cuser.id:
                    v, s = E.addVote(cuser, 1)
                    return jsonify({
                        "result": "success",
                        "update": { "vote": v, "score": s}
                    })
                else:
                    return jsonify({
                        "result": "error",
                        "error": "Du kannst nicht deinen eigenen Beitrag bewerten."
                    })

            elif type == "down":
                if not E.getAuthor().id == cuser.id:
                    v, s = E.addVote(cuser, -1)
                    return jsonify({
                        "result": "success",
                        "update": { "vote": v, "score": s}
                    })
                else:
                    return jsonify({
                        "result": "error",
                        "error": "Du kannst nicht deinen eigenen Beitrag bewerten."
                    })

            elif type == "delete":
                if not cuser.may("general_autoMod") and not cuser.isMod() and cuser.id != article.getAuthor().id:
                    return jsonify({
                        "result": "error",
                        "error": "Du kannst keine Beiträge löschen."
                    })
                if not E.isDeleted() and (not E.isFrozen() or cuser.isMod()):
                    if cuser.id == E.getAuthor().id:
                        E.setDetail("deleted", 1)
                        E.setDetail("deletionReason", "owner")
                        E.addRevComm("deleted", muser.User.from_id(-1), "seinem Urheber")
                        return jsonify({
                            "result": "success",
                            "update": { "deleted": True }
                        })
                    else:
                        E.delvote(cuser)
                        if E.getInfo()["deleted"] == 1:
                            return jsonify({
                                "result": "success",
                                "update": { "deleted": True }
                            })
                        return jsonify({
                            "result": "success",
                            "update": { "delvotes": E.getDelVotes() }
                        })

                else:
                    return jsonify({
                        "result": "error",
                        "error": "Beitrag kann nicht gelöscht werden: bereits gelöscht oder eingefroren."
                    })

            elif type == "undelete":
                if not cuser.may("general_autoMod") and not cuser.isMod() and cuser.id != E.getAuthor().id:
                    return jsonify({
                        "result": "error",
                        "error": "Du kannst keine Beiträge löschen."
                    })
                if E.isDeleted() and (not E.isFrozen() or cuser.isMod()):
                    if cuser.id == E.getAuthor().id:
                        E.setDetail("deleted", 0)
                        E.setDetail("deletionReason", "")
                        E.addRevComm("undeleted", cuser, "seinem Besitzer")
                        return jsonify({
                            "result": "success",
                            "update": { "deleted": False }
                        })
                    else:
                        E.undelvote(cuser)
                        if E.getInfo()["deleted"] == 0:
                            return jsonify({
                                "result": "success",
                                "update": { "deleted": False }
                            })
                        else:
                            return jsonify({
                                "result": "success",
                                "update": { "undelvotes": E.getUndelVotes() }
                            })

                else:
                    return jsonify({
                        "result": "error",
                        "error": "Beitrag kann nicht gelöscht werden: bereits un-gelöscht oder eingefroren."
                    })

            elif post_id[0] == "answer" and type == "accept":
                article = mforum.Article(E.getDetail("articleID"))
                op = article.getDetail("author")
                if op == -1:
                    op = article.getRevision(1)["editor"].id
                if op == cuser.id:

                    if article.hasAccepted() == 0:
                        E.setDetail("isAcceptedAnswer", 1)
                        article.setDetail("hasAcceptedAnswer", 1)
                        if E.getDetail("author") != op:
                            au = E.getAuthor()
                            if au.id != -1 and au.id != -3:
                                au.setReputationChange("forum_accept", "["+article.getHTMLTitle()+"](/f/"+str(article.getDetail("forumID"))+"/" + str(article.id) +"#answer-"+str(E.id)+")", 5)
                                au.setDetail("reputation", au.getDetail("reputation")+5)
                        return jsonify({
                            "result": "success",
                            "update": { "accepted": "answer-" + str(E.id) }
                        })
                    else:
                        if E.isAccepted():
                            E.setDetail("isAcceptedAnswer", 0)
                            article.setDetail("hasAcceptedAnswer", 0)
                            if E.getDetail("author") != op:
                                au = E.getAuthor()
                                if au.id != -1 and au.id != -3:
                                    au.setReputationChange("forum_accept", "["+article.getHTMLTitle()+"](/f/"+str(article.getDetail("forumID"))+"/" + str(article.id) +"#answer-"+str(E.id)+")", -5)
                                    au.setDetail("reputation", au.getDetail("reputation")-5)
                            return jsonify({
                                "result": "success",
                                "update": { "accepted": None }
                            })
                        else:
                            old = article.getAccepted()
                            old.setDetail("isAcceptedAnswer", 0)
                            if old.getDetail("author") != op:
                                au = old.getAuthor()
                                if au.id != -1 and au.id != -3:
                                    au.setReputationChange("forum_accept", "["+article.getHTMLTitle()+"](/f/"+str(article.getDetail("forumID"))+"/" + str(article.id) +"#answer-"+str(old.id)+")", -5)
                                    au.setDetail("reputation", au.getDetail("reputation")-5)
                            E.setDetail("isAcceptedAnswer", 1)
                            article.setDetail("hasAcceptedAnswer", 1)
                            if E.getDetail("author") != op:
                                au = E.getAuthor()
                                if au.id != -1 and au.id != -3:
                                    au.setReputationChange("forum_accept", "["+article.getHTMLTitle()+"](/f/"+str(article.getDetail("forumID"))+"/" + str(article.id) +"#answer-"+str(E.id)+")", 5)
                                    au.setDetail("reputation", au.getDetail("reputation")+5)
                            return jsonify({
                                "result": "success",
                                "update": { "accepted": "answer-" + str(E.id) }
                            })


            return jsonify({"result": "error", "error": "Ein Fehler ist aufgetreten."})
        else:
            return jsonify({
                "result": "error",
                "error": "Der Beitrag wurde nicht gefunden. Vielleicht wurde er bereits gelöscht oder er ist eingefroren."
            })
    else:
        return jsonify({
            "result": "error",
            "error": "Der Beitrag wurde nicht gefunden. Vielleicht wurde er bereits gelöscht."
        })


def forum_post_reopen(forum_id, id):
    try:
        id = int(id)
        forum_id = int(forum_id)
    except:
        return "Ungültige Anfrage. Bitte im globalen Forum melden!"
    data = request.json
    cuser = muser.getCurrentUser()
    if mforum.Article.exists(forum_id, id):
        article = mforum.Article(id)
        if not article.isDeleted():
            if not article.isClosed():
                return "Beitrag nicht geschlossen."
            if cuser.may("forum_closeQuestion"):
                x = article.reopen(cuser)
                if x:
                    return "{ok}"
                else:
                    return "Ein Fehler ist aufgetreten."
            else:
                return "Dir fehlt etwas Reputation, um Beiträge zu schließen."

        else:
            return "Der Beitrag wurde nicht gefunden. Vielleicht wurde er bereits gelöscht."
    else:
        return "Der Beitrag wurde nicht gefunden. Vielleicht wurde er bereits gelöscht."


def forum_answer_accept(forum_id, id):
    try:
        id = int(id)
        forum_id = int(forum_id)
    except:
        return "Ungültige Anfrage. Bitte im globalen Forum melden!"
    data = request.json
    cuser = muser.getCurrentUser()
    if mforum.Answer.exists(forum_id, id):
        answer = mforum.Answer(id)
        article = mforum.Article(E.getDetail("articleID"))
        op = article.getDetail("author")
        if op == -1:
            op = article.getRevision(1)["editor"].id
        if (cuser.id == op or op==-3 and cuser.isMod()) and not (answer.isFrozen() or article.isLocked()) and not answer.isDeleted() and not article.isDeleted():
            if article.hasAccepted() == 0:
                E.setDetail("isAcceptedAnswer", 1)
                article.setDetail("hasAcceptedAnswer", 1)
                if E.getDetail("author") != op:
                    au = E.getAuthor()
                    if au.id != -1 and au.id != -3:
                        au.setReputationChange("forum_accept", "["+article.getHTMLTitle()+"](/f/"+str(article.getDetail("forumID"))+"/" + str(article.id) +"#answer-"+str(answer.id)+")", 5)
                        au.setDetail("reputation", au.getDetail("reputation")+5)
                return jsonify({"checked": answer.id})
            else:
                if E.isAccepted():
                    E.setDetail("isAcceptedAnswer", 0)
                    E.setDetail("hasAcceptedAnswer", 0)
                    if E.getDetail("author") != op:
                        au = E.getAuthor()
                        if au.id != -1 and au.id != -3:
                            au.setReputationChange("forum_accept", "["+article.getHTMLTitle()+"](/f/"+str(article.getDetail("forumID"))+"/" + str(article.id) +"#answer-"+str(answer.id)+")", -5)
                            au.setDetail("reputation", au.getDetail("reputation")-5)
                    return jsonify({"checked": 0})
                else:
                    old = article.getAccepted()
                    old.setDetail("isAcceptedAnswer", 0)
                    if old.getDetail("author") != op:
                        au = old.getAuthor()
                        if au.id != -1 and au.id != -3:
                            au.setReputationChange("forum_accept", "["+article.getHTMLTitle()+"](/f/"+str(article.getDetail("forumID"))+"/" + str(article.id) +"#answer-"+str(old.id)+")", -5)
                            au.setDetail("reputation", au.getDetail("reputation")-5)
                    answer.setDetail("isAcceptedAnswer", 1)
                    article.setDetail("hasAcceptedAnswer", 1)
                    if answer.getDetail("author") != op:
                        au = answer.getAuthor()
                        if au.id != -1 and au.id != -3:
                            au.setReputationChange("forum_accept", "["+article.getHTMLTitle()+"](/f/"+str(article.getDetail("forumID"))+"/" + str(article.id) +"#answer-"+str(answer.id)+")", 5)
                            au.setDetail("reputation", au.getDetail("reputation")+5)
                    return jsonify({"checked": answer.id})
        else:
            return "Der Beitrag wurde nicht gefunden. Vielleicht wurde er bereits gelöscht oder er ist eingefroren."
    else:
        return "Der Beitrag wurde nicht gefunden. Vielleicht wurde er bereits gelöscht."

def forum_post_reopen(forum_id, id):
    try:
        id = int(id)
        forum_id = int(forum_id)
    except:
        return "Ungültige Anfrage. Bitte im globalen Forum melden!"
    data = request.json
    cuser = muser.getCurrentUser()
    if mforum.Article.exists(forum_id, id):
        article = mforum.Article(id)
        if not article.isDeleted():
            if not article.isClosed():
                return "Beitrag nicht geschlossen."
            if cuser.may("forum_closeQuestion"):
                x = article.reopen(cuser)
                if x:
                    return "{ok}"
                else:
                    return "Ein Fehler ist aufgetreten."
            else:
                return "Dir fehlt etwas Reputation, um Beiträge zu schließen."

        else:
            return "Der Beitrag wurde nicht gefunden. Vielleicht wurde er bereits gelöscht."
    else:
        return "Der Beitrag wurde nicht gefunden. Vielleicht wurde er bereits gelöscht."

def forum_comment(post_id):
    post_id = post_id.split("-")
    if len(post_id) != 2: abort(404)
    if post_id[0] not in ["post", "answer"]: abort(404)
    try: post_id[1] = int(post_id[1])
    except: abort(404)
    if muser.require_login() or muser.getCurrentUser().isDisabled(): abort(403)
    data = request.json
    cuser = muser.getCurrentUser()
    el = mforum.Article if post_id[0] == "post" else mforum.Answer
    if el.exists(post_id[1]):
        E = el(post_id[1])
        if not E.isDeleted() and not E.isFrozen():
            if post_id[0] == "post":
                master = E
            else:
                master = mforum.Article(E.getDetail("articleID"))
            if not E.getAuthor().id == cuser.id and not master.getAuthor().id == cuser.id and not cuser.may("forum_comment"):
                return jsonify({
                    "result": "error",
                    "error": "Du hast nicht genug Reputation, um Kommentare zu schreiben."
                })
            forum_id=master.getDetail("forumID")
            e = mforum.ForumComment.createNew(post_id[0], E.id, forum_id, cuser.id, data["content"])
            if post_id[0] == "post":
                E.getAuthor().notify("commented", "Es gibt einen neuen Kommentar auf deinen Foren-Beitrag \"" + E.getTitle() + "\"", "/f/"+str(forum_id)+"/"+str(E.id) + "#post-" + str(E.id) + "-comment-"+str(e.id))
            else:
                E.getAuthor().notify("commented", "Es gibt einen neuen Kommentar auf deine Antwort zum Forenbeitrag \"" + master.getTitle() + "\"", "/f/"+str(forum_id)+"/"+str(master.id) + "#answer-" + str(E.id) + "-comment-"+str(e.id))
            return jsonify({
                "result": "success"
            })
        else:
            return jsonify({
                "result": "error",
                "error": "Der Beitrag kann nicht kommentiert werden. Vielleicht wurde er bereits gelöscht oder er ist eingefroren."
            })
    else:
        return jsonify({
            "result": "error",
            "error": "Der Beitrag wurde nicht gefunden. Vielleicht wurde er bereits gelöscht."
        })

    return "ok"

def forum_purge_comments(post_id):
    post_id = post_id.split("-")
    if len(post_id) != 2: abort(404)
    if post_id[0] not in ["post", "answer"]: abort(404)
    try: post_id[1] = int(post_id[1])
    except: abort(404)

    cuser = muser.getCurrentUser()
    if not cuser.isMod():
        abort(404)
    el = mforum.Article if post_id[0] == "post" else mforum.Answer
    if el.exists(post_id[1]):
        E = el(post_id[1])
        for c in E.getComments(cuser.isMod()):
            if c.isDeleted(): continue
            c.setDetail("deleted", 1)
            c.setDetail("deletedby", cuser.id)

        return jsonify({
            "result": "success"
        })
    return jsonify({
        "result": "error",
        "error": "Der Beitrag wurde nicht gefunden. Vielleicht wurde er bereits gelöscht."
    })

    return "ok"

def forum_view_comments(post_id):
    post_id = post_id.split("-")
    if len(post_id) != 2: abort(404)
    if post_id[0] not in ["post", "answer"]: abort(404)
    try: post_id[1] = int(post_id[1])
    except: abort(404)

    cuser = muser.getCurrentUser()
    el = mforum.Article if post_id[0] == "post" else mforum.Answer
    if el.exists(post_id[1]):
        E = el(post_id[1])
        if not E.isDeleted() and not E.isFrozen():
            return jsonify({
                "result": "success",
                "render": render_template("forum/comments.html", post=E, type=post_id[0], with_deleted = cuser.isMod() and request.values.get("include-deleted")=="yes")
            })
    return jsonify({
        "result": "error",
        "error": "Der Beitrag wurde nicht gefunden. Vielleicht wurde er bereits gelöscht."
    })

    return "ok"

def forum_comment_vote(id):
    try:
        id = int(id)
    except:
        return jsonify({
            "result": "error",
            "error": "Ungültige Anfrage. Bitte im globalen Forum melden!"
        })

    data = request.json
    cuser = muser.getCurrentUser()

    if not cuser.isLoggedIn():
        return jsonify({
            "result": "error",
            "error": "Du musst dich anmelden, um Kommentare bewerten zu können."
        })

    try:
        e = mforum.ForumComment(id)
    except:
        return jsonify({
            "result": "error",
            "error": "Kommentar nicht gefunden"
        })

    if e.isDeleted() and not cuser.isMod():
        return jsonify({
            "result": "error",
            "error": "Kommentar nicht gefunden"
        })

    if data["vote"] == "up":
        if e.hasVote(cuser.id, "up", True):
            return jsonify({
                "result": "error",
                "error": "Du hast bereits für diesen Kommentar gestimmt."
            })
        elif cuser.id == e.getDetail("comment_author"):
            return jsonify({
                "result": "error",
                "error": "Du kannst nicht deine eigenen Kommentare bewerten."
            })

        e.setDetail("comment_score", e.getScore()+1)
        e.addVote(cuser.id, "up")

    elif data["vote"] == "delete":
        if cuser.id != e.getDetail("comment_author"):
            return jsonify({
                "result": "error",
                "error": "Fehlerhafte Anfrage"
            })

        e.setDetail("deleted", 1)
        e.setDetail("deletedby", cuser.id)

    elif data["vote"] == "kill":
        if not cuser.isMod():
            return jsonify({
                "result": "error",
                "error": "Fehlerhafte Anfrage"
            })

        e.setDetail("deleted", 1)
        e.setDetail("deletedby", cuser.id)

    elif data["vote"] == "restore":
        if not cuser.isMod():
            return jsonify({
                "result": "error",
                "error": "Fehlerhafte Anfrage"
            })

        e.setDetail("deleted", 0)
        e.setDetail("deletedby", 0)

    else:
        return jsonify({
            "result": "error",
            "error": "Fehlerhafte Anfrage"
        })

    e._ForumComment__data = e.getInfo()

    return jsonify({
        "result": "success",
        "score": e.getScore(),
        "deleted": e.isDeleted()
    })


def _validateQuestion(title, body, tags, cuser, forum_id):
    errors = []
    warnings = []

    if not cuser.isLoggedIn():
        errors.append(u"Du musst dich anmelden, bevor du eine Frage stellen kannst.")
    elif cuser.isDisabled():
        errors.append(u"Du bist gesperrt und darfst keine Fragen stellen.")

    if len(title) > 100:
        errors.append(u"Der Titel ist zu lang. Höchstens 100 Zeichen möglich. (aktuell: %i)" % len(title))
    elif len(title) < 10:
        errors.append(u"Der Titel ist zu kurz. Versuche das Problem ausführlich zu beschreiben. Mindestens zehn Zeichen erforderlich. (aktuell: %i)" % len(title))

    title = title.replace("<", "&lt;")
    title = title.replace("\"", "&quot;")
    title = title.replace(">", "&gt;")


    bodyMsg = _validateBody(body, cuser, id)
    errors += bodyMsg[0]
    warnings += bodyMsg[1]


    if len(tags) > 5:
        errors.append(u"Du hast zu viel Schlagwörter verwendet. Maximal 5 möglich. (aktuell: %i)" % len(tags))
    elif len(tags) < 1:
        errors.append(u"Füge mindestens ein Schlagwort hinzu. (aktuell: %i)" % len(tags))
    elif len(tags) < 2:
        warnings.append(u"Du hast nur ein Schlagwort verwendet. Wir empfehlen mindestens ein kategorisierendes Schlagwort (diskussion, support, fehler oder verbesserungsidee) und ein thematisches Schlagwort (z.B. forum oder polynomdivision).")

    for t in tags:

        if len(t) == 0:
            errors.append(u"Ein Schlagwort darf nicht leer sein.")
        elif len(t) > 25:
            errors.append(u"Ein Schlagwort darf nicht mehr als 25 Zeichen lang sein. ("+t+" hat %i)" % len(t))


        tagged = mtags.ForumTag.byName(t)
        if not tagged:
            tagged = mtags.ForumTag.byName(t, forum_id)
        if not tagged:
            continue
        if tagged.isModOnly() and not (cuser.isMod() or cuser.isTeam()):
            errors.append(u"Das Schlagwort " + t + u" kann nur von ♦-Moderatoren hinzugefügt werden.")
        if not tagged.isApplicable():
            if tagged.getDeprecationWarning():
                errors.append(u"Das Schlagwort " + t + u" darf nicht verwendet werden: " + tagged.getDeprecationWarning())
            else:
                errors.append(u"Das Schlagwort " + t + u" darf nicht verwendet werden.")
        elif tagged.getDeprecationWarning():
            warnings.append(tagged.getDeprecationWarning())

    return errors, warnings

def _validateBody(body, cuser, forum_id, isquestion=False):
    errors = []
    warnings = []

    if len(body) > 15000:
        errors.append(u"Der Inhalt ist zu lang. Höchstens 15.000 Zeichen möglich. (aktuell: %i)" % len(body))
    elif len(body) > 10000:
        warnings.append(u"Der Inhalt ist relativ lang (mehr als 10.000 Zeichen). Kannst du das nicht etwas kürzer fassen? (aktuell: %i)" % len(body))
    elif len(body) < 20:
        if isquestion:
            errors.append(u"Der Inhalt ist zu kurz. Versuche das Problem ausführlich zu beschreiben. Mindestens zwanzig Zeichen erforderlich. (aktuell: %i)" % len(body))
        else:
            errors.append(u"Der Inhalt ist zu kurz. Versuche ausführliche Antworten zu liefern, die erklären, wie und warum die Lösung korrekt ist. Mindestens zwanzig Zeichen erforderlich. (aktuell: %i)" % len(body))
    elif len(body) < 50:
        if isquestion:
            warnings.append(u"Der Inhalt ist etwas kurz. Versuche das Problem ausführlich zu beschreiben. Mindestens fünfzig Zeichen empfohlen. (aktuell: %i)" % len(body))
        else:
            warnings.append(u"Der Inhalt ist etwas kurz. Versuche ausführliche Antworten zu liefern, die erklären, wie und warum die Lösung korrekt ist.Mindestens fünfzig Zeichen empfohlen. (aktuell: %i)" % len(body))

    if (len(body) > 500 and body.count("\n\n") < 2) or (len(body) > 1500 and body.count("\n\n") < 4):
        warnings.append(u"Bitte gliedere deinen Text in Abschnitte (zwei Zeilenumbrücke). Das ermöglicht es potentiellen Antwortenden deinen Text einfacher zu lesen.")

    return errors, warnings


def apply(app):
    app.route('/f/<id>/new', methods=["GET", "POST"])(
        app.route('/forum/<id>/<label>/new', methods=["GET", "POST"])(forum_new)
    )
    app.route('/f/<id>')(
        app.route('/forum/<id>')(
            app.route('/forum/<id>/<label>')(forum_list)
        )
    )
    app.route('/f/<id>/tagged/<tag>')(
        app.route('/forum/<id>/tagged/<tag>')(
            app.route('/forum/<id>/<label>/tagged/<tag>')(forum_tag_view)
        )
    )
    app.route('/f/<id>/tag/<tag>/options', methods=["GET", "POST"])(
        app.route('/forum/<id>/tag/<tag>/options', methods=["GET", "POST"])(
            app.route('/forum/<id>/<label>/tag/<tag>/options', methods=["GET", "POST"])(forum_tag_options)
        )
    )
    app.route('/forum/<forum_id>/post/<post_id>/answer', methods=["POST"])(app.route('/forum/<forum_id>/<forum_label>/post/<post_id>/answer', methods=["POST"])(forum_post_answer))
    app.route('/forum/<forum_id>/<forum_label>/post/<post_id>/mod', methods=["POST"])(forum_post_mod)
    app.route('/forum/<forum_id>/<forum_label>/post/<post_id>/protect', methods=["POST"])(forum_post_protect)
    app.route('/forum/<forum_id>/<forum_label>/post/<post_id>/unprotect', methods=["POST"])(forum_post_unprotect)
    app.route('/forum/<forum_id>/post/<id>/reopen', methods=["POST"])(forum_post_reopen)
    app.route('/forum/<forum_id>/<forum_label>/post/<post_id>/edit', methods=["GET", "POST"])(app.route('/f/<forum_id>/post/<post_id>/edit', methods=["GET", "POST"])(forum_post_edit))
    app.route('/forum/<forum_id>/<forum_label>/post/<post_id>/rollback/<rev>', methods=["GET", "POST"])(forum_post_rollback)
    app.route('/forum/<forum_id>/<forum_label>/post/<post_id>/revisions', methods=["GET", "POST"])(app.route('/f/<forum_id>/post/<post_id>/rev', methods=["GET", "POST"])(forum_post_revision))
    app.route('/f/<forum_id>/<id>')(
        app.route('/forum/<forum_id>/a/<id>')(
            app.route('/forum/<forum_id>/<forum_label>/article/<id>')(
                app.route('/forum/<forum_id>/article/<id>/<label>')(
                    app.route('/forum/<forum_id>/<forum_label>/article/<id>/<label>')(forum_view)
                )
            )
        )
    )
    app.route('/forum/<forum_id>/<forum_label>/answer/<answer_id>/mod', methods=["POST"])(forum_answer_mod)
    app.route('/forum/<forum_id>/<forum_label>/answer/<answer_id>/edit', methods=["GET", "POST"])(app.route('/f/<forum_id>/answer/<answer_id>/edit', methods=["GET", "POST"])(forum_answer_edit))
    app.route('/forum/<forum_id>/<forum_label>/answer/<answer_id>/rollback/<rev>', methods=["GET", "POST"])(forum_answer_rollback)
    app.route('/forum/<forum_id>/<forum_label>/answer/<answer_id>/revisions', methods=["GET", "POST"])(forum_answer_revision)
    app.route('/forum/<post_id>/comments', methods=["GET"])(forum_view_comments)
    app.route('/forum/comments/<post_id>/add', methods=["POST"])(forum_comment)
    app.route('/forum/comments/<post_id>/purge', methods=["POST"])(forum_purge_comments)
    app.route('/forum/comments/<id>/vote', methods=["POST"])(forum_comment_vote)


    app.route('/forum/<post_id>/dialog', methods=["GET", "POST"])(forum_post_dialog)
    app.route('/forum/<int:forum_id>/<post_id>/flag', methods=["POST"])(forum_post_flag)
    app.route('/forum/<post_id>/vote', methods=["POST"])(forum_post_vote)
