import os
import sqlite3 as lite
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

def index(stop, value=None):
    data = {"course_proposals":0}
    try:
        con = lite.connect('databases/courses.db')
        #con.row_factory = lite.Row
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM course_proposals WHERE state=0")
        data["course_proposals"] = cur.fetchone()[0]
    except lite.Error as e:
        print(e)
    finally:
        if con:
            con.close()
    return render_template('review/index.html', data=data, stop=stop, title="Moderationslisten – Überblick", thispage="review")

def course_proposals(stop, value=None):
    abort(405)
    return
    if value != None:
        try:
            print(value)
            con = lite.connect('databases/courses.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            if value == "skip":
                cur.execute("UPDATE course_proposals SET actor='-3', state=? WHERE id=?", ("1", request.form["id"]))
            elif value == "accept":
                cur.execute("UPDATE course_proposals SET title=?, shortdesc=?, longdesc=?, materials=?, state=? WHERE id=?", (request.form['proposal_title'], request.form['shortdesc'], request.form['longdesc'], request.form['materials'], "1", request.form["id"]))
                cur.execute("INSERT INTO courses (title, shortdesc, longdesc, materials, state, getcert, highqual, admincourse) VALUES (?,?,?,?,'1','0','0','0')", (request.form['proposal_title'], request.form['shortdesc'], request.form['longdesc'], request.form['materials']))
            elif value == "deny":
                cur.execute("UPDATE course_proposals SET title=?, shortdesc=?, longdesc=?, materials=?, state=? WHERE id=?", (request.form['proposal_title'], request.form['shortdesc'], request.form['longdesc'], request.form['materials'], "-1", request.form["id"]))
            con.commit()
        except lite.Error as e:
            print(e)
            return ""
        finally:
            if con:
                con.close()
    proposal={"exists": False}
    try:
        con = lite.connect('databases/courses.db')
        con.row_factory = lite.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM course_proposals WHERE state=0 AND actor=?", (stop["userid"], ))
        data = cur.fetchone()
        if data is None:
            cur.execute("SELECT * FROM course_proposals WHERE state=0 AND actor='-3' ORDER BY RANDOM() LIMIT 1")
            data = cur.fetchone()
        if data is not None:
            if data["actor"] == -3:
                cur.execute("UPDATE course_proposals SET actor=? WHERE id=?", (stop["userid"], data["id"]))
                con.commit()
            proposal["exists"] = True
            proposal["id"] = data["id"]
            proposal["title"] = data["title"]
            proposal["shortdesc"] = data["shortdesc"]
            proposal["longdesc"] = data["longdesc"]
            proposal["material"] = data["materials"]
    except lite.Error as e:
        print(e)
    finally:
        if con:
            con.close()
    return render_template('review/course_proposals.html', stop=stop, title="Moderationslisten – Kursvorschläge", thispage="review", proposal=proposal)

views = {
    "index": index,
    "course-proposals": course_proposals
}