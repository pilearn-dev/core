# coding: utf-8
from flask import request, session, redirect, url_for, abort, render_template
from model import privileges as mprivileges, tags as mtags, user as muser, reviews as mreviews, forum as mforum, stats as mstats

def wrap_func(cb):
    def my_cb(*args, **kwargs):
        return cb(*args, **kwargs)
    return my_cb

QUEUES = {
    "post-closure": {
        "name": u"Beiträge schließen",
        "url": "post-closure",
        "desc": u"Entscheide ob Beiträge geschlossen werden sollen.",
        "queue": mreviews.PostClosure,
        "item_function": wrap_func(mforum.Article),
        "critical_open": 10,
        "required_privilege": "forum_closeQuestion",
        "template_inwork": "review/post-closure.html",
        "template_outcome": "review/post-closure-outcome.html",
        "flag_reasons": {
            "off-topic": u"nicht in dieses Forum passend",
            "unclear": u"unklar",
            "too-specific": u"zu spezifisch",
            "too-broad": u"zu allgemein",
            "other": u"in diesem Forum nicht mehr erwünscht",
            "duplicate": u"bereits gefragt und beantwortet"
        },
        "queue_results": [u"FEHLER!", u"Überspringen", u"schließen", u"bearbeiten", u"nicht schließen", u"Beitrag wurde gelöscht", u"Außerhalb dieser Liste geschlossen"],
        "may_ban": lambda u: u.isMod()
    },
    "post-reopen": {
        "name": u"Beiträge wieder öffnen",
        "url": "post-reopen",
        "desc": u"Entscheide ob geschlossene Beiträge wieder geöffnet werden sollen.",
        "queue": mreviews.PostReopen,
        "item_function": wrap_func(mforum.Article),
        "critical_open": 5,
        "required_privilege": "forum_closeQuestion",
        "template_inwork": "review/post-reopen.html",
        "template_outcome": "review/post-reopen-outcome.html",
        "flag_reasons": {
            "voted": u"Benutzer stimmten für das erneute Öffnen dieses Beitrags",
            "edited": u"Beitrag wurde nach der Schließung bearbeitet",
            "popular": u"Beitrag ist sehr populär",
            "disputed": u"Beitrag wurde schon zuvor geschlossen und danach wieder geöffnet."
        },
        "queue_results": [u"FEHLER!", u"Überspringen", u"öffnen", u"geschlossen lassen", u"Beitrag wurde gelöscht", u"Außerhalb dieser Liste geöffnet"],
        "may_ban": lambda u: u.isMod()
    },
    "post-deletion": {
        "name": u"Beiträge löschen",
        "url": "post-deletion",
        "desc": u"Entscheide ob Beiträge gelöscht werden sollen oder sogar gefährlich sind.",
        "queue": mreviews.PostDeletion,
        "item_function": wrap_func(mforum.Article),
        "critical_open": 5,
        "required_privilege": "forum_reviewEdits",
        "template_inwork": "review/post-deletion.html",
        "template_outcome": "review/post-deletion-outcome.html",
        "flag_reasons": {
            "delvote": u"Andere Benutzer verlangen die Löschung dieses Beitrags.",
            "spam": u"Andere Benutzer meinen, dass dies SPAM sein könnte.",
            "offensive": u"Andere Benutzer meinen, dass dies beleidigend sein könnte.",
            "autospam": u"Dieser Beitrag ist möglicherweise SPAM. **BITTE VORSICHTIG ÜBERPRÜFEN**",
            "autooffensive": u"Dieser Beitrag ist möglicherweise beleidigend. **BITTE VORSICHTIG ÜBERPRÜFEN**",
            "autofilter": u"Dieser Beitrag erfüllt eventuell unsere Qualitätsstandards nicht."
        },
        "queue_results": [u"FEHLER!", u"Überspringen", u"löschen", u"ist gefährlich", u"bearbeiten", u"keine Probleme gefunden", u"Beitrag wurde bearbeitet.", u"Beitrag wurde gelöscht."],
        "may_ban": lambda u: u.isMod()
    }
}
def review_start():
    cuser = muser.getCurrentUser()
    return render_template("review/start.html", thispage="review", title="Moderationslisten", queues=QUEUES.values())

def review_end(queue, action):
    if queue not in QUEUES.keys():
        abort(404)
    return render_template("review/end.html", thispage="review", title="Moderationslisten", queues=QUEUES.values(), action=action, single_queue=QUEUES[queue])

