# coding: utf-8
from flask import Blueprint, request, session, redirect, url_for, abort, render_template, jsonify
from model import user as muser, badges as mbadges
from controller import num as cnum, times as ctimes

from flask_babel import _

import json, time

badges = Blueprint('badges', __name__)

@badges.route("/")
def index():
    request.badge_prev=None
    def changed(l):
        b = l != request.badge_prev
        request.badge_prev = l
        return b
    return render_template("badges/list.html", title=_("Abzeichen"), badges=sorted(mbadges.Badge.getAll(), key=lambda x:["bronze","silver","gold"].index(x.getClass())), changed=changed)

@badges.route("/<int:id>")
def single(id):
    if not mbadges.Badge.exists(id):
        abort(404)
    badge = mbadges.Badge(id)
    return render_template("badges/single.html", title=_("Abzeichen") + " - " + badge.getName(), b=badge)

@badges.route("/<int:id>/award", methods=["POST"])
def award(id):
    if not mbadges.Badge.exists(id):
        abort(404)
    if not muser.getCurrentUser().isDev():
        abort(403)
    badge = mbadges.Badge(id)
    data = request.form["data"]
    if not data:
        data = None
    badge.awardTo(request.form["to"], data)
    return redirect(url_for("badges.single", id=id))

@badges.route("/<int:id>/revoke", methods=["POST"])
def revoke(id):
    if not mbadges.Badge.exists(id):
        abort(404)
    if not muser.getCurrentUser().isDev():
        abort(403)
    badge = mbadges.Badge(id)
    badge.revokeFrom(request.form["from"], request.form["ts"])
    return redirect(url_for("badges.single", id=id))
