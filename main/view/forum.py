# coding: utf-8
from flask import request, session, redirect, url_for, abort, render_template, jsonify
from model import privileges as mprivileges, tags as mtags, user as muser, forum as mforum
from controller import diff as cdiff
from sha1 import sha1

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
            return render_template("forum/list.html", forum=forum, thispage="course" if id != 0 else "forum", title=forum.getDetail("name"), search=request.values.get("query", False))
    else:
        abort(404)

def forum_new(id, label=None):
    try:
        id = int(id)
    except:
        abort(404)
    if mforum.Forum.exists(id):
        forum = mforum.Forum.from_id(id)
        cuser = muser.getCurrentUser()
        if label != forum.getDetail("label"):
            return redirect(url_for("forum_new", id=id, label=forum.getDetail("label")))
        else:
            if request.form == {}:
                return render_template("forum/new.html", forum=forum, thispage="course" if id != 0 else "forum", title=forum.getDetail("name"))
            else:
                form = dict(request.form)
                title = u"[Kein Titel gesetzt]"
                content = u"[Kein Inhalt gesetzt]"
                tags = u"[kein-tag]"
                comment = u"Ursprüngliche Version"
                if "content" in form.keys():
                    content = request.form["content"]
                if "title" in form.keys():
                    title = request.form["title"]
                if "tags" in form.keys():
                    tags = "|".join(["["+i+"]" for i in request.form["tags"].split(",")])
                article = mforum.Article.createNew(id, title, content, tags, cuser)
                article.addRevision(title, content, tags, cuser, comment)
                return redirect("/f/"+str(id)+"/"+str(article.id))
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
    if mforum.Forum.exists(forum_id):
        forum = mforum.Forum.from_id(forum_id)
        cuser = muser.getCurrentUser()
        if mforum.Article.exists(forum_id, post_id):
            article = mforum.Article(post_id)
            if request.form == {}:
                abort(405)
            else:
                form = dict(request.form)
                content = u"[Kein Inhalt gesetzt]"
                comment = u"Ursprüngliche Version"
                if "answer" in form.keys():
                    content = request.form["answer"]
                answer = mforum.Answer.createNew(forum_id, post_id, content, cuser)
                answer.addRevision(content, cuser, comment)
                au = article.getAuthor()
                if au.id == -1:
                    answer.setDetail("author", -1)
                    answer.addRevComm("anonymized", cuser, "-1")
                elif au.id != -3:
                    au.notify("answered", "Es gibt eine neue Antwort auf deinen Foren-Beitrag \"" + article.getTitle() + "\"", "/f/"+str(forum_id)+"/"+str(post_id) + "#answer-" + str(answer.id))
                return redirect("/f/"+str(forum_id)+"/"+str(post_id) + "#answer-" + str(answer.id))
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
                    return render_template("forum/view.html", forum=forum, post=article, thispage="course" if forum_id != 0 else "forum", title=forum.getDetail("name"))
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
    except:
        abort(404)
    try:
        post_id = int(post_id)
    except:
        abort(404)#
    if mforum.Forum.exists(forum_id):
        if mforum.Article.exists(forum_id, post_id):
            cuser = muser.getCurrentUser()
            article = mforum.Article(post_id)
            forum = mforum.Forum.from_id(forum_id)
            if not article.mayBeSeen(cuser):
                abort(404)
            form = dict(request.form)
            if form == {}:
                return render_template("forum/edit-post.html", title="Beitrag bearbeiten", thispage="course" if forum_id != 0 else "forum", forum=forum, article=article)
            else:
                if cuser.may("forum_reviewEdits") or cuser.id == article.getAuthor().id:
                    title = article.getTitle()
                    content = article.getContent()
                    tags = "|".join(["["+i+"]" for i in article.getTags()])
                    comment = "Beitrag wurde von **[" + cuser.getDetail("name") + "](" + str(cuser.id) + ")** bearbeitet."
                    if "comment" in form.keys():
                        comment = request.form["comment"]
                    if "content" in form.keys():
                        content = request.form["content"]
                        article.setDetail("content", request.form["content"])
                    if "title" in form.keys():
                        title = request.form["title"]
                        article.setDetail("title", request.form["title"])
                    if "tags" in form.keys():
                        tags = "|".join(["["+i+"]" for i in request.form["tags"].split(",")])
                        article.setDetail("tags", "|".join(["["+i+"]" for i in request.form["tags"].split(",")]))
                    article.addRevision(title, content, tags, cuser, comment)
                return redirect(url_for("forum_view", id=post_id, forum_id=forum_id))
    abort(404)

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
            return render_template("forum/revision-post.html", title="Beitragsversionen", thispage="course" if forum_id != 0 else "forum", forum=forum, post=article, generate_diff=cdiff.generate_diff)
    abort(404)

