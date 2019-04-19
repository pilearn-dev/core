# coding: utf-8
from flask import render_template, redirect, abort, url_for, request
from model import privileges as mprivileges, courses as mcourses, user as muser, proposal as mproposal
from controller import query as cquery
import json

def proposal_show(id):
    if not mproposal.Proposal.exists(id):
        abort(404)
    data = mproposal.Proposal(id)
    cuser = muser.getCurrentUser()
    if data.isDeleted() and not cuser.isMod():
        abort(404)
    return render_template('proposal/show.html', title=u"Kursvorschlag: " + data.getTitle(), thispage="course", data=data)

def proposal_delete(id):
    if not mproposal.Proposal.exists(id):
        abort(404)
    proposal = mproposal.Proposal(id)
    cuser = muser.getCurrentUser()
    if not cuser.isMod():
        abort(404)
    data = request.json
    proposal.setDetail("deleted", 1)
    proposal.setDetail("delete_reason", data["reason"])
    return "{ok}"

def proposal_undelete(id):
    if not mproposal.Proposal.exists(id):
        abort(404)
    proposal = mproposal.Proposal(id)
    cuser = muser.getCurrentUser()
    if not cuser.isMod():
        abort(404)
    proposal.setDetail("deleted", 0)
    proposal.setDetail("delete_reason", "")
    return "{ok}"

def proposal_close(id):
    if not mproposal.Proposal.exists(id):
        abort(404)
    proposal = mproposal.Proposal(id)
    cuser = muser.getCurrentUser()
    if not cuser.isMod():
        abort(404)
    data = request.json
    proposal.setDetail("declined", 1)
    proposal.setDetail("decline_reason", data["reason"])
    return "{ok}"

def proposal_unclose(id):
    if not mproposal.Proposal.exists(id):
        abort(404)
    proposal = mproposal.Proposal(id)
    cuser = muser.getCurrentUser()
    if not cuser.isMod():
        abort(404)
    proposal.setDetail("declined", 0)
    proposal.setDetail("decline_reason", "")
    return "{ok}"

def proposal_commit(id):
    if not mproposal.Proposal.exists(id):
        abort(404)
    proposal = mproposal.Proposal(id)
    cuser = muser.getCurrentUser()
    if cuser.isDisabled() or not cuser.isLoggedIn():
        return "[no.permission]"
    if not proposal.hasUserCommitment(cuser):
        proposal.addUserCommitment(cuser)
    return "{ok}"

def proposal_accept(id):
    if not mproposal.Proposal.exists(id):
        abort(404)
    proposal = mproposal.Proposal(id)
    cuser = muser.getCurrentUser()
    if not cuser.isMod():
        abort(403)
    if proposal.getDetail("courseid") == 0:
        proposal.createCourse()
    return "{ok}"

def apply(app):
    app.route("/course/proposal/<id>")(proposal_show)
    app.route("/course/proposal/<id>/close", methods=["POST"])(proposal_close)
    app.route("/course/proposal/<id>/unclose", methods=["POST"])(proposal_unclose)
    app.route("/course/proposal/<id>/delete", methods=["POST"])(proposal_delete)
    app.route("/course/proposal/<id>/undelete", methods=["POST"])(proposal_undelete)
    app.route("/course/proposal/<id>/commit", methods=["POST"])(proposal_commit)
    app.route("/course/proposal/<id>/accept", methods=["POST"])(proposal_accept)
