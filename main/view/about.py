# coding: utf-8
from flask import request, session, redirect, url_for, abort, render_template, jsonify
from model import user as muser, help as mhelp

import json, time

def about_team():
    TEAM = json.loads(mhelp.HelpEntry.from_url("concept/teampage").getContent().split("<!-- end comment -->")[1])
    return render_template("about/team.html", title=u"Über uns - Unser Team", mkuser=muser.User.safe, team=TEAM)

def apply(app):
    app.route("/about/team")(about_team)
