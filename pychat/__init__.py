"""
    FLASK APPLICATION
"""

from flask import Flask, session, request, redirect, url_for, abort, render_template
import json, minimark
import time
from model import getCurrentUser, User, Room, Message, MEQ, MF


app = Flask(__name__)

f = open("chatdata.json", "r")
CONFIG = json.loads(f.read())
f.close()

app.config.update(dict(
    SECRET_KEY=CONFIG["secret_key"]
))

@app.context_processor
def _context_processor():
    """
        This function will return values available in
        all top-level template code.
    """

    cuser = getCurrentUser()

    #session["login"] = 2

    return{
        "config": CONFIG,
        "is_anon": cuser.id == -3,
        "user": cuser,
        "mini_mark": minimark.compile
    }

@app.before_request
def _before_request():
    """
        This function will be called before the request
        handler. If return value is not None return value
        will be used as response.
    """
    return None

@app.route("/")
def index():
    """
        Route for /.
    """
    return render_template("index.html", title="Startseite", roomList=Room.all())

@app.route("/room/<int:id>/view")
def room_view(id):
    """
        Route for /room/<int:id>/view.
    """
    if not Room.exists(id):
        abort(404)
    r = Room(id)
    cuser = getCurrentUser()
    msg = Message.all(r.id, not cuser.isMod())
    return render_template("room_view.html", title="Raum " + r.getName(), room=r, messageList=msg, latest_id=MEQ.room_latest(r.id))

@app.route("/user/<int:id>")
def user_view(id):
    """
        Route for /user/<int:id>.
    """
    if not User.exists(id):
        abort(404)
    u = User(id)
    return render_template("user_view.html", title="Benutzer " + u.getName(), duser=u)

@app.route("/polling", methods=["GET", "POST"])
def socket():
    """
        Polling server
    """

    cuser = getCurrentUser()
    data = json.loads(request.data)
    if data["action"] == "message":
        msg = data["data"]["message"]
        room_id = data["data"]["room"]
        if cuser.mayPost():
            if msg:
                if session.get("last_msg", 0) != 0:
                    if time.time() - session.get("last_msg", 0) < 2:
                        session["last_msg"] = time.time()
                        return "{}"
                session["last_msg"] = time.time()
                M = Message.new(room_id, cuser, msg)
                MEQ.add(room_id, "new", M)
    elif data["action"] == "delete":
        if cuser.isMod():
            msg = data["data"]["message"]
            room_id = data["data"]["room"]
            M = Message(msg)
            M.setDetail("is_shown",False)
            MEQ.add(room_id, "deleted", M)
    elif data["action"] == "undelete":
        if cuser.isMod():
            msg = data["data"]["message"]
            room_id = data["data"]["room"]
            M = Message(msg)
            M.setDetail("is_shown",True)
            MEQ.add(room_id, "undeleted", M)
    elif data["action"] == "update":
        if cuser.isMod():
            msg = data["data"]["message"]
            content = data["data"]["content"]
            room_id = data["data"]["room"]
            M = Message(msg)
            M.setDetail("was_edited",True)
            M.setDetail("content",content)
            MEQ.add(room_id, "updated", M)
    elif data["action"] == "promote":
        if cuser.isMod():
            content = data["data"]["content"]
            room_id = data["data"]["room"]
            promo_room_id = data["data"]["promo_room"]
            M = Message.new(room_id, cuser, content)
            MEQ.add(room_id, "new", M)
            MEQ.add(promo_room_id, "system-banner", M)
    elif data["action"] == "flag":
        msg = data["data"]["message"]
        comment = data["data"]["comment"]
        room_id = data["data"]["room"]
        M = Message(msg)
        MF.new(room_id, M.id, cuser, comment)
    elif data["action"] == "flag-list":
        if cuser.isMod():
            room_id = data["data"]["room"]
            data = MF.all(room_id)
            D = json.dumps({
                "event": "flaglist",
                "data": [[json.loads(Message.toJSON(x[0])), [y.toJSON() for y in x[1]]] for x in data]
            })
            return D
    elif data["action"] == "flag.validation":
        if cuser.isMod():
            msg = data["data"]["message"]
            review = data["data"]["review"]
            MF.mark_by_msg(msg, 1 if review == "ok" else 2)
            M = Message(msg)
            if review == "bad":
                M.setDetail("is_shown",False)
                MEQ.add(M.getDetail("room_id"), "deleted", M)
                a = M.getAuthor()
                if not a.isSuspended():
                    a.setDetail("suspension_end",int(time.time())+int(600)+10)
                    a.setDetail("suspension_reason","wegen Regelverletzung")
                    a.setDetail("is_suspended",True)
                else:
                    a.setDetail("suspension_end",int(a.getDetail("suspension_end"))+int(600)+10)
            data = MF.all(M.getDetail("room_id"))
            return json.dumps({
                "event": "flaglist",
                "data": [[json.loads(Message.toJSON(x[0])), [y.toJSON() for y in x[1]]] for x in data]
            })

    last_fetch_id = data["data"]["last-update-id"]
    room_id = data["data"]["room"]
    updates = MEQ.get_newest(room_id, last_fetch_id)
    updates = list(map(MEQ.toJSON, updates))
    fc = MF.roomCount(room_id)
    answer = {
        "event": "events",
        "data": {"u":updates, "fc":fc, "may_post": cuser.mayPost()}
    }
    return json.dumps(answer)


@app.route("/user-api", methods=["GET", "POST"])
def user_api():
    """
        Polling server
    """
    cuser = getCurrentUser()
    data = json.loads(request.data)
    if data["action"] == "suspend":
        if cuser.isMod():
            reason = data["data"]["reason"]
            duration = data["data"]["time"]
            user_id = data["data"]["user"]
            u = User(user_id)
            u.setDetail("suspension_end",int(time.time())+int(duration)+10)
            u.setDetail("suspension_reason",reason)
            u.setDetail("is_suspended",True)
            answer = {
                "event": "reload",
                "data": True
            }
        else:
            answer = {
                "event": "@error",
                "data": False
            }
    elif data["action"] == "unsuspend":
        if cuser.isMod():
            user_id = data["data"]["user"]
            User(user_id).setDetail("is_suspended",False)
            answer = {
                "event": "reload",
                "data": True
            }
        else:
            answer = {
                "event": "@error",
                "data": False
            }
    return json.dumps(answer)

@app.errorhandler(404)
def error404(e):
    """
        404 Not found.
    """
    return "<h1>Not found (404)</h1>", 404

# Start server if this file is the main program
# DO NOT USE run_simple IN PRODUCTION MODE!!
if __name__ == "__main__":
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 80, app, use_reloader=True)
