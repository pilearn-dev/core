# coding: utf-8
from flask import Blueprint, render_template, redirect, abort, url_for, request
from model import privileges as mprivileges, courses as mcourses, user as muser, proposal as mproposal
from controller import query as cquery, mail as cmail
import json

proposal = Blueprint('proposal', __name__)

@proposal.route("/<id>")
def single(id):
    if not mproposal.Proposal.exists(id):
        abort(404)
    data = mproposal.Proposal(id)
    cuser = muser.getCurrentUser()
    if data.isDeleted() and not cuser.isMod():
        abort(404)
    return render_template('proposal/show.html', title="Kursvorschlag: " + data.getTitle(), thispage="course", data=data)

@proposal.route("/<id>/delete", methods=["POST"])
def delete(id):
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

@proposal.route("/<id>/undelete", methods=["POST"])
def undelete(id):
    if not mproposal.Proposal.exists(id):
        abort(404)
    proposal = mproposal.Proposal(id)
    cuser = muser.getCurrentUser()
    if not cuser.isMod():
        abort(404)
    proposal.setDetail("deleted", 0)
    proposal.setDetail("delete_reason", "")
    return "{ok}"

@proposal.route("/<id>/close", methods=["POST"])
def close(id):
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

@proposal.route("/<id>/unclose", methods=["POST"])
def unclose(id):
    if not mproposal.Proposal.exists(id):
        abort(404)
    proposal = mproposal.Proposal(id)
    cuser = muser.getCurrentUser()
    if not cuser.isMod():
        abort(404)
    proposal.setDetail("declined", 0)
    proposal.setDetail("decline_reason", "")
    return "{ok}"

@proposal.route("/<id>/commit", methods=["POST"])
def commit(id):
    if not mproposal.Proposal.exists(id):
        abort(404)
    proposal = mproposal.Proposal(id)
    cuser = muser.getCurrentUser()
    if cuser.isDisabled() or not cuser.isLoggedIn():
        return "[no.permission]"
    if not proposal.hasUserCommitment(cuser):
        proposal.addUserCommitment(cuser)
    return "{ok}"

@proposal.route("/<id>/accept", methods=["POST"])
def accept(id):
    if not mproposal.Proposal.exists(id):
        abort(404)
    proposal = mproposal.Proposal(id)
    cuser = muser.getCurrentUser()
    if not cuser.isMod():
        abort(403)

    if proposal.getDetail("courseid") == 0:
        proposal.createCourse()
        proposal = mproposal.Proposal(id)

        owner = proposal.getProposer()

        cmail.send_textbased_email(owner.getDetail("email"), "Dein Kursvorschlag für '" + proposal.getTitle() + "' war erfolgreich!", """Hallo %s,

dein Kursvorschlag für einen Kurs

## %s

war erfolgreich. Du kannst jetzt den Kurs erstellen.

{# Zum Kurs -> %s #}""" %(owner.getDetail("realname"), proposal.getTitle(), request.url_root + "c/" + str(proposal.getDetail("courseid"))))
    return "{ok}"
