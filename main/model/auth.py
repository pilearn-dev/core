from flask import url_for, current_app, redirect, request
from flask_oauthlib.client import OAuth
import json, urllib.request, urllib.error, urllib.parse

# SECRET #
OAUTH_CREDENTIALS = {
    "google": {
        "id": "960981775265-3hi6ojngqgscglu9eu18is576ou05m8i.apps.googleusercontent.com",
        "secret": "HKaRkWwqLJcuASrg6Gz52GkM"
    }
}
#========#

google = None

def apply(app):
    global google
    oauth = OAuth(app)
    google = oauth.remote_app(
        'google',
        consumer_key=OAUTH_CREDENTIALS["google"]["id"],
        consumer_secret=OAUTH_CREDENTIALS["google"]["secret"],
        request_token_params={
            'scope': 'profile email'
        },
        base_url='https://www.googleapis.com/oauth2/v1/',
        request_token_url=None,
        access_token_method='POST',
        access_token_url='https://accounts.google.com/o/oauth2/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
    )
