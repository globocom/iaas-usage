# Statement for enabling the development environment
import os

DEBUG = True
if os.environ.get('OAUTHLIB_INSECURE_TRANSPORT') is None:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

SERVER_NAME = os.getenv('SERVER_NAME', 'localhost:8080')
SERVER_PORT = os.getenv('SERVER_PORT', 8080)
SERVER_SCHEME = os.getenv('SERVER_SCHEME', 'http')
SECRET_KEY = os.getenv('SESSION_SECRET_KEY', '1')
OAUTH_CLIENT_ID = os.getenv('OAUTH_CLIENT_ID')
OAUTH_CLIENT_SECRET = os.getenv('OAUTH_CLIENT_SECRET')
OAUTH_AUTH_URL = os.getenv('OAUTH_AUTH_URL')
OAUTH_TOKEN_URL = os.getenv('OAUTH_TOKEN_URL')
OAUTH_USER_URL = os.getenv('OAUTH_USER_URL')
OAUTH_LOGOUT_URL = os.getenv('OAUTH_LOGOUT_URL')