from functools import wraps
from flask import request, url_for, session
from flask_login import current_user
from flask_restful import abort
from requests_oauthlib import OAuth2Session
from werkzeug.utils import redirect
from app import app, login_manager
from app.auth.models import User
import re


def required_login(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        is_api_uri = re.match("/api/", request.url_rule.rule) is not None
        user_is_authenticated = current_user.is_authenticated()

        if is_api_uri and not user_is_authenticated:
            return abort(403)
        if not user_is_authenticated:
            client_id = app.config['OAUTH_CLIENT_ID']
            authorization_url = app.config['OAUTH_AUTH_URL']
            oauth_redirect_url = app.config['OAUTH_REDIRECT_URL']

            if(oauth_redirect_url is not None):
                redirect_uri = oauth_redirect_url + '/login'
            else:
                redirect_uri = url_for('login', _external=True)

            oauth2_session = OAuth2Session(client_id, scope=[], redirect_uri=redirect_uri)

            authorization_url, state = oauth2_session.authorization_url(authorization_url)
            return redirect(authorization_url)
        return func(*args, **kwargs)
    return decorated_view


@login_manager.user_loader
def load_user(user_id):
    if user_id is not None and session.get('user') is not None:
        user = session['user']
        return User(user['email'], user['email'], user['picture'])
    return None

