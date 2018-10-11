import os
import sqlite3 as lite
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
import user

def model__get_all_posts(forumid):
    con = lite.connect('databases/forum.db')
    con.row_factory = lite.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM fo_articles WHERE forum_id=? ORDER BY pinned DESC, election DESC,award DESC, state DESC, score DESC, id ASC", (forumid, ))
    data = cur.fetchall()
    return_value = []
    for row in data:
        teaser = row["content"]
        if len(teaser) > 200:
            teaser = teaser[:200] + "..."
        tags = row["tags"]
        tags = [tags[1:-1] for tags in tags.split("|")]
        return_value.append({
            "id": row["id"],
            "forum_id": row["forum_id"],
            "title": row["title"],
            "state": row["state"],
            "award": row["award"],
            "accepted_answer": bool(row["accepted_answer"]),
            "locked": row["locked"],
            "pinned": bool(row["pinned"]),
            "election": bool(row["election"]),
            "author": user.model__get_user_info(row["author"]),
            "score": row["score"],
            "teaser": teaser,
            "tags": tags
        })
    return return_value

def model__get_one_post(forumid, id):
    con = lite.connect('databases/forum.db')
    con.row_factory = lite.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM fo_articles WHERE forum_id=? AND id=? ORDER BY pinned DESC, election DESC,award DESC, state DESC, score DESC, id ASC", (forumid, id))
    data = cur.fetchone()
    if data is None:
        return None
    content = data["content"]
    tags = data["tags"]
    tags = [tags[1:-1] for tags in tags.split("|")]
    return_value = {
        "id": data["id"],
        "forum_id": data["forum_id"],
        "title": data["title"],
        "state": data["state"],
        "award": data["award"],
        "accepted_answer": bool(data["accepted_answer"]),
        "locked": data["locked"],
        "pinned": bool(data["pinned"]),
        "election": bool(data["election"]),
        "author": user.model__get_user_info(data["author"]),
        "score": data["score"],
        "content": content,
        "tags": tags,
        "lockMessage": data["lockMessage"],
        "closeMessage": data["closeMessage"],
        "modMessage": data["modMessage"],
        "deleteMessage": data["deleteReason"]
    }
    return return_value

def model__get_posts_answers(forumid, articleid):
    con = lite.connect('databases/forum.db')
    con.row_factory = lite.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM fo_answers WHERE forum_id=? AND article_id=? ORDER BY state DESC, is_accepted DESC, award DESC, score DESC, id ASC", (forumid, articleid))
    data = cur.fetchall()
    return_value = []
    for row in data:
        content = row["content"]
        return_value.append({
            "id": row["id"],
            "forum_id": row["forum_id"],
            "article_id": row["article_id"],
            "state": row["state"],
            "award": row["award"],
            "is_accepted": bool(row["is_accepted"]),
            "author": user.model__get_user_info(row["author"]),
            "score": row["score"],
            "content": content,
            "modMessage": row["modMessage"],
            "deleteMessage": row["deleteReason"]
        })
    return return_value

def model__get_one_answer(forumid, id):
    con = lite.connect('databases/forum.db')
    con.row_factory = lite.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM fo_answers WHERE forum_id=? AND id=?", (forumid, id))
    data = cur.fetchone()
    if data is None:
        return None
    content = data["content"]
    return_value = {
        "id": data["id"],
        "forum_id": data["forum_id"],
        "article_id": data["article_id"],
        "state": data["state"],
        "award": data["award"],
        "is_accepted": bool(data["is_accepted"]),
        "author": user.model__get_user_info(data["author"]),
        "score": data["score"],
        "content": content,
        "modMessage": data["modMessage"],
        "deleteMessage": data["deleteReason"]
    }
    return return_value

def model___delete_post(reason, post_type, post_id):
    con = lite.connect('databases/forum.db')
    con.row_factory = lite.Row
    cur = con.cursor()
    if post_type == "art":
        cur.execute("UPDATE fo_articles SET state=-1, deleteReason=? WHERE id=?", (reason, post_id))
        con.commit()
        return True
    elif post_type == "ans":
        cur.execute("UPDATE fo_answers SET state=0, deleteReason=? WHERE id=?", (reason, post_id))
        con.commit()
        return True
    return False

