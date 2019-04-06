# coding: utf-8
from flask import request, session, redirect, url_for, abort, render_template, jsonify
from model import privileges as mprivileges, tags as mtags, user as muser, reviews as mreviews, forum as mforum, post_templates as mposttemplates
from controller import num as cnum, times as ctimes

import markdown as md

from sha1 import sha1
import json, time, pprint

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
    for x in cuser.getTopbarAwards():
        if x["type"] == "reputation":
            x["message_html"] = md.markdown(x["label"])
            x["count"] = 1
            if len(dat) >0 and dat[-1]["type"] == "reputation" and x["label"] == dat[-1]["label"] and x["given_date"] - dat[-1]["given_date"] < 24*3600:
                dat[-1]["count"] += 1
                dat[-1]["data"] += x["data"]
            else:
                dat.append(x)
        elif x["type"] == "badge":
            dat.append(x)
    cuser.knowReputationChanges()
    cuser.knowNewBadges()
    request.prev=None
    def changed(l):
        b = l != request.prev
        request.prev = l
        return b
    return render_template("topbar/rep-audit.html", data=dat, now=time.time(), changed=changed)

def topbar_user_info():
    return render_template("topbar/user-info.html")

def apply(app):
    app.route('/topbar/inbox')(topbar_inbox)
    app.route('/topbar/user-info')(topbar_user_info)
    app.route('/topbar/rep-audit')(topbar_repaudit)
