# coding: utf-8
from flask import request, session, redirect, url_for, abort, render_template, jsonify
from model import user as muser, badges as mbadges
from controller import num as cnum, times as ctimes

import json, time

def badges_page():
    request.badge_prev=None
    def changed(l):
        b = l != request.badge_prev
        request.badge_prev = l
        return b
    return render_template("badges/list.html", title="Abzeichen", badges=sorted(mbadges.Badge.getAll(), key=lambda x:["bronze","silver","gold"].index(x.getClass())), changed=changed)

def apply(app):
    app.route('/badges')(badges_page)