def model___destroy_post(post_type, post_id):
    con = lite.connect('databases/forum.db')
    con.row_factory = lite.Row
    cur = con.cursor()
    if post_type == "art":
        cur.execute("UPDATE fo_articles SET state=-5, content='', modMessage='', lockMessage='', locked=0, award=0, title=?, election=0, pinned=0, author=-2, score=0, tags='', closeReason='', closeMessage='', deleteReason='' WHERE id=?", ("Destroyed question #" + str(post_id), post_id))
        con.commit()
        return True
    elif post_type == "ans":
        cur.execute("UPDATE fo_answers SET state=-5, content='', award=0, is_accepted=0, author=-2, score=0, modMessage='', deleteReason='' WHERE id=?", (post_id,))
        con.commit()
        return True
    return False

def model___undelete_post(post_type, post_id):
    con = lite.connect('databases/forum.db')
    con.row_factory = lite.Row
    cur = con.cursor()
    if post_type == "art":
        cur.execute("UPDATE fo_articles SET state=1, deleteReason='' WHERE id=?", (post_id, ))
        con.commit()
        return True
    elif post_type == "ans":
        cur.execute("UPDATE fo_answers SET state=1, deleteReason='' WHERE id=?", (post_id, ))
        con.commit()
        return True
    return False

def model___adminize_post(post_type, post_id):
    con = lite.connect('databases/forum.db')
    con.row_factory = lite.Row
    cur = con.cursor()
    if post_type == "art":
        cur.execute("UPDATE fo_articles SET author=-1 WHERE id=?", (post_id, ))
        con.commit()
        return True
    elif post_type == "ans":
        cur.execute("UPDATE fo_answers SET author=-1 WHERE id=?", (post_id, ))
        con.commit()
        return True
    return False

def model___lock_post(post_id, type, msg):
    con = lite.connect('databases/forum.db')
    con.row_factory = lite.Row
    cur = con.cursor()
    cur.execute("UPDATE fo_articles SET locked=?, lockMessage=? WHERE id=?", (type, msg, post_id))
    con.commit()
    return True

def model___unlock_post(post_id):
    con = lite.connect('databases/forum.db')
    con.row_factory = lite.Row
    cur = con.cursor()
    cur.execute("UPDATE fo_articles SET locked=0, lockMessage='' WHERE id=?", (post_id, ))
    con.commit()
    return True

def model___set_award(forumid, post_id, amount):
    con = lite.connect('databases/forum.db')
    con.row_factory = lite.Row
    cur = con.cursor()
    cur.execute("UPDATE fo_articles SET award=? WHERE id=?", (amount, post_id))
    con.commit()
    return True

def model___set_pin(forumid, post_id, pinned):
    con = lite.connect('databases/forum.db')
    con.row_factory = lite.Row
    cur = con.cursor()
    cur.execute("UPDATE fo_articles SET pinned=? WHERE id=?", (pinned, post_id))
    con.commit()
    return True

def model___change_post_vote(post_type, post_id, vote):
    con = lite.connect('databases/forum.db')
    con.row_factory = lite.Row
    cur = con.cursor()
    if post_type == "art":
        cur.execute("UPDATE fo_articles SET score=? WHERE id=?", (vote, post_id))
        con.commit()
        return True
    elif post_type == "ans":
        cur.execute("UPDATE fo_answers SET score=? WHERE id=?", (vote, post_id))
        con.commit()
        return True
    return False

def model___has_not_voted_yet(userid, post_type, post_id, type_):
    con = lite.connect('databases/forum.db')
    con.row_factory = lite.Row
    cur = con.cursor()
    if post_type == "art":
        cur.execute("SELECT * FROM fo_votes WHERE user_id=? AND type=? AND target_id=? AND whatfor=?", (userid, type_, post_id, post_type))
        return not bool(cur.fetchone())
    elif post_type == "ans":
        cur.execute("SELECT * FROM fo_votes WHERE user_id=? AND type=? AND target_id=? AND whatfor=?", (userid, type_, post_id, post_type))
        return not bool(cur.fetchone())
    return False

