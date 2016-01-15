# Statement for enabling the development environment
import os

DEBUG = True
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

SECRET_KEY = os.getenv('SESSION_SECRET_KEY', '1')
OAUTH_CLIENT_ID = os.getenv('OAUTH_CLIENT_ID')
OAUTH_CLIENT_SECRET = os.getenv('OAUTH_CLIENT_SECRET')
OAUTH_AUTH_URL = os.getenv('OAUTH_AUTH_URL')
OAUTH_TOKEN_URL = os.getenv('OAUTH_TOKEN_URL')
OAUTH_USER_URL = os.getenv('OAUTH_USER_URL')
OAUTH_LOGOUT_URL = os.getenv('OAUTH_LOGOUT_URL')