def flags_review(queue, id):
    if queue not in QUEUES.keys():
        abort(404)
    review = QUEUES[queue]
    cuser = muser.getCurrentUser()
    if id == "start":
        if not cuser.may(review["required_privilege"]):
            abort(404)
        id = review["queue"].getOpenItemId(cuser)
        if id == -1:
            return redirect(url_for("review_start"))
        return redirect(url_for("flags_review", id=id, queue=queue))
    elif id == "-1":
        return redirect(url_for("review_start"))
    try:
        id = int(id)
    except:
        abort(404)
    dat = review["queue"].getItemData(id)
    if dat == -1:
        abort(404)
    elif dat["state"] == 0 and cuser.may(review["required_privilege"]) and review["queue"].isOpenReview(id, cuser) and not cuser.isReviewBanned(queue):
        dat = dict(dat)
        dat["item"] = review["item_function"](dat["item_id"])
        flags = review["queue"].getItemFlags(id)
        flags_new = []
        tps = review["flag_reasons"]
        for flag in flags:
            flag = dict(flag)
            flag["reason"] = tps[flag["reason"]]
            flags_new.append(flag)
        reasons = [f["reason"] for f in flags_new]
        reasons = [(f, reasons.count(f)) for f in reasons]
        flag_reasons = set(reasons)
        flag_comments = [f["comment"] for f in flags_new if f["comment"] != ""]
        return render_template(review["template_inwork"], thispage="review", title="Moderationslisten - " + review["name"], data=dat, flag_reasons=flag_reasons, flag_comments=flag_comments, reviewqueue=review)
    else:
        dat = dict(dat)
        dat["item"] = review["item_function"](dat["item_id"])
        flags = review["queue"].getItemFlags(id)
        flags_new = []
        tps = review["flag_reasons"]
        for flag in flags:
            flag = dict(flag)
            flag["reason"] = tps[flag["reason"]]
            flags_new.append(flag)
        reasons = [f["reason"] for f in flags_new]
        reasons = [(f, reasons.count(f)) for f in reasons]
        flag_reasons = set(reasons)
        flag_comments = [f["comment"] for f in flags_new if f["comment"] != ""]
        tos = review["queue_results"]

        reviews = review["queue"].getReviews(id)

        print(flag_comments)
        return render_template(review["template_outcome"], thispage="review", title="Moderationslisten - "+review["name"], data=dat, flag_reasons=flag_reasons, flag_comments=flag_comments, reviews=reviews, tos=tos, reviewqueue=review)

def flags_action(queue, id):
    if queue not in QUEUES.keys():
        abort(404)
    review = QUEUES[queue]
    cuser = muser.getCurrentUser()
    if not cuser.may(review["required_privilege"]):
        abort(404)
    try:
        id = int(id)
    except:
        abort(404)

    data = request.json
    result = data["result"]
    msg = ""

    was_audit = 0#
    if queue == "post-closure":
        tps = {
            "off-topic": u"nicht in dieses Forum passend",
            "unclear": u"unklar",
            "too-specific": u"zu spezifisch",
            "too-broad": u"zu allgemein",
            "other": u"in diesem Forum nicht mehr erwünscht"
        }
        if result == 2:
            reason = data["reason"]
            subreason = data["subreason"]
            if subreason != None:
                msg = "**"+tps[reason]+"**: " + subreason
            else:
                msg = "**"+tps[reason]+"**"

    if queue == "post-closure":
        if result == 2:
            dat = review["queue"].getItemData(id)
            closa = review["item_function"](dat["item_id"])
            closa.close({
                "reason": reason,
                "message": subreason
            }, cuser, mreviews.PostClosure.isCompleted(id))
            if closa.getInfo()["closed"] == 1:
                mreviews.PostClosure.completeReview(id, 2)
        elif result == 3:
            closa = review["item_function"](dat["item_id"])
            title = request.json["new_title"]
            content = request.json["new_content"]
            tags = "|".join(["["+i+"]" for i in closa.getTags()])
            comment = "**Dieser Beitrag soll nicht geschlossen werden!**"
            article.setDetail("content", content)
            article.setDetail("title", title)
            article.addRevision(title, content, tags, cuser, comment)
            mreviews.UserFlags.completeReview(id, 3)
    elif queue == "post-reopen":
        if result == 2:
            dat = review["queue"].getItemData(id)
            reoa = review["item_function"](dat["item_id"])
            reoa.reopen(cuser, mreviews.PostClosure.isCompleted(id))
            if reoa.getInfo()["closed"] == 0:
                mreviews.UserFlags.completeReview(id, 2)
    elif queue == "post-deletion":
        if result == 2:
            dat = review["queue"].getItemData(id)
            closa = review["item_function"](dat["item_id"])
            closa.delvote(cuser, mreviews.PostClosure.isCompleted(id))
            if closa.getInfo()["closed"] == 1:
                mreviews.UserFlags.completeReview(id, 2)
        elif result == 4:
            closa = review["item_function"](dat["item_id"])
            title = request.json["new_title"]
            content = request.json["new_content"]
            tags = "|".join(["["+i+"]" for i in closa.getTags()])
            comment = "**Dieser Beitrag soll nicht gelöscht werden!**"
            article.setDetail("content", content)
            article.setDetail("title", title)
            article.addRevision(title, content, tags, cuser, comment)
            mreviews.UserFlags.completeReview(id, 3)

    review["queue"].addReview(id, cuser, result, msg)

    dat = review["queue"].getItemData(id)
    if dat["state"] != 0:
        if queue == "post-closure":
            if dat["result"] == 3:
                review["queue"].markFlags(id, -1)
            elif dat["result"] == 4:
                review["queue"].markFlags(id, -2)
        elif queue == "post-reopen":
            if dat["result"] == 3:
                review["queue"].markFlags(id, -2)
        elif queue == "post-deletion":
            if dat["result"] == 4:
                review["queue"].markFlags(id, -1)
            elif dat["result"] == 5:
                review["queue"].markFlags(id, -2)

    if was_audit == 0:
        return url_for("flags_review", queue=queue, id="start")
    elif was_audit == 1:
        return url_for("review_end", queue=queue, action="test-passed")
    else:
        return url_for("review_end", queue=queue, action="test-failure")

