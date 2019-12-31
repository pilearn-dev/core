# coding: utf-8
from flask import Blueprint, request, session, redirect, url_for, abort, render_template, jsonify, escape
from model import privileges as mprivileges, tags as mtags, user as muser, reviews as mreviews, forum as mforum, post_templates as mposttemplates
from controller import num as cnum, times as ctimes, mail as cmail

import markdown as md

from sha1 import sha1
import json, time
import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse

helpdesk = Blueprint('helpdesk', __name__)

@helpdesk.route("/")
def index():
    return render_template("helpdesk.html", title="Helpdesk", submit=bool(request.values.get("submit", False)))

@helpdesk.route("/submit", methods=["POST"])
def submit():
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

    cmail.send_textbased_email("team@pilearn.de", "HD #" + id + " von Benutzer #" + str(cuser.id), "Es gibt eine neue Support-Anfrage.\n\nTyp: " + rt + "\n\nKommentar:\n\n" + escape(rc) + "\n\n---\n\nAntwort an: " + rm + (" (mod)" if cuser.isMod() else "") + (" (team)" if cuser.isTeam() else ""))

    time.sleep(1)

    if secure:
        cmail.send_textbased_email(rm, "Support-Anfrage #"+id+" entgegengenommen", "Hallo " + cuser.getDetail("realname") + ",\n\nwir haben deine Support-Anfrage vom Typ " + rt + " entgegengenommen. Sie hat die Kennung #"+id+".\n\nWenn du noch etwas hinzufügen möchtest, sende eine E-Mail mit dieser Kennung an team@pilearn.de.\n\nViele Grüße\n\n&pi;-Learn Team")
    else:
        cmail.send_textbased_email(rm, "Support-Anfrage #"+id+" entgegengenommen", "Hallo " + cuser.getDetail("realname") + ",\n\nwir haben deine Support-Anfrage vom Typ " + rt + " entgegengenommen. Sie hat die Kennung #"+id+". Folgendes ist dein Kommentar:\n\n"+rc+"\n\nWenn du noch etwas hinzufügen möchtest, sende eine E-Mail mit dieser Kennung an team@pilearn.de.\n\nViele Grüße\n\n&pi;-Learn Team")

    return redirect(url_for("helpdesk.index", submit=True))
