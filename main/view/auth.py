# coding: utf-8
from flask import render_template, redirect, abort, url_for, request, session
from model import user as muser, auth as mauth
from controller import query as cquery, mail as cmail
import json, time, re
from flask_babel import _

banned_email_domains = ["@yeah.net", "@163.com"]

def login():
    error = False
    if request.method == 'POST':
        if request.form['login_provider'] == "local_account":
            data = muser.User.login(request.form['email'], request.form['password'])
            if data == -4:
                error = "forbidden"
            elif data == -3:
                error = "not-found"
            else:
                user_id = data
        if not error:
            session['login'] = user_id
            session["login_time"] = time.time()

            if "continue" in request.values:
                return redirect(request.values.get("continue"))

            return redirect(url_for('index'))
    return render_template('login.html', error=error, title=_("Anmelden"), thispage="login", oauth=mauth.OAUTH_CREDENTIALS)

def register():
    error = False
    if request.method == 'POST':
        if request.form['login_provider'] == "local_account":
            if re.match("[a-zA-Z0-9.+_-]+\@[a-zA-Z0-9.+_-]+\.[a-zA-Z]{2,10}", request.form['email']):
                for banned_email_domain in banned_email_domains:
                    if request.form["email"].endswith(banned_email_domain):
                        abort(500)
                llin = muser.User.login(request.form['email'], request.form['password'])
                if llin == -4:
                    data = muser.User.reset_deletion(request.form['email'], request.form['password'])
                else:
                    user_name = request.form['realname']
                    if len(user_name) > 30 or "http://" in user_name or "https://" in user_name:
                        abort(400)
                    data = muser.User.register(request.form['password'], time.time(), request.form['email'])
                    datao = muser.User.from_id(data)
                    datao.setDetail("name", "benutzer-" + str(datao.id))
                    datao.setDetail("realname", "benutzer-" + str(datao.id))
                    if 3 <= len(user_name) and "♦" not in user_name:
                        datao.setDetail("realname", user_name)
                        datao.setDetail("name", user_name)
                if data == -3:
                    error = "forbidden"
                else:
                    user_id = data
                    session['login'] = user_id
                    session["login_time"] = time.time()

                    if "continue" in request.values:
                        return redirect(request.values.get("continue"))

                    return redirect(url_for('tour'))
            else:
                error="format"
        if not error:
            session['login'] = user_id
            session["login_time"] = time.time()

            if "continue" in request.values:
                return redirect(request.values.get("continue"))

            return redirect(url_for('index'))
    return render_template('register.html', error=error, title=_("Registrieren"), thispage="login", oauth=mauth.OAUTH_CREDENTIALS)

def reset_password():
    error = False
    if request.method == 'POST':
        data = muser.User.passwdreset_new_request(request.form['email'])
        if data:

            url = url_for("reset_password_verify", id=data[0], _external=True)

            cmail.send_textbased_email(request.form['email'], _("Dein Passwort-Zurücksetz-Code"), _("""Hallo,

du hast eine Anfrage auf &pi;-Learn gesendet, um das Passwort für diese E-Mail-Adresse zurückzusetzen.

Der Bestätigungscode dafür lautet:

# %(code)s

Wenn du das Fenster bereits geschlossen hast, kannst du { hier klicken -> %(link)s } oder diesen Link im Browser öffnen:

%(link)s

Wenn diese Anfrage nicht von dir stammt, kannst du diese E-Mail einfach löschen.""", code=data[1], link=url))



            return redirect(url)
        error = "invalid"
    return render_template('passwordreset.html', error=error, title=_("Passwort zurücksetzen"), thispage="login")

def reset_password_verify(id):
    if not muser.User.passwdreset_has_request(id):
        abort(404)
    error = False
    if request.method == 'POST':
        data = muser.User.passwdreset_run_request(id, request.form['key'].strip(), request.form['pw'])
        if data:
            error = "success"
        else:
            error = "invalid-code"
    return render_template('passwordreset_verify.html', error=error, title=_("Passwort zurücksetzen"), thispage="login")

def logout():
    user = muser.getCurrentUser()
    session.clear()
    return redirect(url_for('index'))

def auth_reset():
    user = muser.getCurrentUser()
    session.clear()
    return redirect(url_for('login'))

def oauth_authorize(provider):
    if not muser.require_login() and request.form.get("override") != "true" and request.values.get("re-login") != "true":
        return redirect(url_for('index'))
    if provider == "google":
        return mauth.google.authorize(callback=url_for('oauth_callback', provider="google", _external=True))
    abort(404)

def oauth_callback(provider):
    email = nickname = username = None
    if provider == "google":
        resp = mauth.google.authorized_response()
        if resp is None:
            return redirect("/oauth-error/"+provider)
        session[provider+'_token'] = (resp['access_token'], '')
        me = mauth.google.get('userinfo')
        email = me.data["email"]
        username = me.data["name"].lower().replace(" ", ".")
        username = re.sub("[^a-z0-9.-]", "", username)
        nickname = me.data["name"]
    if email is None:
        return redirect('/oauth_error/'+provider)
    # Look if the user already exists
    cuser = muser.getCurrentUser()
    if cuser.isLoggedIn():
        user=muser.User.oauth_login(provider, email)
        if user < 0:
            cuser.loginMethod_add("oauth:"+provider, email, None)
            return redirect(url_for("user_edit_page", id=cuser.id, name=cuser.getDetail("name"), page="login"))
        elif user == cuser.id:
            return redirect("/")
            session["login_time"] = time.time()
        else:
            return redirect(url_for("user_edit_page", id=cuser.id, name=cuser.getDetail("name"), page="login-alter", method="google", error="dualism"))
    else:
        user=muser.User.oauth_login(provider, email)
        if user < 0:
            # Create the user. Try and use their name returned by Google,
            # but if it is not set, split the email address at the @.
            if (nickname is None or nickname == "") or (username is None or username == ""):
                nickname = username = email.split('@')[0]
            user = muser.User.register(None, nickname, email)
            if user < 0:
                return render_template('login.html', error="format", title="Anmelden", thispage="login")
            user = muser.User.from_id(user)
            user.loginMethod_add("oauth:"+provider, email, None)

    session['login'] = user
    session["login_time"] = time.time()
    return redirect(url_for('index'))

def get_google_oauth_token():
    return session.get('google_token')

def apply(app):
    @app.route("/login")
    def login_redirect():
        return redirect(url_for("login"))
    app.route("/auth/login", methods=['GET', 'POST'])(login)

    @app.route("/register")
    def register_redirect():
        return redirect(url_for("register"))
    app.route("/auth/register", methods=['GET', 'POST'])(register)


    app.route("/auth/password-reset", methods=['GET', 'POST'])(reset_password)
    app.route("/auth/password-reset/verify/<int:id>", methods=['GET', 'POST'])(reset_password_verify)


    @app.route("/logout")
    def logout_redirect():
        return redirect(url_for("logout"))
    app.route('/auth/logout')(logout)

    app.route('/auth/reset')(auth_reset)

    app.route('/auth/oauth-provider/<provider>', methods=["GET", "POST"])(oauth_authorize)
    app.route('/oauth2callback/<provider>')(oauth_callback)

    mauth.apply(app)
    try:
        mauth.google.tokengetter(get_google_oauth_token)
    except:
        pass