def flags_ban(queue):
    if queue not in QUEUES.keys():
        abort(404)
    review = QUEUES[queue]
    cuser = muser.getCurrentUser()
    if not review["may_ban"](cuser):
        abort(404)
    u = muser.User.from_id(request.json["user"])
    action = request.json["action"]
    if action == "ban":
        if not u.isReviewBanned(queue):
            u.imposeReviewBan(queue, cuser, request.json["msg"])
            return "{ok}";
        return "Benutzer bereits gesperrt."
    elif action == "unban":
        if u.isReviewBanned(queue):
            u.invalidateReviewBan(queue, cuser)
            return "{ok}";
        return "Benutzer bereits entsperrt."
    return "Ein Fehler ist aufgetreten."


def flags_act(queue, id):
    cuser = muser.getCurrentUser()
    if queue not in ["mod", "admin"]:
        return "Dies ist keine gültige Meldungsliste."
    cuser = muser.getCurrentUser()
    if not cuser.isMod():
        return "Du bist kein Moderator und kannst diese Aktion daher nicht machen."
    if queue == "admin" and not cuser.isAdmin():
        return "Du bist kein Administrator und kannst diese Aktion daher nicht machen."
    q = {
        "mod": mreviews.ModQueue,
        "admin": mreviews.AdminQueue
    }
    q = q[queue]
    data = q.getItemData(id)
    print(data)
    if not data:
        return "Meldung nicht gefunden."
    req = request.json
    fid = req["id"]
    state = req["state"]
    flag = q.getFlagData(fid)
    if not flag:
        return "Meldung nicht gefunden."
    elif flag["state"] != 0:
        return "Meldung wurde bereits bearbeitet."
    q.manageFlag(id, fid, state, "")
    return "{ok}"

def flags_complete(queue, id):
    cuser = muser.getCurrentUser()
    if queue not in ["mod", "admin"]:
        abort(404)
    cuser = muser.getCurrentUser()
    if not cuser.isMod():
        abort(404)
    if queue == "admin" and not cuser.isAdmin():
        abort(404)
    q = {
        "mod": mreviews.ModQueue,
        "admin": mreviews.AdminQueue
    }
    q = q[queue]
    data = q.getItemData(id)
    if data == False:
        abort(404)
    if data["state"] == 0:
        q.completeReview(id)
    return url_for("flags_page")

def data_page():
    cuser = muser.getCurrentUser()
    if not cuser.isDev():
        abort(404)
    hasLargeModTraffic = mreviews.ModQueue.getOpenItemCount() > HIGH_MOD_TRAFFIC
    return render_template("review/data/index.html", thispage="review", title="Moderationslisten", hasLargeModTraffic=hasLargeModTraffic)

def data_subpage(x):
    cuser = muser.getCurrentUser()
    if not cuser.isDev():
        abort(404)
    hasLargeModTraffic = mreviews.ModQueue.getOpenItemCount() > HIGH_MOD_TRAFFIC
    return render_template("review/data/"+x+".html", thispage="review", title="Moderationslisten", hasLargeModTraffic=hasLargeModTraffic, Statistics=mstats)

def apply(app):
    app.route('/review')(app.route('/review/start')(review_start))
    app.route('/review/<queue>/ban', methods=["POST"])(flags_ban)
    app.route('/review/<queue>/<id>')(flags_review)
    app.route('/review/add-review/<queue>/<id>', methods=["POST"])(flags_action)
    app.route('/review/finished/<queue>/<action>')(review_end)
    app.route("/data")(data_page)
    app.route("/data/<x>")(data_subpage)
