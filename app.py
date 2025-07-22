import os
from flask import Flask, Blueprint, request, session, redirect, url_for, render_template_string
from authlib.integrations.flask_client import OAuth

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

# ----- HTML Helpers -----

def render_page(body_html: str, title: str = "Service Queue"):
    """สร้างโครงหน้าเว็บด้วย TailwindCSS และ Font Awesome"""
    page_html = f"""
    <!doctype html>
    <html lang=\"th\">
    <head>
      <meta charset=\"utf-8\">
      <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
      <script src=\"https://cdn.tailwindcss.com\"></script>
      <link rel=\"stylesheet\" href=\"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css\"/>
      <title>{title}</title>
    </head>
    <body class=\"bg-gradient-to-br from-blue-50 to-teal-50 min-h-screen flex items-center justify-center\">
      <div class=\"bg-white shadow-lg rounded p-6 w-full max-w-lg\">
        {body_html}
      </div>
    </body>
    </html>
    """
    return render_template_string(page_html)

# ----- Utility -----

def sso_authenticated():
    """Return True if staff user logged in via SSO."""
    return session.get('staff_user') is not None

# ----- Routes -----

@bp.route('/')
def index():
    form_html = f"""
    <h1 class=\"text-2xl font-bold mb-4\"><i class=\"fa-solid fa-qrcode mr-2\"></i>จองบัตรคิว</h1>
    <form method=\"post\" action=\"{url_for('service_queue.book')}\" class=\"space-y-4\">
        <label class=\"block\">
          <span class=\"block mb-1\"><i class=\"fa-solid fa-id-card mr-1\"></i>หมายเลขบัตรประชาชน:</span>
          <input type=\"text\" name=\"id_card\" class=\"border rounded w-full p-2\" required>
        </label>
      <button type=\"submit\" class=\"bg-blue-600 text-white px-4 py-2 rounded\"><i class=\"fa-solid fa-ticket mr-1\"></i>จองคิว</button>
    </form>
    """
    return render_page(form_html, title="จองบัตรคิว")

@bp.route('/book', methods=['POST'])
def book():
    global next_queue
    id_card = request.form['id_card']
    queue = {'number': next_queue, 'id_card': id_card}
    queues.append(queue)
    next_queue += 1
    success_html = f"<p class='bg-green-100 border border-green-400 text-green-700 px-4 py-2 rounded'><i class='fa-solid fa-check-circle mr-1'></i>จองคิวสำเร็จ หมายเลขคิว {queue['number']}</p>"
    return render_page(success_html, title="ผลการจองคิว")

@bp.route('/login')
def login():
    """เริ่มกระบวนการเข้าสู่ระบบผ่าน SSO ถ้ามีการตั้งค่า"""
    if oauth:
        redirect_uri = url_for('service_queue.authorize', _external=True)
        return oauth.sso.authorize_redirect(redirect_uri)
    user = request.args.get('user')
    if user:
        session['staff_user'] = user
        return redirect(url_for('service_queue.staff'))
    return 'Redirect to your SSO provider and return with ?user=ID'


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
    queue_list = ''.join(
        f"<li class='border-b py-1'>{q['number']} - {q['id_card']}</li>" for q in queues
    )
    staff_html = f"""
    <h1 class=\"text-2xl font-bold mb-4\"><i class=\"fa-solid fa-list mr-2\"></i>รายการคิว</h1>
    <ul class=\"border rounded mb-3\">{queue_list}</ul>
    """
    return render_page(staff_html, title="รายการคิว")


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

    call_html = f"""
    <h1 class=\"text-2xl font-bold mb-4\"><i class=\"fa-solid fa-bullhorn mr-2\"></i>เรียกคิว</h1>
    <form method=\"post\" class=\"mb-3\">
      <button type=\"submit\" class=\"bg-blue-600 text-white px-4 py-2 rounded\"><i class=\"fa-solid fa-forward mr-1\"></i>เรียกคิวถัดไป</button>
    </form>
    <p>{message}</p>
    """
    return render_page(call_html, title="เรียกคิว")

app.register_blueprint(bp)

if __name__ == '__main__':
    app.run(debug=True)
