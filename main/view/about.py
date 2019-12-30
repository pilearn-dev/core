# coding: utf-8
from flask import Blueprint, request, session, redirect, url_for, abort, render_template, jsonify
from model import user as muser, help as mhelp

import json, time

about = Blueprint('about', __name__)

@about.route("/team")
def team():
    TEAM = json.loads(mhelp.HelpEntry.from_url("concept/teampage").getContent().split("<!-- end comment -->")[1])
    return render_template("about/team.html", title="Über uns - Unser Team", mkuser=muser.User.safe, team=TEAM)