def forum_post_delete(forum_id, post_id, forum_label=None):
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
            article = mforum.Article(post_id)
            if not cuser.may("general_autoMod") and not cuser.isMod() and cuser.id != article.getAuthor().id:
                abort(404)
            if not article.isDeleted() and (not article.isFrozen() or cuser.isMod()):
                if cuser.id == article.getAuthor().id:
                    article.setDetail("deleted", 1)
                    article.setDetail("deletionReason", "owner")
                    article.addRevComm("deleted", muser.User.from_id(-1), article.getDeleteMessage())
                else:
                    article.delvote(cuser)
            return "ok"
    abort(404)

def forum_post_destroy(forum_id, post_id, forum_label=None):
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
            if not cuser.isMod():
                abort(404)
            article = mforum.Article(post_id)
            if not article.isDestroyed():
                article.setDetail("deleted", 2)
                article.addRevComm("destroyed", cuser, "")
            return "ok"
    abort(404)

def forum_post_undelete(forum_id, post_id, forum_label=None):
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
            if not cuser.may("general_autoMod") and not cuser.isMod() and cuser.id != article.getAuthor().id:
                abort(404)
            article = mforum.Article(post_id)
            if article.isDeleted() and (not article.isFrozen() or cuser.isMod()):
                if article.getDetail("deletionReason") == "owner" and cuser.id == article.getAuthor().id:
                    article.setDetail("deleted", 0)
                    article.addRevComm("undeleted", cuser, "seinem Besitzer")
                else:
                    article.undelvote(cuser)
            return "ok"
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
                return render_template("forum/rollback-post.html", title="Beitragsversion wiederherstellen", thispage="course" if forum_id != 0 else "forum", rev=rev, forum=forum, article=article)
            else:
                comment = request.form["comment"]
                article.setDetail("content", rev["content"])
                article.setDetail("title", rev["title"])
                article.setDetail("tags", rev["tags"])
                print(rev)
                article.addRevision(rev["title"], rev["content"], rev["tags"], cuser, u"**Wiederherstellung einer früheren Version**: " + comment)
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
        abort(404)#
    if mforum.Forum.exists(forum_id):
        if mforum.Answer.exists(forum_id, answer_id):
            cuser = muser.getCurrentUser()
            answer = mforum.Answer(answer_id)
            forum = mforum.Forum.from_id(forum_id)
            if not answer.mayBeSeen(cuser):
                abort(404)
            form = dict(request.form)
            if form == {}:
                return render_template("forum/edit-answer.html", title="Beitrag bearbeiten", thispage="course" if forum_id != 0 else "forum", forum=forum, answer=answer)
            else:
                if cuser.may("forum_reviewEdits") or cuser.id == answer.getAuthor().id:
                    content = answer.getContent()
                    comment = "Beitrag wurde von **[" + cuser.getDetail("name") + "](" + str(cuser.id) + ")** bearbeitet."
                    if "comment" in form.keys():
                        comment = request.form["comment"]
                    if "content" in form.keys():
                        content = request.form["content"]
                        answer.setDetail("content", request.form["content"])
                    answer.addRevision(content, cuser, comment)
                return redirect(url_for("forum_view", id=answer.getDetail("articleID"), forum_id=forum_id))
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
            return render_template("forum/revision-answer.html", title="Beitragsversionen", thispage="course" if forum_id != 0 else "forum", forum=forum, post=answer, article=article, generate_diff=cdiff.generate_diff)
    abort(404)

def forum_answer_delete(forum_id, answer_id, forum_label=None):
    try:
        forum_id = int(forum_id)
    except:
        abort(404)
    try:
        answer_id = int(answer_id)
    except:
        abort(404)
    if mforum.Forum.exists(forum_id):
        if mforum.Answer.exists(forum_id, answer_id):
            cuser = muser.getCurrentUser()
            if not cuser.may("general_autoMod") and not cuser.isMod():
                abort(404)
            answer = mforum.Answer(answer_id)
            if not answer.isDeleted() and (not answer.isFrozen() or cuser.isMod()):
                answer.setDetail("deleted", 1)
                answer.addRevComm("deleted", cuser, "")
            return "ok"
    abort(404)

