# coding: utf-8
import datetime as d
from flask import render_template, redirect, url_for, request
import model.user as muser
W2018TC = d.datetime(day=21, month=12, year=2018)

QUIZ_DATA = {
    14: {
        "q": u"DevTest: Wie viel Reputation möchtest du haben",
        "a1": "2",
        "a2": "0",
        "a3": "0",
        "correct": [1],
        "reputation": 2
    },
    21: {
        "q": u"Heute ist ...",
        "a1": "Sommersonnenwende",
        "a2": "Wintersonnenwende",
        "a3": "Äquinoktium",
        "correct": [2],
        "reputation": 2
    },
    22: {
        "q": u"Es gibt ... Wintermonate",
        "a1": "1",
        "a2": "2",
        "a3": "3",
        "correct": [3],
        "reputation": 2
    },
    23: {
        "q": u"Wenn bei uns Winter ist, wird in Australien ... gefeiert.",
        "a1": "Halloween",
        "a2": "Weihnachten",
        "a3": "Ostern",
        "correct": [2],
        "reputation": 2
    },
    24: {
        "q": u"Geschenke! Wähle irgendetwas aus!",
        "a1": "mich",
        "a2": "mich",
        "a3": "mich",
        "correct": [1,2,3],
        "reputation": 10
    },
    25: {
        "q": u"1. Weihnachtsfeiertag! Wähle irgendetwas aus",
        "a1": "hier",
        "a2": "hier",
        "a3": "hier",
        "correct": [1,2,3],
        "reputation": 5
    },
    26: {
        "q": u"Es gibt ... Wintermonate",
        "a1": "1",
        "a2": "2",
        "a3": "2",
        "correct": [3],
        "reputation": 2
    }
}

def winter2018_index():
    now = d.datetime.now()
    if (W2018TC-now) < (now-now):
        return render_template("winter2018/index.html", title="Winter 2018")
    return render_template("winter2018/countdown.html", title="Winter 2018")

def winter2018_quiz():
    now = d.datetime.now()
    if (W2018TC-now) >= (now-now):
        return redirect(url_for("winter2018_index"))
    if request.values.get("submit"):
        qd = QUIZ_DATA[now.day]
        if int(request.form["value"]) in qd["correct"]:
            cu = muser.getCurrentUser()
            cu.setDetail("reputation", cu.getDetail("reputation") + qd["reputation"])
            cu.setReputationChange("winter", "Teilnahme am Winter-Quiz am " + str(now.day) + ".12.2018", qd["reputation"])
            return redirect(url_for("index"))
        else:
            return redirect(url_for("index"))
    return render_template("winter2018/quiz.html", title="Winte r 2018", quiz=QUIZ_DATA[now.day])

def apply(f):
    f.route("/event/winter2018")(winter2018_index)
    f.route("/event/winter2018/quiz", methods=["GET", "POST"])(winter2018_quiz)