def the_forum(stop, forumid, page, action):
    if page == "list":
        return forum_list(stop, forumid, action)
    elif page == "view":
        return forum_view(stop, forumid, action)
    elif page == "delete":
        return forum_delete(stop, forumid, action)
    elif page == "undelete":
        return forum_undelete(stop, forumid, action)
    elif page == "pin":
        return forum_pin(stop, forumid, action)
    elif page == "unpin":
        return forum_unpin(stop, forumid, action)
    elif page == "adminize":
        return forum_adminize(stop, forumid, action)
    elif page == "voteup":
        return forum_voteup(stop, forumid, action)
    elif page == "votedown":
        return forum_votedown(stop, forumid, action)
    elif page == "lock":
        return forum_lock(stop, forumid, action)
    elif page == "unlock":
        return forum_unlock(stop, forumid, action)
    elif page == "new":
        return forum_new(stop, forumid, action)
    elif page == "edit":
        return forum_edit(stop, forumid, action)
    elif page == "edit-answer":
        return forum_edit_answer(stop, forumid, action)
    elif page == "edit-modmsg":
        return forum_editmodmsg(stop, forumid, action)
    elif page == "add-answer":
        return forum_add_answer(stop, forumid, action)
    elif page == "edit-answer-modmsg":
        return forum_editanswermodmsg(stop, forumid, action)
    elif page == "setaward":
        return forum_setaward(stop, forumid, action)
    elif page == "destroy":
        return forum_destroy(stop, forumid, action)
    abort(405)

def forum_list(stop, forumid, action):
    thispage = "course" if forumid != 0 else "forum"
    the_posts = model__get_all_posts(forumid)
    return render_template('forum/list.html', stop=stop, title="Forumüberblick", thispage=thispage, posts=the_posts, forumid=forumid)

def forum_view(stop, forumid, action):
    thispage = "course" if forumid != 0 else "forum"
    the_post = model__get_one_post(forumid, action)
    if the_post == None:
        abort(400)
    answers = model__get_posts_answers(forumid, action)
    return render_template('forum/view.html', stop=stop, title="Forum – " + the_post["title"], thispage=thispage, post=the_post, forumid=forumid, answers=answers)

def forum_delete(stop, forumid, action):
    if len(action) < 4:
        abort(400)
    post_type, post_id = action[:3], int(action[3:])
    if post_type == "art":
        info = model__get_one_post(forumid, post_id)
        if stop["userid"] == info["author"]["id"] or stop["userrole"] == "m" or stop["userrole"] == "a":
            if stop["userid"] == info["author"]["id"]:
                reason = "Der Autor dieses Posts hat ihn gelöscht"
            else:
                reason = "Der Moderator [" + str(stop["username"]) + "](/user/view/id="+str(stop["userid"]) + ") hat diesen Post gelöscht"
            model___delete_post(reason, post_type, post_id)
        return redirect("/forum/f"+str(forumid)+"/view/" + str(post_id))
    elif post_type == "ans":
        info = model__get_one_answer(forumid, post_id)
        if stop["userid"] == info["author"]["id"] or stop["userrole"] == "m" or stop["userrole"] == "a":
            if stop["userid"] == info["author"]["id"]:
                reason = "Der Autor dieses Posts hat ihn gelöscht"
            else:
                reason = "Der Moderator [" + str(stop["username"]) + "](/user/view/id="+str(stop["userid"]) + ") hat diesen Post gelöscht"
            model___delete_post(reason, post_type, post_id)
        return redirect("/forum/f"+str(forumid)+"/view/" + str(info["article_id"])+"#answer-"+str(post_id))
    else:
        abort(404)

def forum_undelete(stop, forumid, action):
    if len(action) < 4:
        abort(400)
    post_type, post_id = action[:3], int(action[3:])
    if post_type == "art":
        info = model__get_one_post(forumid, post_id)
        if stop["userid"] == info["author"]["id"] or stop["userrole"] == "m" or stop["userrole"] == "a":
            model___undelete_post(post_type, post_id)
        return redirect("/forum/f"+str(forumid)+"/view/" + str(post_id))
    elif post_type == "ans":
        info = model__get_one_answer(forumid, post_id)
        if stop["userid"] == info["author"]["id"] or stop["userrole"] == "m" or stop["userrole"] == "a":
            model___undelete_post(post_type, post_id)
        return redirect("/forum/f"+str(forumid)+"/view/" + str(info["article_id"])+"#answer-"+str(post_id))
    else:
        abort(404)

