# coding: utf-8
from flask import request, session, redirect, url_for, abort, render_template, jsonify, g
from model import privileges as mprivileges, tags as mtags, user as muser, reviews as mreviews, forum as mforum, post_templates as mposttemplates
from controller import num as cnum, times as ctimes

import markdown as md

from sha1 import sha1
import json, time, pprint

def topbar_inbox():
    TYPES = {
      "helpdesk": "Helpdesk",
      "pm": "Moderatoren-Nachricht",
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

def topbar_update():
    cuser = muser.getCurrentUser()
    return jsonify({
        "badges": cuser.hasUnknownBadges(),
        "reputation": cuser.getRepDelta(),
        "messages": g.countNotifications(cuser.getNotifications())
    })

def apply(app):
    app.route('/topbar/inbox')(topbar_inbox)
    app.route('/topbar/user-info')(topbar_user_info)
    app.route('/topbar/rep-audit')(topbar_repaudit)
    app.route('/topbar/Update')(topbar_update)