def forum_answer_destroy(forum_id, answer_id, forum_label=None):
    try:
        forum_id = int(forum_id)
    except:
        abort(404)
    try:
        answer_id = int(answer_id)
    except:
        abort(404)
    if mforum.Forum.exists(forum_id):
        if mforum.Answer.exists(forum_id, answer_id):
            cuser = muser.getCurrentUser()
            if not cuser.isMod():
                abort(404)
            answer = mforum.Answer(answer_id)
            if not answer.isDestroyed():
                answer.setDetail("deleted", 2)
                answer.addRevComm("destroyed", cuser, "")
            return "ok"
    abort(404)

def forum_answer_undelete(forum_id, answer_id, forum_label=None):
    try:
        forum_id = int(forum_id)
    except:
        abort(404)
    try:
        answer_id = int(answer_id)
    except:
        abort(404)
    if mforum.Forum.exists(forum_id):
        if mforum.Answer.exists(forum_id, answer_id):
            cuser = muser.getCurrentUser()
            if not cuser.may("general_autoMod") and not cuser.isMod():
                abort(404)
            answer = mforum.Answer(answer_id)
            if answer.isDeleted() and (not answer.isFrozen() or cuser.isMod()):
                answer.setDetail("deleted", 0)
                answer.addRevComm("undeleted", cuser, "")
            return "ok"
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
                rev = answer.getRevision(rev)
            except:
                abort(404)
            if form == {}:
                return render_template("forum/rollback-answer.html", title="Beitragsversion wiederherstellen", thispage="course" if forum_id != 0 else "forum", rev=rev, forum=forum, answer=answer, article=article)
            else:
                comment = request.form["comment"]
                answer.setDetail("content", rev["content"])
                answer.addRevision(rev["content"], cuser, "### Wiederherstellung von Version " + str(rev["revid"]) + ":\n\n" + comment)
            return redirect(url_for("forum_view", id=article.id, forum_id=forum_id))
    abort(404)


def forum_post_flag(forum_id, id):
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
            if data["type"] == "flag":
                if cuser.may("forum_flag"):
                    if data["reason"] == "close":
                        if article.isClosed():
                            return "Beitrag bereits geschlossen."
                        data["reason"] = data["subreason"]
                        data["message"] = ""
                        print(data)
                        x = article.closeflag(data, cuser)
                    elif data["reason"] == "duplicate":
                        if article.isClosed():
                            return "Beitrag bereits geschlossen."
                        data["message"] = data["subreason"]
                        x = article.closeflag(data, cuser)
                    elif data["reason"] == "other":
                        message = data["message"]
                        x = article.customflag(message, cuser)
                    if x:
                        return "{ok}"
                    else:
                        return "Ein Fehler ist aufgetreten."
                else:
                    return "Dir fehlt etwas Reputation, um Beiträge zu melden."
            elif data["type"] == "close":
                if article.isClosed():
                    return "Beitrag bereits geschlossen."
                if cuser.may("forum_closeQuestion"):
                    if data["reason"] == "other" and not cuser.isMod():
                        return u"Nur Moderatoren können Beiträge wegen `Anderes` schließen."
                    if data["reason"] != "duplicate":
                        if data["reason"] != "off-topic":
                            data["message"] = ""
                        else:
                            data["message"] = data["subreason"]
                        x = article.close(data, cuser)
                    elif data["reason"] == "duplicate":
                        data["message"] = data["subreason"]
                        x = article.close(data, cuser)
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


def forum_post_vote(forum_id, id):
    try:
        id = int(id)
        forum_id = int(forum_id)
    except:
        return "Ungültige Anfrage. Bitte im globalen Forum melden!"
    data = request.json
    cuser = muser.getCurrentUser()
    if mforum.Article.exists(forum_id, id):
        article = mforum.Article(id)
        if not article.isDeleted() and not article.isFrozen():
            if not article.getAuthor().id == cuser.id:
                v, s = article.addVote(cuser, data["direction"])
            else:
                v, s = 0, article.getScore()
            return jsonify({"checked": v, "score": s})
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