def forum_adminize(stop, forumid, action):
    if len(action) < 4:
        abort(400)
    post_type, post_id = action[:3], int(action[3:])
    if post_type == "art":
        info = model__get_one_post(forumid, post_id)
        if stop["userrole"] == "m" or stop["userrole"] == "a":
            model___adminize_post(post_type, post_id)
        return redirect("/forum/f"+str(forumid)+"/view/" + str(post_id))
    elif post_type == "ans":
        info = model__get_one_answer(forumid, post_id)
        if stop["userrole"] == "m" or stop["userrole"] == "a":
            model___adminize_post(post_type, post_id)
        return redirect("/forum/f"+str(forumid)+"/view/" + str(info["article_id"]))
    else:
        abort(404)

def forum_voteup(stop, forumid, action):
    if len(action) < 4:
        abort(400)
    post_type, post_id = action[:3], int(action[3:])
    if post_type == "art":
        info = model__get_one_post(forumid, post_id)
        if stop["userid"] != info["author"]["id"]:
            if model___has_not_voted_yet(stop["userid"], post_type, post_id, "score"):
                model___change_post_vote(post_type, post_id, info["score"]+1)
                con = lite.connect('databases/forum.db')
                cur = con.cursor()
                cur.execute("INSERT INTO fo_votes (user_id, type, subtype, message, whatfor, target_id) VALUES (?, 'score', 'up', '', 'art', ?)", (stop["userid"], post_id))
                con.commit()
                con.close()
                if info["author"]["id"] > 0:
                    user.model___set_user_info(info["author"]["id"], "reputation", info["author"]["reputation"]+2)
        return redirect("/forum/f"+str(forumid)+"/view/" + str(post_id))
    elif post_type == "ans":
        info = model__get_one_answer(forumid, post_id)
        if stop["userid"] != info["author"]["id"]:
            if model___has_not_voted_yet(stop["userid"], post_type, post_id, "score"):
                print("# barrier 2")
                print(model___change_post_vote(post_type, post_id, info["score"]+1))
                con = lite.connect('databases/forum.db')
                cur = con.cursor()
                cur.execute("INSERT INTO fo_votes (user_id, type, subtype, message, whatfor, target_id) VALUES (?, 'score', 'up', '', 'ans', ?)", (stop["userid"], post_id))
                con.commit()
                con.close()
                if info["author"]["id"] > 0:
                    user.model___set_user_info(info["author"]["id"], "reputation", info["author"]["reputation"]+2)
        return redirect("/forum/f"+str(forumid)+"/view/" + str(info["article_id"])+"#answer-"+str(post_id))
    else:
        abort(404)

def forum_votedown(stop, forumid, action):
    if len(action) < 4:
        abort(400)
    post_type, post_id = action[:3], int(action[3:])
    if post_type == "art":
        info = model__get_one_post(forumid, post_id)
        if stop["userid"] != info["author"]["id"]:
            if model___has_not_voted_yet(stop["userid"], post_type, post_id, "score"):
                model___change_post_vote(post_type, post_id, info["score"]-1)
                con = lite.connect('databases/forum.db')
                cur = con.cursor()
                cur.execute("INSERT INTO fo_votes (user_id, type, subtype, message, whatfor, target_id) VALUES (?, 'score', 'down', '', 'art', ?)", (stop["userid"], post_id))
                con.commit()
                con.close()
                if info["author"]["id"] > 0:
                    user.model___set_user_info(info["author"]["id"], "reputation", info["author"]["reputation"]-1)
        return redirect("/forum/f"+str(forumid)+"/view/" + str(post_id))
    elif post_type == "ans":
        info = model__get_one_answer(forumid, post_id)
        if stop["userid"] != info["author"]["id"]:
            if model___has_not_voted_yet(stop["userid"], post_type, post_id, "score"):
                print("# barrier 2")
                print(model___change_post_vote(post_type, post_id, info["score"]-1))
                con = lite.connect('databases/forum.db')
                cur = con.cursor()
                cur.execute("INSERT INTO fo_votes (user_id, type, subtype, message, whatfor, target_id) VALUES (?, 'score', 'up', '', 'ans', ?)", (stop["userid"], post_id))
                con.commit()
                con.close()
                if info["author"]["id"] > 0:
                    user.model___set_user_info(info["author"]["id"], "reputation", info["author"]["reputation"]-1)
        return redirect("/forum/f"+str(forumid)+"/view/" + str(info["article_id"])+"#answer-"+str(post_id))
    else:
        abort(404)

