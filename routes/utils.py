from flask import session
from authlib.integrations.flask_client import OAuth
import pymysql
from config import Config

oauth = OAuth()
if Config.SSO_CLIENT_ID:
    oauth.register(
        name='sso',
        client_id=Config.SSO_CLIENT_ID,
        client_secret=Config.SSO_CLIENT_SECRET,
        authorize_url=Config.SSO_AUTHORIZE_URL,
        access_token_url=Config.SSO_TOKEN_URL,
        userinfo_endpoint=Config.SSO_USERINFO_URL,
        client_kwargs={'scope': 'openid profile email'}
    )
else:
    oauth = None


def init_oauth(app):
    if oauth:
        oauth.init_app(app)


def get_connection():
    return pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


def sso_authenticated():
    return session.get('staff_user') is not None
