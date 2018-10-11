import os
import sqlite3 as lite
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from user import model__is_enrolled, model__do_enroll

def list(stop, value=None):
    con = None
    try:
        con = lite.connect('databases/courses.db')
        con.row_factory = lite.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM courses")
        data = cur.fetchall()
        now_courses = []
        my_courses = []
        soon_courses = []
        for row in data:
            if row["state"] == 0:
                continue
            if row["state"] == 1:
                tbl = soon_courses
            elif model__is_enrolled(stop["userid"], row["id"]):
                tbl = my_courses
            else:
                tbl = now_courses
            tbl.append({
                "id": row["id"],
                "title": row["title"],
                "shortdesc": row["shortdesc"],
            })
    except lite.Error as e:
        print(e)
        abort(500)
        return
    finally:
        if con:
            con.close()
    return render_template('courses/list.html', my_courses=my_courses, now_courses=now_courses, soon_courses=soon_courses, stop=stop, title="Kursüberblick", thispage="course")

def details(stop, value=None):
    if not value.startswith("id="):
        abort(400)
    value = value[len("id="):]
    try:
        value = int(value)
    except:
        abort(400)
    con = None
    try:
        con = lite.connect('databases/courses.db')
        con.row_factory = lite.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM courses WHERE id='"+str(value)+"'")
        data = dict(cur.fetchone())
        if data["state"] == 1:
            data["rel"] = "soon"
        else:
            data["rel"] = "now"
        print(value)
        cur.execute("SELECT * FROM authorship WHERE user_id=? AND course_id=?", (stop["userid"], value))
        data["is_author"] = cur.fetchone() is not None
    except lite.Error as e:
        abort(500)
        return
    finally:
        if con:
            con.close()
    return render_template('courses/details.html', data=data, stop=stop, title="Kurs " + data['title'], thispage="course")


def proposal(stop, value=None):
    try:
        value = int(value)
    except:
        abort(400)
    con = None
    try:
        con = lite.connect('databases/courses.db')
        con.row_factory = lite.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM course_proposals WHERE id='"+str(value)+"'")
        data = cur.fetchone()
        if not data:
            abort(400)
        data = dict(data)

        cur.execute("SELECT vote FROM proposal_votes WHERE prop_id=? AND user_id=?", (value, stop["userid"]))
        d2 = cur.fetchone()
        if d2 is None:
            user = {"acceptance":0}
        else:
            user = {"acceptance":d2["vote"]}
    except lite.Error as e:
        abort(500)
        return
    finally:
        if con:
            con.close()
    return render_template('courses/proposal.html', the_proposal=data, stop=stop, title="Kursvorschlag " + data['title'], thispage="course", user=user)

def accept_proposal(stop, value=None):
    try:
        value = int(value)
    except:
        abort(400)
    con = None
    try:
        con = lite.connect('databases/courses.db')
        cur = con.cursor()
        cur.execute("SELECT score FROM course_proposals WHERE id='"+str(value)+"'")
        score = cur.fetchone()[0]
        if stop["userrole"] != "a":
            score += 1
            cur.execute("INSERT INTO proposal_votes VALUES (?,?,1)", (value, stop["userid"]))
        
        if score == 5 or stop["userrole"] == "a":
            cur.execute("UPDATE course_proposals SET score=?, state=1 WHERE id='"+str(value)+"'", (score,))
        else:
            cur.execute("UPDATE course_proposals SET score=? WHERE id='"+str(value)+"'", (score,))
        con.commit()
    except lite.Error as e:
        abort(500)
        return
    finally:
        if con:
            con.close()
    return redirect("/course/proposal/"+str(value))

def decline_proposal(stop, value=None):
    try:
        value = int(value)
    except:
        abort(400)
    con = None
    try:
        con = lite.connect('databases/courses.db')
        cur = con.cursor()
        cur.execute("SELECT score FROM course_proposals WHERE id='"+str(value)+"'")
        score = cur.fetchone()[0]
        if stop["userrole"] != "a":
            score -= 1
            cur.execute("INSERT INTO proposal_votes VALUES (?,?,-1)", (value, stop["userid"]))
        
        if score == 5 or stop["userrole"] == "a":
            cur.execute("UPDATE course_proposals SET score=?, state=-1 WHERE id='"+str(value)+"'", (score,))
        else:
            cur.execute("UPDATE course_proposals SET score=? WHERE id='"+str(value)+"'", (score,))
        con.commit()
    except lite.Error as e:
        abort(500)
        return
    finally:
        if con:
            con.close()
    return redirect("/course/proposal/"+str(value))

def propose(stop, value=None):
    if request.method == 'POST':
        try:
            con = lite.connect('databases/courses.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            data = (request.form['proposal_title'], request.form['shortdesc'], request.form['longdesc'], request.form['materials'], stop['userid'])
            cur.execute("INSERT INTO course_proposals (title, shortdesc, longdesc, materials, state, author, score) VALUES (?,?,?,?,0,?,0)", data)
            con.commit()
        except lite.Error as e:
            print(e)
            abort(500)
            return
        finally:
            if con:
                con.close()
        return render_template('courses/propose.html', state="success", stop=stop, title="Kurs vorschlagen", thispage="course")
    return render_template('courses/propose.html', state="unknown", stop=stop, title="Kurs vorschlagen", thispage="course")

def enroll(stop, value=None):
    if not value.startswith("id="):
        abort(400)
    value = value[len("id="):]
    try:
        value = int(value)
    except:
        abort(400)
    model__do_enroll(stop["userid"], value)
    return redirect(url_for("course_", action="list"))

views = {
    "list": list,
    "details": details,
    "enroll": enroll,
    "propose": propose,
    "proposal":proposal,
    "accept-proposal":accept_proposal,
    "decline-proposal":decline_proposal
}