def forum_new(stop, forumid, action):
    if request.method == "POST":
        con = lite.connect('databases/forum.db')
        cur = con.cursor()
        if "election" in request.form.keys():
            election = 1
        else:
            election = 0
        tags = request.form["tags"]
        tags = tags.split(",")
        tags = "|".join(["[" + tag + "]" for tag in tags])
        cur.execute("INSERT INTO fo_articles (forum_id, title, state, award, accepted_answer, locked, pinned, election, author, score, content, tags, closeReason, closeMessage, lockMessage, modMessage, deleteReason) VALUES (?, ?, '1', '0', '0', '0', '0', ?, ?, '0', ?, ?, '', '', '', '', '')", (forumid, request.form["title"], election, stop["userid"], request.form["content"], tags))
        con.commit()
        lrid = cur.lastrowid
        con.close()
        return redirect("forum/f"+str(forumid)+"/view/"+str(lrid))
    thispage = "course" if forumid != 0 else "forum"
    return render_template('forum/new.html', stop=stop, title="Forum – Neuen Beitrag posten", thispage=thispage, forumid=forumid)

def forum_editmodmsg(stop, forumid, action):
    try:
        action = int(action)
    except:
        abort(400)
    if stop["userrole"] == "m" or stop["userrole"] == "a":
        con = lite.connect('databases/forum.db')
        cur = con.cursor()
        if request.method == "POST":
            cur.execute("UPDATE fo_articles SET modMessage=? WHERE id=?", (request.form["message"], action))
            con.commit()
            con.close()
            return redirect("forum/f"+str(forumid)+"/view/"+str(action))
        else:
            cur.execute("SELECT modMessage FROM fo_articles WHERE id=?", (action,))
            modMessage = cur.fetchone()[0]
            con.close()
        thispage = "course" if forumid != 0 else "forum"
        return render_template('forum/edit-modmsg.html', stop=stop, title="Forum – Moderatorennachricht bearbeiten", thispage=thispage, post_id=action, forumid=forumid, current_message=modMessage)
    else:
        return redirect("forum/f"+str(forumid)+"/view/"+str(action))

def forum_editanswermodmsg(stop, forumid, action):
    try:
        action = int(action)
    except:
        abort(400)
    info = model__get_one_answer(forumid, action)
    if stop["userrole"] == "m" or stop["userrole"] == "a":
        con = lite.connect('databases/forum.db')
        cur = con.cursor()
        if request.method == "POST":
            cur.execute("UPDATE fo_answers SET modMessage=? WHERE id=?", (request.form["message"], action))
            con.commit()
            con.close()
            return redirect("forum/f"+str(forumid)+"/view/"+str(info["article_id"])+"#answer-"+str(action))
        else:
            cur.execute("SELECT modMessage FROM fo_answers WHERE id=?", (action,))
            modMessage = cur.fetchone()[0]
            con.close()
        thispage = "course" if forumid != 0 else "forum"
        return render_template('forum/edit-modmsg.html', stop=stop, title="Forum – Moderatorennachricht bearbeiten", thispage=thispage, post_id=str(info["article_id"])+"#answer-"+str(action), forumid=forumid, current_message=modMessage)
    else:
        return redirect("forum/f"+str(forumid)+"/view/"+str(info["article_id"])+"#answer-"+str(action))

