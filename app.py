import os
from flask import Flask, Blueprint, request, session, redirect, url_for, render_template
from authlib.integrations.flask_client import OAuth
import pymysql

VERSION = "0.6.2"

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'BST-bangsithong-app-SECRET_KEY-024467684')

# ใช้ Blueprint เพื่อติดตั้งเส้นทางทั้งหมดภายใต้ /service_queue
bp = Blueprint('service_queue', __name__, url_prefix='/service_queue')

oauth = OAuth(app)
if os.environ.get('SSO_CLIENT_ID'):
    oauth.register(
        name='sso',
        client_id=os.environ.get('SSO_CLIENT_ID'),
        client_secret=os.environ.get('SSO_CLIENT_SECRET'),
        authorize_url=os.environ.get('SSO_AUTHORIZE_URL'),
        access_token_url=os.environ.get('SSO_TOKEN_URL'),
        userinfo_endpoint=os.environ.get('SSO_USERINFO_URL'),
        client_kwargs={'scope': 'openid profile email'}
    )
else:
    oauth = None

# ----- Database -----

def get_connection():
    """สร้างการเชื่อมต่อ MariaDB ใหม่"""
    return pymysql.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        port=int(os.environ.get('DB_PORT', 3306)),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# ----- Utility -----

def sso_authenticated():
    """Return True if staff user logged in via SSO."""
    return session.get('staff_user') is not None

# ----- Routes -----

@bp.route('/')
def index():
    return render_template('index.html', title="จองบัตรคิว")

@bp.route('/book', methods=['POST'])
def book():
    """บันทึกคิวใหม่ลงฐานข้อมูล"""
    id_card = request.form['id_card']
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
                    (id_card,)
                )
                citizen_id = cur.lastrowid

            cur.execute(
                "SELECT IFNULL(MAX(queue_number), 0) AS max_q FROM queues WHERE service_date=CURDATE()"
            )
            max_q = cur.fetchone()["max_q"]
            next_q = int(max_q) + 1

            cur.execute(
                """
                INSERT INTO queues (citizen_id, department_id, service_id, queue_number, service_date)
                VALUES (%s, 1, 1, %s, CURDATE())
                """,
                (citizen_id, str(next_q)),
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
        if os.environ.get('SSO_SECRET_KEY'):
            extra['sso_secret_key'] = os.environ['SSO_SECRET_KEY']
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
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if request.method == 'POST':
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
    finally:
        conn.close()

    return render_template('call.html', message=message, title="เรียกคิว")

app.register_blueprint(bp)

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=4999, debug=True)

