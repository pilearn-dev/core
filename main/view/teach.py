# coding: utf-8
from flask import Blueprint, request, session, redirect, url_for, abort, render_template, jsonify, g

from flask_babel import _

teach = Blueprint('teach', __name__)

@teach.route("/")
def index():
    return render_template("teach/index.html", title=_(u"Über Teach"), thispage="teach")

@teach.route("/try", methods=["GET", "POST"])
def try_it():
    pass