def forum_edit(stop, forumid, action):
    try:
        action = int(action)
    except:
        abort(400)
    info = model__get_one_post(forumid, action)
    if stop["userrep"] > stop["priv"]["forum_reviewEdits"] or stop["userrole"] == "m" or stop["userrole"] == "a" or stop["userid"]==info["author"]["id"]:
        if request.method == "POST":
            con = lite.connect('databases/forum.db')
            cur = con.cursor()
            if "election" in request.form.keys():
                election = 1
            else:
                election = 0
            tags = request.form["tags"]
            tags = tags.split(",")
            tags = "|".join(["[" + tag + "]" for tag in tags])
            cur.execute("UPDATE fo_articles SET title=?, election=?, content=?, tags=? WHERE id=?", (request.form["title"], election, request.form["content"], tags, action))
            con.commit()
            con.close()
            return redirect("forum/f"+str(forumid)+"/view/"+str(action))
        else:
            title, election, content, tags = info["title"], info["election"], info["content"], info["tags"]
            tags = ",".join([i[1:-1] for i in tags.split("|")])
        thispage = "course" if forumid != 0 else "forum"
        return render_template('forum/edit.html', stop=stop, title="Forum – Neuen Beitrag posten", thispage=thispage, forumid=forumid, post_id=action, current_title=title, current_election=election, current_content=content, current_tags=tags)
    else:
        abort(400)

def forum_lock(stop, forumid, action):
    try:
        action = int(action)
    except:
        abort(400)
    if (stop["userrep"] >= stop["priv"]["forum_setProtection"]) or stop["userrole"] == "m" or stop["userrole"] == "a":
        if request.method == "POST":
            msg = request.form["message"]
            type  = request.form["type"]
            if type == "protect-spam":
                msg = "Dieser Post hat eine große Anzahl von beleidigenden oder SPAM-Inhalten angezogen und wurde darum geschützt. Um eine Antwort zu schreiben, brauchst du jetzt [mindestens 5 Reputationspunkte](/help/privileges#priv-table-forum_workAtProtected)."
            elif type == "stopped-hasans":
                msg = "Dieser Post hat bereits eine oder mehrere gute, gemeinschaftlich entstandene Antworten. Weitere Antworten sind unnötig. Falls du eine Ergänzung/Frage/Anmerkung hast oder ein ähnliches Problem hast, das nicht durch diesen Post beantwortet wird, schreibe eine neue Frage, in der du auch den Unterschied zu dieser betonen musst."
            elif type == "locked-historical":
                msg = "Dieser Post ist von historischer Relevanz, stellt allerdings kein gutes Beispiel für einen Post in diesem Forum dar. Weitere Änderungen an diesem Post sind untersagt."
            elif type == "locked-great":
                msg = "Dieser Post ist ein hervorragendes Musterbeispiel. Um Vandalismus zu verhindern, wurde er eingefroren."
            if type.startswith("protect-"):
                type = 1
            elif type.startswith("stopped-"):
                type = 2
            elif type.startswith("locked-"):
                type = 3
            print(type)
            model___lock_post(action, type, msg)
            return redirect("/forum/f"+str(forumid)+"/view/" + str(action))
        else:
            info = model__get_one_post(forumid, action)
            thispage = "course" if forumid != 0 else "forum"
            msg = info["lockMessage"]
            if msg == "Dieser Post hat eine große Anzahl von beleidigenden oder SPAM-Inhalten angezogen und wurde darum geschützt. Um eine Antwort zu schreiben, brauchst du jetzt [mindestens 5 Reputationspunkte](/help/privileges#priv-table-forum_workAtProtected).":
                type = "protect-spam"
            elif msg == "Dieser Post hat bereits eine oder mehrere gute, gemeinschaftlich entstandene Antworten. Weitere Antworten sind unnötig. Falls du eine Ergänzung/Frage/Anmerkung hast oder ein ähnliches Problem hast, das nicht durch diesen Post beantwortet wird, schreibe eine neue Frage, in der du auch den Unterschied zu dieser betonen musst.":
                type = "stopped-hasans"
            elif msg == "Dieser Post ist von historischer Relevanz, stellt allerdings kein gutes Beispiel für einen Post in diesem Forum dar. Weitere Änderungen an diesem Post sind untersagt.":
                type = "locked-historical"
            elif msg == "Dieser Post ist ein hervorragendes Musterbeispiel. Um Vandalismus zu verhindern, wurde er eingefroren.":
                type = "locked-great"
            else:
                if info["locked"] == 1:
                    type = "protect-other"
                elif info["locked"] == 2:
                    type = "stopped-other"
                elif info["locked"] == 3:
                    type = "locked-other"
                else:
                    type = ""
            return render_template('forum/lock.html', stop=stop, title="Forum – Post schützen", thispage=thispage, forumid=forumid, post_title=info["title"], post_id=action, current_type=type, current_message=info["lockMessage"])
    else:
        abort(404)

