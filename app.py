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
def inject_globals():
    return {
        'app_version': VERSION,
        'default_checkin': Config.DEFAULT_CHECKIN_TIME,
        'default_checkout': Config.DEFAULT_CHECKOUT_TIME
    }

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

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT COUNT(*) AS c FROM staff')
            staff_count = cur.fetchone()['c']

            cur.execute('SELECT COUNT(*) AS c FROM attendances '\
                        'WHERE DATE(checkin_time)=CURDATE()')
            today_attendance = cur.fetchone()['c']

            cur.execute('SELECT COUNT(*) AS c FROM leaves')
            leave_count = cur.fetchone()['c']

            cur.execute('SELECT COUNT(*) AS c FROM trainings')
            training_count = cur.fetchone()['c']

            cur.execute('SELECT COUNT(*) AS c FROM activities')
            activity_count = cur.fetchone()['c']

            cur.execute('SELECT COUNT(*) AS c FROM behaviors')
            behavior_count = cur.fetchone()['c']
    finally:
        conn.close()

    return render_template(
        'index.html',
        title='หน้าหลัก',
        staff_count=staff_count,
        today_attendance=today_attendance,
        leave_count=leave_count,
        training_count=training_count,
        activity_count=activity_count,
        behavior_count=behavior_count,
    )

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

    from datetime import date

    message = ''
    selected_date = request.values.get('work_date') or date.today().isoformat()

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT DISTINCT department FROM staff ORDER BY department')
            departments = [row['department'] or '' for row in cur.fetchall()]

            cur.execute('SELECT id, full_name, department FROM staff ORDER BY department, full_name')
            rows = cur.fetchall()
            staff_by_dept = {}
            for row in rows:
                dept = row['department'] or ''
                staff_by_dept.setdefault(dept, []).append(row)

            cur.execute('SELECT id, staff_id, checkin_time, checkout_time FROM attendances '
                        'WHERE DATE(checkin_time)=%s OR DATE(checkout_time)=%s',
                        (selected_date, selected_date))
            attendance_rows = cur.fetchall()
            attendance_map = {r['staff_id']: r for r in attendance_rows}

            if request.method == 'POST' and request.form.get('action') == 'save':
                for dept_list in staff_by_dept.values():
                    for st in dept_list:
                        cid = f'checkin_{st["id"]}'
                        coid = f'checkout_{st["id"]}'
                        checkin = request.form.get(cid)
                        checkout = request.form.get(coid)
                        if st['id'] in attendance_map:
                            att_id = attendance_map[st['id']]['id']
                            cur.execute(
                                'UPDATE attendances SET checkin_time=%s, checkout_time=%s WHERE id=%s',
                                (f"{selected_date} {checkin}" if checkin else None,
                                 f"{selected_date} {checkout}" if checkout else None,
                                 att_id)
                            )
                        elif checkin or checkout:
                            cur.execute(
                                'INSERT INTO attendances (staff_id, checkin_time, checkout_time)'
                                ' VALUES (%s,%s,%s)',
                                (st['id'],
                                 f"{selected_date} {checkin}" if checkin else None,
                                 f"{selected_date} {checkout}" if checkout else None)
                            )
                conn.commit()
                message = 'บันทึกข้อมูลเรียบร้อยแล้ว'
                cur.execute('SELECT id, staff_id, checkin_time, checkout_time FROM attendances '
                            'WHERE DATE(checkin_time)=%s OR DATE(checkout_time)=%s',
                            (selected_date, selected_date))
                attendance_rows = cur.fetchall()
                attendance_map = {r['staff_id']: r for r in attendance_rows}

    finally:
        conn.close()

    return render_template('attendance.html',
                           departments=departments,
                           staff_by_dept=staff_by_dept,
                           attendance=attendance_map,
                           selected_date=selected_date,
                           message=message,
                           title='บันทึกเวลา')

# ----- Attendance Stats -----

@bp.route('/attendance-stats')
def attendance_stats():
    if not sso_authenticated():
        return redirect(url_for('hrm.login'))

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT YEAR(checkin_time) AS y, COUNT(*) AS c "
                "FROM attendances GROUP BY y ORDER BY y"
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    labels = [str(r['y']) for r in rows]
    counts = [r['c'] for r in rows]
    return render_template('attendance_stats.html',
                           labels=json.dumps(labels),
                           counts=json.dumps(counts),
                           title='สถิติการเข้างาน')


