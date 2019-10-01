# coding: utf-8

from model.settings import Settings as S

import sqlite3 as lite

from flask import request, session, redirect, url_for, abort, render_template, jsonify, g
from model import privileges as mprivileges, tags as mtags, user as muser, reviews as mreviews, forum as mforum, post_templates as mposttemplates
from controller import num as cnum, times as ctimes

from flask_babel import _

def admin_index():
    cuser = muser.getCurrentUser()
    if not cuser.isDev():
        abort(403)
    return render_template("admin/index.html", title=_("Administration"), thispage="admin")

def admin_settings():
    cuser = muser.getCurrentUser()
    if not cuser.isDev():
        abort(403)
    if request.method == "GET":
        return render_template("admin/settings.html", title=_("Administration") + ": " + _("Einstellungen"), thispage="admin", S=S)
    elif request.method == "POST":
        S.set(request.json["key"], request.json["value"])
        return "true"

def admin_sql():
    cuser = muser.getCurrentUser()
    if not cuser.isDev():
        abort(404)

    lr = columns = None

    if request.method == "POST":
        sql = request.form["sql"]
        is_bulk = request.form.has_key("is_bulk")

        try:
            con = lite.connect('databases/pilearn.db')
            cur = con.cursor()
            if not is_bulk:
                cur.execute(sql)
                lr = cur.fetchall()
                columns = cur.description
                if not lr:
                    columns = None
                    lr = [["Success:", sql], ["Rows affected:", cur.rowcount], ["Last row:", cur.lastrowid]]
            else:
                cur.executescript(sql)
                lr = [["Success:", sql], ["Rows affected:", cur.rowcount], ["Last row:", cur.lastrowid]]
            con.commit()
        except lite.Error as e:
            lr = [["Error:", str(e)]]
        except lite.Warning as e:
                lr = [["Warning:", str(e)]]

    return render_template("admin/sql.html", title=_("Administration") + ": " + _(u"SQL ausführen"), lr=lr, columns=columns)

def apply(app):
    app.route('/admin', methods=["GET", "POST"])(admin_index)
    app.route('/admin/settings', methods=["GET", "POST"])(admin_settings)
    app.route('/admin/sql', methods=["GET", "POST"])(admin_sql)
