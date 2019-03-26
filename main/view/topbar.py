# coding: utf-8
from flask import request, session, redirect, url_for, abort, render_template, jsonify
from model import privileges as mprivileges, tags as mtags, user as muser, reviews as mreviews, forum as mforum, post_templates as mposttemplates
from controller import num as cnum, times as ctimes

import markdown as md

from sha1 import sha1
import json, time

def topbar_inbox():
    TYPES = {
      "helpdesk": "Helpdesk",
      "pm": "Admin-Nachricht",
      "ping": "Benutzer-PING",
      "answered": "Neue Antwort",
      "commented": "Neuer Kommentar",
      "proposal_accept": "Kursvorschlag angenommen"
    }
    cuser = muser.getCurrentUser()
    cuser.hideNotifications()
    return render_template("topbar/inbox.html", types=TYPES)

def topbar_repaudit():
    cuser = muser.getCurrentUser()
    dat = []
    for x in cuser.getReputationChanges():
        x["amount_text"] = cnum.num2suff(x["amount"])
        x["message_html"] = md.markdown(x["message"])
        x["count"] = 1
        if len(dat) >0 and x["message"] == dat[-1]["message"]:
            dat[-1]["count"] += 1
            dat[-1]["amount"] += x["amount"]
            dat[-1]["amount_text"] = cnum.num2suff(dat[-1]["amount"])
        else:
            print x["message"]
            dat.append(x)
        if len(dat) == 20:
            break
    cuser.knowReputationChanges()
    print dat
    return render_template("topbar/rep-audit.html", data=dat)

def topbar_user_info():
    return render_template("topbar/user-info.html")

def apply(app):
    app.route('/topbar/inbox')(topbar_inbox)
    app.route('/topbar/user-info')(topbar_user_info)
    app.route('/topbar/rep-audit')(topbar_repaudit)