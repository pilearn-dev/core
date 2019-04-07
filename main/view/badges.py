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

def badges_single(id):
    if not mbadges.Badge.exists(id):
        abort(404)
    badge = mbadges.Badge(id)
    return render_template("badges/single.html", title="Abzeichen " + badge.getName(), b=badge)

def badges_award(id):
    if not mbadges.Badge.exists(id):
        abort(404)
    if not muser.getCurrentUser().isDev():
        abort(403)
    badge = mbadges.Badge(id)
    data = request.form["data"]
    if not data:
        data = None
    badge.awardTo(request.form["to"], data)
    return redirect(url_for("badges_single", id=id))

def badges_revoke(id):
    if not mbadges.Badge.exists(id):
        abort(404)
    if not muser.getCurrentUser().isDev():
        abort(403)
    badge = mbadges.Badge(id)
    badge.revokeFrom(request.form["from"], request.form["ts"])
    return redirect(url_for("badges_single", id=id))

def apply(app):
    app.route('/badges')(badges_page)
    app.route('/badges/<int:id>')(badges_single)
    app.route('/badges/<int:id>/award', methods=["POST"])(badges_award)
    app.route('/badges/<int:id>/revoke', methods=["POST"])(badges_revoke)