def forum_answer_vote(forum_id, id):
    try:
        id = int(id)
        forum_id = int(forum_id)
    except:
        return "Ungültige Anfrage. Bitte im globalen Forum melden!"
    data = request.json
    cuser = muser.getCurrentUser()
    if mforum.Answer.exists(forum_id, id):
        answer = mforum.Answer(id)
        if not answer.isDeleted() and not answer.isFrozen():
            if not answer.getAuthor().id == cuser.id:
                v, s = answer.addVote(cuser, data["direction"])
            else:
                v, s = 0, answer.getScore()
            return jsonify({"checked": v, "score": s})
        else:
            return "Der Beitrag wurde nicht gefunden. Vielleicht wurde er bereits gelöscht oder er ist eingefroren."
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
        article = mforum.Article(answer.getDetail("articleID"))
        op = article.getDetail("author")
        if op == -1:
            op = article.getRevision(1)["editor"].id
        if (cuser.id == op or op==-3 and cuser.isMod()) and not (answer.isFrozen() or article.isLocked()) and not answer.isDeleted() and not article.isDeleted():
            if article.hasAccepted() == 0:
                answer.setDetail("isAcceptedAnswer", 1)
                article.setDetail("hasAcceptedAnswer", 1)
                if answer.getDetail("author") != op:
                    au = answer.getAuthor()
                    if au.id != -1 and au.id != -3:
                        au.setReputationChange("forum_accept", "["+article.getHTMLTitle()+"](/f/"+str(article.getDetail("forumID"))+"/" + str(article.id) +"#answer-"+str(answer.id)+")", 5)
                        au.setDetail("reputation", au.getDetail("reputation")+5)
                return jsonify({"checked": answer.id})
            else:
                if answer.isAccepted():
                    answer.setDetail("isAcceptedAnswer", 0)
                    article.setDetail("hasAcceptedAnswer", 0)
                    if answer.getDetail("author") != op:
                        au = answer.getAuthor()
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

def forum_comment(forum_id, post_type, id):
    try:
        id = int(id)
        forum_id = int(forum_id)
        assert post_type in ["post", "answer"]
    except:
        return "Ungültige Anfrage. Bitte im globalen Forum melden!"
    data = request.json
    cuser = muser.getCurrentUser()
    el = mforum.Article if post_type == "post" else mforum.Answer
    if el.exists(forum_id, id):
        E = el(id)
        if not E.isDeleted() and not E.isFrozen():
            if post_type == "post":
                master = E
            else:
                master = mforum.Article(E.getDetail("articleID"))
            if not E.getAuthor().id == cuser.id and not master.getAuthor().id == cuser.id and not cuser.may("forum_comment"):
                return "Du hast nicht genug Reputation um Kommentare zu schreiben."
            e = mforum.ForumComment.createNew(post_type, E.id, forum_id, cuser.id, data["content"])
            if post_type == "post":
                E.getAuthor().notify("commented", "Es gibt einen neuen Kommentar auf deinen Foren-Beitrag \"" + E.getTitle() + "\"", "/f/"+str(forum_id)+"/"+str(id) + "#post-" + str(E.id) + "-comment-"+str(e.id))
            else:
                E.getAuthor().notify("commented", "Es gibt einen neuen Kommentar auf deine Antwort zum Forenbeitrag \"" + master.getTitle() + "\"", "/f/"+str(forum_id)+"/"+str(master.id) + "#answer-" + str(E.id) + "-comment-"+str(e.id))
            return jsonify(e.id)
        else:
            return "Der Beitrag kann nicht kommentiert werden. Vielleicht wurde er bereits gelöscht oder er ist eingefroren."
    else:
        return "Der Beitrag wurde nicht gefunden. Vielleicht wurde er bereits gelöscht."

