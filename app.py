from flask import Flask, Blueprint, request, session, redirect, url_for, render_template
from authlib.integrations.flask_client import OAuth
import pymysql
from config import Config


VERSION = Config.VERSION

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# ใช้ Blueprint เพื่อติดตั้งเส้นทางทั้งหมดภายใต้ /service_queue
bp = Blueprint('service_queue', __name__, url_prefix='/service_queue')

@app.context_processor
def inject_version():
    return {'app_version': VERSION}

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
    """สร้างการเชื่อมต่อ MariaDB ใหม่"""
    return pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# ----- Utility -----

def sso_authenticated():
    """Return True if staff user logged in via SSO."""
    return session.get('staff_user') is not None

def ensure_default_ids(cur, dept_id=None):
    """ตรวจสอบหรือสร้างข้อมูล department และ service"""
    if dept_id:
        cur.execute("SELECT id FROM departments WHERE id=%s", (dept_id,))
        row = cur.fetchone()
        if not row:
            cur.execute(
                "INSERT INTO departments (name, description) VALUES (%s, %s)",
                ("งานบริการทั่วไป", "สร้างโดยระบบ"),
            )
            dept_id = cur.lastrowid
    else:
        cur.execute("SELECT id FROM departments ORDER BY id LIMIT 1")
        row = cur.fetchone()
        if row:
            dept_id = row["id"]
        else:
            cur.execute(
                "INSERT INTO departments (name, description) VALUES (%s, %s)",
                ("งานบริการทั่วไป", "สร้างโดยระบบ"),
            )
            dept_id = cur.lastrowid

    cur.execute(
        "SELECT id FROM services WHERE department_id=%s ORDER BY id LIMIT 1",
        (dept_id,),
    )
    row = cur.fetchone()
    if row:
        service_id = row["id"]
    else:
        cur.execute(
            "INSERT INTO services (department_id, name, description) VALUES (%s, %s, %s)",
            (dept_id, "บริการทั่วไป", "สร้างโดยระบบ"),
        )
        service_id = cur.lastrowid
    return dept_id, service_id

# ----- Routes -----

@bp.route('/')
def index():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM departments ORDER BY name")
            departments = cur.fetchall()
    finally:
        conn.close()
    return render_template('index.html', title="จองบัตรคิว", departments=departments)

@bp.route('/book', methods=['POST'])
def book():
    """บันทึกคิวใหม่ลงฐานข้อมูล"""
    id_card = request.form['id_card']
    dept_id_form = request.form.get('department_id')
    dept_id_int = int(dept_id_form) if dept_id_form else None
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM citizens WHERE national_id=%s", (id_card,))
            row = cur.fetchone()
            if row:
                citizen_id = row['id']
            else:
                cur.execute(
                    "INSERT INTO citizens (national_id, full_name) VALUES (%s, '')",
                    (id_card,),
                )
                citizen_id = cur.lastrowid

            dept_id, service_id = ensure_default_ids(cur, dept_id_int)

            cur.execute(
                "SELECT IFNULL(MAX(queue_number), 0) AS max_q FROM queues WHERE service_date=CURDATE()"
            )
            max_q = cur.fetchone()["max_q"]
            next_q = int(max_q) + 1

            cur.execute(
                """
                INSERT INTO queues (citizen_id, department_id, service_id, queue_number, service_date)
                VALUES (%s, %s, %s, %s, CURDATE())
                """,
                (citizen_id, dept_id, service_id, str(next_q)),
            )
        conn.commit()
    finally:
        conn.close()
    return render_template('success.html', number=next_q, title="ผลการจองคิว")

@bp.route('/login')
def login():
    """เริ่มกระบวนการเข้าสู่ระบบผ่าน SSO ถ้ามีการตั้งค่า"""
    if oauth:
        token_param = request.args.get('token')
        if token_param:
            token = {'id_token': token_param}
            userinfo = oauth.sso.parse_id_token(token)
            session['staff_user'] = userinfo.get('name') or userinfo.get('preferred_username')
            return redirect(url_for('service_queue.staff'))
        redirect_uri = url_for('service_queue.authorize', _external=True)
        extra = {}
        if Config.SSO_SECRET_KEY:
            extra['sso_secret_key'] = Config.SSO_SECRET_KEY
        return oauth.sso.authorize_redirect(redirect_uri, **extra)
    user = request.args.get('user')
    if user:
        session['staff_user'] = user
        return redirect(url_for('service_queue.staff'))
    return render_template('login.html', title="เข้าสู่ระบบ")


@bp.route('/authorize')
def authorize():
    """รับผลลัพธ์จาก SSO และบันทึกข้อมูลผู้ใช้"""
    if not oauth:
        return redirect(url_for('service_queue.login'))
    token = oauth.sso.authorize_access_token()
    userinfo = oauth.sso.parse_id_token(token)
    session['staff_user'] = userinfo.get('name') or userinfo.get('preferred_username')
    return redirect(url_for('service_queue.staff'))

@bp.route('/staff')
def staff():
    if not sso_authenticated():
        return redirect(url_for('service_queue.login'))
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT q.queue_number AS number, c.national_id AS id_card
                FROM queues q
                JOIN citizens c ON q.citizen_id=c.id
                WHERE q.service_status='รอเรียก'
                ORDER BY q.queue_number
                """
            )
            rows = cur.fetchall()
    finally:
        conn.close()
    return render_template('staff.html', queues=rows, title="รายการคิว")


@bp.route('/staff/call', methods=['GET', 'POST'])
def call_next():
    if not sso_authenticated():
        return redirect(url_for('service_queue.login'))

    message = ''
    action = request.form.get('action') if request.method == 'POST' else None
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if request.method == 'POST' and action == 'next':
                cur.execute(
                    """
                    SELECT q.id, q.queue_number, c.national_id
                    FROM queues q
                    JOIN citizens c ON q.citizen_id=c.id
                    WHERE q.service_status='รอเรียก'
                    ORDER BY q.queue_number
                    LIMIT 1
                    """
                )
                row = cur.fetchone()
                if row:
                    cur.execute(
                        "UPDATE queues SET service_status='ให้บริการแล้ว', called_time=NOW() WHERE id=%s",
                        (row['id'],)
                    )
                    conn.commit()
                    message = f"เรียกคิวหมายเลข {row['queue_number']} หมายเลขบัตร {row['national_id']}"
                else:
                    message = 'ไม่มีคิวค้างอยู่'
            elif request.method == 'POST' and action == 'new':
                return redirect(url_for('service_queue.index'))
    finally:
        conn.close()

    return render_template('call.html', message=message, title="เรียกคิว")

app.register_blueprint(bp)

# เส้นทางหลักเพื่อให้เปิดได้ที่ http://<host>:<port> โดยไม่ต้องพิมพ์เครื่องหมาย /
@app.route('/')
def root_redirect():
    return redirect(url_for('service_queue.index'))

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=4999, debug=True)

