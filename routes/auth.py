from flask import render_template, request, redirect, url_for, session
import json
import base64
from config import Config
from . import bp
from .utils import oauth

@bp.route('/login')
def login():
    token_param = request.args.get('token')
    userinfo = None

    if token_param:
        try:
            if token_param.count('.') >= 2:
                payload = token_param.split('.')[1]
                padded = payload + '=' * (-len(payload) % 4)
                data = base64.urlsafe_b64decode(padded).decode('utf-8')
                userinfo = json.loads(data)
            else:
                padded = token_param + '=' * (-len(token_param) % 4)
                data = base64.urlsafe_b64decode(padded).decode('utf-8')
                userinfo = json.loads(data)
        except Exception:
            if oauth:
                token = {'id_token': token_param}
                userinfo = oauth.sso.parse_id_token(token)

    if userinfo:
        session['staff_user'] = (
            userinfo.get('username') or
            userinfo.get('full_name') or
            userinfo.get('name') or
            userinfo.get('email') or
            userinfo.get('preferred_username') or
            request.args.get('full_name') or
            request.args.get('user')
        )
        return redirect(url_for('hrm.index'))

    if oauth and not token_param:
        redirect_uri = url_for('hrm.authorize', _external=True)
        extra = {}
        if Config.SSO_SECRET_KEY:
            extra['sso_secret_key'] = Config.SSO_SECRET_KEY
        return oauth.sso.authorize_redirect(redirect_uri, **extra)

    user = request.args.get('user')
    if user:
        session['staff_user'] = user
        return redirect(url_for('hrm.index'))

    return render_template('login.html', title='เข้าสู่ระบบ')

@bp.route('/authorize')
def authorize():
    if not oauth:
        return redirect(url_for('hrm.login'))
    token = oauth.sso.authorize_access_token()
    userinfo = oauth.sso.parse_id_token(token)
    session['staff_user'] = userinfo.get('name') or userinfo.get('preferred_username')
    return redirect(url_for('hrm.index'))