def forum_comment_vote(forum_id, id):
    try:
        id = int(id)
        forum_id = int(forum_id)
    except:
        return "Ungültige Anfrage. Bitte im globalen Forum melden!"
    data = request.json
    cuser = muser.getCurrentUser()
    try:
        e = mforum.ForumComment(id)
    except:
        return "Kommentar nicht gefunden"
    if e.isDeleted() and not cuser.isMod():
        return "Kommentar nicht gefunden"
    if data["type"] == "delete":
        if cuser.id != e.getDetail("comment_author"):
            return "Fehlerhafte Anfrage"
        e.setDetail("deleted", 1)
        e.setDetail("deletedby", cuser.id)
    elif data["type"] == "kill":
        if not cuser.isMod():
            return "Fehlerhafte Anfrage"
        e.setDetail("deleted", 1)
        e.setDetail("deletedby", cuser.id)
    elif data["type"] == "restore":
        if not cuser.isMod():
            return "Fehlerhafte Anfrage"
        e.setDetail("deleted", 0)
        e.setDetail("deletedby", 0)
    else:
        return "Fehlerhafte Anfrage"
    return "{ok}"


def apply(app):
    app.route('/f/<id>/new', methods=["GET", "POST"])(
        app.route('/forum/<id>/<label>/new', methods=["GET", "POST"])(forum_new)
    )
    app.route('/f/<id>')(
        app.route('/forum/<id>')(
            app.route('/forum/<id>/<label>')(
                app.route('/forum/<id>/<label>/list')(forum_list)
            )
        )
    )
    app.route('/f/<forum_id>/post/<post_id>/answer', methods=["POST"])(app.route('/forum/<forum_id>/<forum_label>/post/<post_id>/answer', methods=["POST"])(forum_post_answer))
    app.route('/forum/<forum_id>/<forum_label>/post/<post_id>/delete', methods=["POST"])(app.route('/f/<forum_id>/post/<post_id>/delete', methods=["POST"])(forum_post_delete))
    app.route('/forum/<forum_id>/<forum_label>/post/<post_id>/destroy', methods=["POST"])(forum_post_destroy)
    app.route('/forum/<forum_id>/<forum_label>/post/<post_id>/undelete', methods=["POST"])(app.route('/f/<forum_id>/post/<post_id>/undelete', methods=["POST"])(forum_post_undelete))
    app.route('/forum/<forum_id>/<forum_label>/post/<post_id>/mod', methods=["POST"])(forum_post_mod)
    app.route('/forum/<forum_id>/<forum_label>/post/<post_id>/protect', methods=["POST"])(forum_post_protect)
    app.route('/forum/<forum_id>/<forum_label>/post/<post_id>/unprotect', methods=["POST"])(forum_post_unprotect)
    app.route('/forum/<forum_id>/post/<id>/flag', methods=["POST"])(forum_post_flag)
    app.route('/forum/<forum_id>/post/<id>/vote', methods=["POST"])(forum_post_vote)
    app.route('/forum/<forum_id>/post/<id>/reopen', methods=["POST"])(forum_post_reopen)
    app.route('/forum/<forum_id>/<forum_label>/post/<post_id>/edit', methods=["GET", "POST"])(forum_post_edit)
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
    app.route('/forum/<forum_id>/<forum_label>/answer/<answer_id>/delete', methods=["POST"])(app.route('/f/<forum_id>/answer/<answer_id>/delete', methods=["POST"])(forum_answer_delete))
    app.route('/forum/<forum_id>/<forum_label>/answer/<answer_id>/destroy', methods=["POST"])(forum_answer_destroy)
    app.route('/forum/<forum_id>/<forum_label>/answer/<answer_id>/undelete', methods=["POST"])(app.route('/f/<forum_id>/answer/<answer_id>/undelete', methods=["POST"])(forum_answer_undelete))
    app.route('/forum/<forum_id>/<forum_label>/answer/<answer_id>/mod', methods=["POST"])(forum_answer_mod)
    app.route('/forum/<forum_id>/<forum_label>/answer/<answer_id>/edit', methods=["GET", "POST"])(forum_answer_edit)
    app.route('/forum/<forum_id>/<forum_label>/answer/<answer_id>/rollback/<rev>', methods=["GET", "POST"])(forum_answer_rollback)
    app.route('/forum/<forum_id>/<forum_label>/answer/<answer_id>/revisions', methods=["GET", "POST"])(forum_answer_revision)
    app.route('/forum/<forum_id>/answer/<id>/vote', methods=["POST"])(forum_answer_vote)
    app.route('/forum/<forum_id>/answer/<id>/accept', methods=["POST"])(forum_answer_accept)
    app.route('/forum/<forum_id>/<post_type>/<id>/comment', methods=["POST"])(forum_comment)
    app.route('/forum/<forum_id>/comment/<id>/vote', methods=["POST"])(forum_comment_vote)