def forum_unlock(stop, forumid, action):
    try:
        action = int(action)
    except:
        abort(400)
    if stop["userrole"] == "m" or stop["userrole"] == "a":
        model___unlock_post(action)
        return redirect("/forum/f"+str(forumid)+"/view/" + str(action))
    else:
        abort(404)


def forum_add_answer(stop, forumid, action):
    try:
        action = int(action)
    except:
        abort(400)
    if request.method == "POST":
        con = lite.connect('databases/forum.db')
        cur = con.cursor()
        cur.execute("INSERT INTO fo_answers (forum_id, article_id, state, award, is_accepted, author, score, content, modMessage, deleteReason) VALUES (?, ?, '1', '0', '0', ?, '0', ?, '', '')", (forumid, action, stop["userid"], request.form["answer"]))
        con.commit()
        con.close()
        return redirect("forum/f"+str(forumid)+"/view/"+str(action))
    else:
        abort(400)

def forum_setaward(stop, forumid, action):
    try:
        action = int(action)
    except:
        return "error"
    if stop["userrep"] >= stop["priv"]["forum_setAward"]:
        model___set_award(forumid, action, request.json["amount"])
        user.model___set_user_info(stop["userid"], "reputation", stop["userrep"]-request.json["amount"])
        return "{ok}"
    else:
        return "error"

def forum_pin(stop, forumid, action):
    try:
        action = int(action)
    except:
        abort(400)
    if stop["userrole"] == "m" or stop["userrole"] == "a":
        model___set_pin(forumid, action, 1)
        return redirect("forum/f"+str(forumid)+"/view/"+str(action))
    else:
        abort(400)

def forum_unpin(stop, forumid, action):
    try:
        action = int(action)
    except:
        abort(400)
    if stop["userrole"] == "m" or stop["userrole"] == "a":
        model___set_pin(forumid, action, 0)
        return redirect("forum/f"+str(forumid)+"/view/"+str(action))
    else:
        abort(400)


def forum_destroy(stop, forumid, action):
    if len(action) < 4:
        abort(400)
    post_type, post_id = action[:3], int(action[3:])
    if post_type == "art":
        if stop["userrole"] == "a":
            model___destroy_post(post_type, post_id)
        return redirect("/forum/f"+str(forumid)+"/view/" + str(post_id))
    elif post_type == "ans":
        info = model__get_one_answer(forumid, post_id)
        if stop["userrole"] == "a":
            model___destroy_post(post_type, post_id)
        return redirect("/forum/f"+str(forumid)+"/view/" + str(info["article_id"])+"#answer-"+str(post_id))
    else:
        abort(404)


def forum_edit_answer(stop, forumid, action):
    try:
        action = int(action)
    except:
        abort(400)
    info = model__get_one_answer(forumid, action)
    if stop["userrep"] > stop["priv"]["forum_reviewEdits"] or stop["userrole"] == "m" or stop["userrole"] == "a" or stop["userid"]==info["author"]["id"]:
        if request.method == "POST":
            con = lite.connect('databases/forum.db')
            cur = con.cursor()
            cur.execute("UPDATE fo_answers SET content=? WHERE id=?", (request.form["content"], action))
            con.commit()
            con.close()
            return redirect("forum/f"+str(forumid)+"/view/"+str(info["article_id"])+"#answer-"+str(action))
        else:
            content = info["content"]
        thispage = "course" if forumid != 0 else "forum"
        return render_template('forum/edit-answer.html', stop=stop, title="Forum – Neuen Beitrag posten", thispage=thispage, forumid=forumid, post_id=action, post_master_id=info["article_id"], current_content=content)
    else:
        abort(400)