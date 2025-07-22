from flask import Flask, Blueprint, request, session, redirect, url_for, render_template
from authlib.integrations.flask_client import OAuth
import pymysql
import json
import base64
from config import Config

VERSION = Config.VERSION

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY or 'dev'

# Blueprint หลักของระบบ HRM
bp = Blueprint('hrm', __name__, url_prefix='/hrm')

@app.context_processor
def inject_version():
    return {'app_version': VERSION}

# ----- SSO -----
oauth = OAuth(app)
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

# ----- Database -----

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

# ----- Utilities -----

def sso_authenticated():
    return session.get('staff_user') is not None

# ----- Routes -----

@bp.route('/')
def index():
    if not sso_authenticated():
        return redirect(url_for('hrm.login'))
    return render_template('index.html', title='หน้าหลัก')

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

# ----- Attendance -----

@bp.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if not sso_authenticated():
        return redirect(url_for('hrm.login'))

    message = ''
    if request.method == 'POST':
        id_card = request.form['id_card']
        action = request.form['action']
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute('SELECT id FROM staff WHERE national_id=%s', (id_card,))
                row = cur.fetchone()
                if row:
                    staff_id = row['id']
                else:
                    cur.execute('INSERT INTO staff (national_id) VALUES (%s)', (id_card,))
                    staff_id = cur.lastrowid
                if action == 'checkin':
                    cur.execute('INSERT INTO attendances (staff_id, checkin_time) VALUES (%s, NOW())', (staff_id,))
                    message = 'บันทึกเวลาเข้าแล้ว'
                elif action == 'checkout':
                    cur.execute('INSERT INTO attendances (staff_id, checkout_time) VALUES (%s, NOW())', (staff_id,))
                    message = 'บันทึกเวลาออกแล้ว'
            conn.commit()
        finally:
            conn.close()
    return render_template('attendance.html', message=message, title='บันทึกเวลา')

app.register_blueprint(bp)

@app.route('/')
def root_redirect():
    return redirect(url_for('hrm.index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.SERVER_PORT, debug=True)
