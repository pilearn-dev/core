# coding: utf-8
from flask import request, session, redirect, url_for, abort, render_template, jsonify
from model import privileges as mprivileges, tags as mtags, user as muser, reviews as mreviews, forum as mforum, post_templates as mposttemplates
from controller import num as cnum, times as ctimes, mail as cmail

import markdown as md

from sha1 import sha1
import json, time
import urllib, urllib2

def helpdesk_page():
    return render_template("helpdesk.html", title="Helpdesk", submit=bool(request.values.get("submit", False)))

def helpdesk_submit():
    cuser = muser.getCurrentUser()
    if not cuser.isLoggedIn():
        abort(404)

    rt = request.form.get("request-type")
    rc = request.form.get("description")
    secure = rt.endswith("_")
    if secure:
        rt = rt[:-1]
    rm = cuser.getDetail("email")

    id = str(int(time.time()))

    cmail.send_textbased_email("team@pilearn.de", u"HD #" + id + u" von Benutzer #" + str(cuser.id), u"Es gibt eine neue Support-Anfrage.\n\nTyp: " + rt + u"\n\nKommentar:\n\n" + rc + u"\n\n---\n\nAntwort an: " + rm + (" (mod)" if cuser.isMod() else "") + (" (team)" if cuser.isTeam() else ""))

    time.sleep(1)

    if secure:
        cmail.send_textbased_email(rm, "Support-Anfrage #"+id+" entgegengenommen", u"Hallo " + cuser.getDetail("realname") + u",\n\nwir haben deine Support-Anfrage vom Typ " + rt + u" entgegengenommen. Sie hat die Kennung #"+id+u".\n\nWenn du noch etwas hinzufügen möchtest, sende eine E-Mail mit dieser Kennung an team@pilearn.de.\n\nViele Grüße\n\n&pi;-Learn Team")
    else:
        cmail.send_textbased_email(rm, "Support-Anfrage #"+id+" entgegengenommen", u"Hallo " + cuser.getDetail("realname") + u",\n\nwir haben deine Support-Anfrage vom Typ " + rt + u" entgegengenommen. Sie hat die Kennung #"+id+u". Folgendes ist dein Kommentar:\n\n"+rc+u"\n\nWenn du noch etwas hinzufügen möchtest, sende eine E-Mail mit dieser Kennung an team@pilearn.de.\n\nViele Grüße\n\n&pi;-Learn Team")

    return redirect(url_for("helpdesk_page", submit=True))

def apply(app):
    app.route('/helpdesk')(helpdesk_page)
    app.route('/helpdesk/submit', methods=["POST"])(helpdesk_submit)