@bp.route('/attendance-stats/data')
def attendance_stats_data():
    if not sso_authenticated():
        return {}, 403

    year = request.args.get('year')
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if year:
                cur.execute(
                    "SELECT DATE_FORMAT(checkin_time,'%Y-%m') AS m, COUNT(*) AS c "
                    "FROM attendances WHERE YEAR(checkin_time)=%s "
                    "GROUP BY m ORDER BY m",
                    (year,),
                )
                rows = cur.fetchall()
                labels = [r['m'] for r in rows]
                counts = [r['c'] for r in rows]
            else:
                cur.execute(
                    "SELECT YEAR(checkin_time) AS y, COUNT(*) AS c "
                    "FROM attendances GROUP BY y ORDER BY y"
                )
                rows = cur.fetchall()
                labels = [str(r['y']) for r in rows]
                counts = [r['c'] for r in rows]
    finally:
        conn.close()

    return {'labels': labels, 'counts': counts}

# ----- Staff Management -----

@bp.route('/staff')
def staff():
    if not sso_authenticated():
        return redirect(url_for('hrm.login'))

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT id, national_id, full_name, position, department, division, start_date, email, phone, note FROM staff ORDER BY id')
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
                form.get('email'),
                form.get('note'),
                form.get('phone'),
            )
            with conn.cursor() as cur:
                if form.get('id'):
                    cur.execute(
                        'UPDATE employee_histories SET national_id=%s, full_name=%s, position=%s, '
                        'department=%s, division=%s, start_date=%s, email=%s, note=%s, phone=%s WHERE id=%s',
                        data + (form.get('id'),)
                    )
                    message = 'แก้ไขข้อมูลเรียบร้อยแล้ว'
                else:
                    cur.execute(
                        'INSERT INTO employee_histories (national_id, full_name, position, department, '
                        'division, start_date, email, note, phone) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
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

# ----- Activities -----

@bp.route('/activities', methods=['GET', 'POST'])
def activities():
   if not sso_authenticated():
        return redirect(url_for('hrm.login'))

@bp.route('/trainings', methods=['GET', 'POST'])
def trainings():
   if not sso_authenticated():
        return redirect(url_for('hrm.login'))

@bp.route('/leaves', methods=['GET', 'POST'])
def leaves():
    if not sso_authenticated():
        return redirect(url_for('hrm.login'))

    message = ''
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if request.method == 'POST':
                cur.execute(
                    'INSERT INTO activities (staff_id, activity_name, activity_date, description) '
                    'VALUES (%s,%s,%s,%s)',
                    (
                        request.form.get('staff_id'),
                        request.form.get('activity_name'),
                        request.form.get('activity_date'),
                        request.form.get('description'),
                    ),
                )
                conn.commit()
                message = 'บันทึกกิจกรรมเรียบร้อยแล้ว'

            cur.execute(
                'SELECT a.id, s.full_name, a.activity_name, a.activity_date, a.description '
                'FROM activities a JOIN staff s ON a.staff_id=s.id '
                'ORDER BY a.activity_date DESC, a.id DESC'
            )
            rows = cur.fetchall()
            cur.execute('SELECT id, full_name FROM staff ORDER BY full_name')
            staff_list = cur.fetchall()

    edit_record = None
    open_modal = False
    conn = get_connection()
    try:
        if request.method == 'POST':
            form = request.form
            data = (
                form.get('staff_id'),
                form.get('topic'),
                form.get('place'),
                form.get('start_date'),
                form.get('end_date'),
                form.get('description'),
            )
            with conn.cursor() as cur:
                if form.get('id'):
                    cur.execute(
                        'UPDATE trainings SET staff_id=%s, topic=%s, place=%s, start_date=%s, end_date=%s, description=%s WHERE id=%s',
                        data + (form.get('id'),),
                    )
                    message = 'แก้ไขข้อมูลเรียบร้อยแล้ว'
                else:
                    cur.execute(
                        'INSERT INTO trainings (staff_id, topic, place, start_date, end_date, description) VALUES (%s,%s,%s,%s,%s,%s)',
                        data,
                    )
                    message = 'เพิ่มข้อมูลเรียบร้อยแล้ว'
                conn.commit()

        edit_id = request.args.get('edit_id')
        with conn.cursor() as cur:
            cur.execute('SELECT id, full_name FROM staff ORDER BY full_name')
            staff_list = cur.fetchall()

        if edit_id:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM trainings WHERE id=%s', (edit_id,))
                edit_record = cur.fetchone()
            open_modal = True
        elif request.args.get('add'):
            open_modal = True

        with conn.cursor() as cur:
            cur.execute('SELECT t.*, s.full_name FROM trainings t JOIN staff s ON t.staff_id=s.id ORDER BY t.id')
            rows = cur.fetchall()

    finally:
        conn.close()

    return render_template(
        'activities.html',
        activities=rows,
        staff_list=staff_list,
        message=message,
        title='กิจกรรม',
        'trainings.html',
        training_list=rows,
        staff_list=staff_list,
        edit_record=edit_record,
        message=message,
        open_modal=open_modal,
        title='อบรม/ดูงาน',
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
