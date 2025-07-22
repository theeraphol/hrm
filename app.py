import os
from flask import Flask, Blueprint, request, session, redirect, url_for, render_template
from authlib.integrations.flask_client import OAuth

VERSION = "0.2.0"

app = Flask(__name__)
app.secret_key = 'change-me'

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

queues = []
next_queue = 1

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
    global next_queue
    id_card = request.form['id_card']
    queue = {'number': next_queue, 'id_card': id_card}
    queues.append(queue)
    next_queue += 1
    return render_template('success.html', number=queue['number'], title="ผลการจองคิว")

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
        return oauth.sso.authorize_redirect(redirect_uri)
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
    return render_template('staff.html', queues=queues, title="รายการคิว")


@bp.route('/staff/call', methods=['GET', 'POST'])
def call_next():
    if not sso_authenticated():
        return redirect(url_for('service_queue.login'))

    message = ''
    if request.method == 'POST':
        if queues:
            current = queues.pop(0)
            message = f"เรียกคิวหมายเลข {current['number']} หมายเลขบัตร {current['id_card']}"
        else:
            message = 'ไม่มีคิวค้างอยู่'

    return render_template('call.html', message=message, title="เรียกคิว")

app.register_blueprint(bp)

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=4999, debug=True)