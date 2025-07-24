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

# ----- Staff Management -----

@bp.route('/staff')
def staff():
    if not sso_authenticated():
        return redirect(url_for('hrm.login'))

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT id, national_id, full_name, position FROM staff ORDER BY id')
            rows = cur.fetchall()
    finally:
        conn.close()
    return render_template('staff.html', staff_list=rows, title='ข้อมูลบุคลากร')

# ----- Employee History -----

@bp.route('/history', methods=['GET', 'POST'])
def history():
    if not sso_authenticated():
        return redirect(url_for('hrm.login'))

    message = ''
    edit_record = None
    open_modal = False
    conn = get_connection()
    try:
        if request.method == 'POST':
            form = request.form
            data = (
                form.get('national_id'),
                form.get('full_name'),
                form.get('position'),
                form.get('department'),
                form.get('division'),
                form.get('start_date'),
                form.get('note'),
                form.get('phone'),
            )
            with conn.cursor() as cur:
                if form.get('id'):
                    cur.execute(
                        'UPDATE employee_histories SET national_id=%s, full_name=%s, position=%s, '
                        'department=%s, division=%s, start_date=%s, note=%s, phone=%s WHERE id=%s',
                        data + (form.get('id'),)
                    )
                    message = 'แก้ไขข้อมูลเรียบร้อยแล้ว'
                else:
                    cur.execute(
                        'INSERT INTO employee_histories (national_id, full_name, position, department, '
                        'division, start_date, note, phone) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
                        data
                    )
                    message = 'เพิ่มข้อมูลเรียบร้อยแล้ว'
                conn.commit()

        edit_id = request.args.get('edit_id')
        if edit_id:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM employee_histories WHERE id=%s', (edit_id,))
                edit_record = cur.fetchone()
            open_modal = True
        elif request.args.get('add'):
            open_modal = True

        with conn.cursor() as cur:
            cur.execute('SELECT * FROM employee_histories ORDER BY id')
            rows = cur.fetchall()
    finally:
        conn.close()
    return render_template(
        'history.html',
        history_list=rows,
        edit_record=edit_record,
        message=message,
        open_modal=open_modal,
        title='ประวัติพนักงาน'
    )

# ----- Projects -----

@bp.route('/projects')
def projects():
    if not sso_authenticated():
        return redirect(url_for('hrm.login'))
    return render_template('projects.html', title='โครงการ')

# ----- Backup -----

@bp.route('/backup')
def backup():
    if not sso_authenticated():
        return redirect(url_for('hrm.login'))
    return render_template('backup.html', title='สำรองข้อมูล')

# ----- About -----

@bp.route('/about')
def about():
    if not sso_authenticated():
        return redirect(url_for('hrm.login'))
    return render_template('about.html', title='เกี่ยวกับระบบ')

app.register_blueprint(bp)

@app.route('/')
def root_redirect():
    return redirect(url_for('hrm.index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.SERVER_PORT, debug=True)
