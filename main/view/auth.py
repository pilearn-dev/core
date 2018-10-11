# coding: utf-8
from flask import render_template, redirect, abort, url_for, request, session
from model import user as muser, auth as mauth
from controller import query as cquery
import json, time, re

def login():
    global LOGGED_INS
    error = False
    if request.method == 'POST':
        if request.form['login_provider'] == "local_account":
            data = muser.User.login(request.form['username'], request.form['password'])
            if data == -4:
                error = "forbidden"
            elif data == -3:
                error = "not-found"
            else:
                user_id = data
        elif request.form["login_provider"] == "local_registration":
            if re.match("[a-zA-Z0-9-_]{2,30}", request.form['username']):
                llin = muser.User.login(request.form['username'], request.form['password'])
                if llin == -4:
                    data = muser.User.reset_deletion(request.form['username'], request.form['password'])
                else:
                    data = muser.User.register(request.form['username'], request.form['password'], request.form['realname'], request.form['email'])
                if data == -3:
                    error = "forbidden"
                else:
                    user_id = data
                    session['login'] = user_id
                    session["login_time"] = time.time()
                    return redirect(url_for('tour'))
            else:
                error="format"
        if not error:
            session['login'] = user_id
            session["login_time"] = time.time()

            if muser.User.from_id(user_id).getDetail("password") == "":
                return redirect(url_for('user_page', id=user_id))
            else:
                return redirect(url_for('index'))
    if IS_OFFLINE:
        abort(503)
    return render_template('login.html', error=error, title="Anmelden", thispage="login")

def reset_password():
    error = False
    if request.method == 'POST':
        data = muser.User.passwdreset(request.form['username'], request.form['email'])
        error = "done"
    return render_template('passwordreset.html', error=error, title=u"Passwort zurücksetzen", thispage="login")

def logout():
    user = muser.getCurrentUser()
    session.pop('login', None)
    return redirect(url_for('index'))

def beta_login():
    error = None
    f = open("main/help-documents/terms_offline.md", "r")
    terms = f.read()
    f.close()
    f = open("main/help-documents/data_info_offline.md", "r")
    data_policy = f.read()
    f.close()
    LOGIN_KEY = pidata["register_key"]
    if request.method == "POST":
        if request.form["beta-passkey"] == LOGIN_KEY or LOGIN_KEY is None:
            if re.match("[a-zA-Z0-9-_]{2,30}", request.form['username']) and len(request.form["realname"]) <= 25:
                data = muser.User.register(request.form['username'], request.form['password'], request.form['realname'], request.form['email'])
                if data != -3:
                    user_id = data
                    cuser = muser.User.from_id(user_id)
                    cuser.setDetail("labels", '["beta", "betaaccess"]')
                    cuser.setDetail("email", request.form["email"])
                    session['login'] = user_id
                    return redirect(url_for('tour'))
                else:
                    error = "any"
            else:
                error = "format"
        else:
            error = "invalid_key"
    return render_template('beta.html', title="Webseite im Offlinemodus", message=OFFLINE_NOTE, beta_token=BETA_TOKEN, terms=terms, data_policy=data_policy, error=error, passkey=LOGIN_KEY)

def oauth_authorize(provider):
    if not muser.require_login():
        return redirect(url_for('index'))
    if provider == "google":
        return mauth.google.authorize(callback=url_for('oauth_callback', provider="google", _external=True))
    abort(404)

def oauth_callback(provider):
    if not muser.require_login():
        return redirect(url_for('index'))
    email = nickname = username = None
    if provider == "google":
        resp = mauth.google.authorized_response()
        if resp is None:
            return redirect("/oauth-error/google")
        session[provider+'_token'] = (resp['access_token'], '')
        me = mauth.google.get('userinfo')
        print(me.data)
        email = me.data["email"]
        username = me.data["name"].lower().replace(" ", ".")
        username = re.sub("[^a-z0-9.-]", "", username)
        nickname = me.data["name"]
    if email is None:
        return redirect('/oauth_error/google')
    # Look if the user already exists
    user=muser.User.oauth_login(provider, email)
    if user < 00:
        # Create the user. Try and use their name returned by Google,
        # but if it is not set, split the email address at the @.
        if (nickname is None or nickname == "") or (username is None or username == ""):
            nickname = username = email.split('@')[0]
        # We can do more work here to ensure a unique nickname, if you
        # require that.
        user = muser.User.register(username, "~~~~~oauth", nickname, email)
        if user < 0:
            return render_template('login.html', error="format", title="Anmelden", thispage="login")
        muser.User.from_id(user).setDetail("login_provider", "oauth:"+provider)
    # Log in the user, by default remembering them for their next visit
    # unless they log out.
    session['login'] = user
    session["login_time"] = time.time()
    return redirect(url_for('index'))

def get_google_oauth_token():
    return session.get('google_token')

def apply(app, pidata2):
    global IS_OFFLINE, OFFLINE_NOTE, IN_BETA, SITE_LABEL, BETA_TOKEN, pidata
    IS_OFFLINE = pidata2["is_offline"]
    OFFLINE_NOTE = pidata2["offline_note"]
    IN_BETA = pidata2["in_beta"]
    SITE_LABEL = pidata2["label"]
    BETA_TOKEN = pidata2["beta_token"]
    pidata = pidata2
    app.route("/~dev/login", methods=['GET', 'POST'])(app.route("/login", methods=['GET', 'POST'])(login))
    app.route("/reset-password", methods=['GET', 'POST'])(reset_password)
    app.route('/logout')(logout)
    app.route("/beta", methods=["GET", "POST"])(beta_login)
    app.route('/oauth/<provider>')(oauth_authorize)
    app.route('/oauth2callback/<provider>')(oauth_callback)
    mauth.apply(app)
    mauth.google.tokengetter(get_google_oauth_token)
