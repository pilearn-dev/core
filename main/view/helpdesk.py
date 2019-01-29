# coding: utf-8
from flask import request, session, redirect, url_for, abort, render_template, jsonify
from model import privileges as mprivileges, tags as mtags, user as muser, reviews as mreviews, forum as mforum, post_templates as mposttemplates
from controller import num as cnum, times as ctimes

import markdown as md

from sha1 import sha1
import json, time
import urllib, urllib2

def helpdesk_page():
    cuser = muser.getCurrentUser()
    if cuser.isDev():
        return redirect("https://support.pilearn.velja.de/admin")

    return render_template("helpdesk.html", title="Helpdesk", submit=bool(request.values.get("submit", False)))

def helpdesk_submit():
    cuser = muser.getCurrentUser()
    if cuser.isDev():
        return redirect("https://support.pilearn.velja.de/admin")
    if not cuser.isLoggedIn():
        abort(404)

    rt = request.form.get("request-type")
    rc = request.form.get("description")

    def encoded_dict(in_dict):
        out_dict = {}
        for k, v in in_dict.iteritems():
            if isinstance(v, unicode):
                v = v.encode('utf8')
            elif isinstance(v, str):
                # Must be encoded in UTF-8
                v.decode('utf8')
            out_dict[k] = v
        return out_dict

    data = urllib.urlencode(encoded_dict({
        "staff": False,
        "email": "pstrobach15@gmail.com",
        "password": "12345678",
        "userId": 9
    }))

    r = urllib2.urlopen("https://support.pilearn.velja.de/api/user/login", data)

    print(r.getcode())
    print(r.read())

    data = urllib.urlencode(encoded_dict({
        "title": rt + "- Benutzer #" + str(cuser.id),
        "content": "<p><strong>Anfrage</strong>: " + rt + "</p><p><strong>Benutzer</strong>: <a href='https://www.pilearn.de/u/"+str(cuser.id)+"'>"+cuser.getHTMLName()+"</a></p><hr>"+md.markdown(rc),
        "departmentId": 4,
        "language": "german",
        "email": unicode(cuser.getDetail("email")),
        "images": 0
    }))
    r = urllib2.urlopen("https://support.pilearn.velja.de/api/ticket/create", data)
    print(r.getcode())
    print(r.read())
    return "..."

def apply(app):
    app.route('/helpdesk')(helpdesk_page)
    app.route('/helpdesk/submit', methods=["POST"])(helpdesk_submit)
