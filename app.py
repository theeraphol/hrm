from flask import Flask, request, session, redirect, url_for, render_template_string

app = Flask(__name__)
app.secret_key = 'change-me'

queues = []
next_queue = 1

# ----- Utility -----

def sso_authenticated():
    """Return True if staff user logged in via SSO."""
    return session.get('staff_user') is not None

# ----- Routes -----

@app.route('/')
def index():
    form_html = """
    <h1>จองบัตรคิว</h1>
    <form method="post" action="/book">
      <label>ชื่อผู้ขอรับบริการ:</label>
      <input type="text" name="name" required>
      <button type="submit">จองคิว</button>
    </form>
    """
    return render_template_string(form_html)

@app.route('/book', methods=['POST'])
def book():
    global next_queue
    name = request.form['name']
    queue = {'number': next_queue, 'name': name}
    queues.append(queue)
    next_queue += 1
    return f"จองคิวสำเร็จ หมายเลขคิว {queue['number']}"

@app.route('/login')
def login():
    """Stub SSO login. In real usage redirect to SSO provider."""
    user = request.args.get('user')
    if user:
        session['staff_user'] = user
        return redirect(url_for('staff'))
    return 'Redirect to your SSO provider and return with ?user=ID'

@app.route('/staff')
def staff():
    if not sso_authenticated():
        return redirect(url_for('login'))
    queue_list = ''.join(f"<li>{q['number']} - {q['name']}</li>" for q in queues)
    staff_html = f"""
    <h1>รายการคิว</h1>
    <ul>{queue_list}</ul>
    """
    return render_template_string(staff_html)


@app.route('/staff/call', methods=['GET', 'POST'])
def call_next():
    if not sso_authenticated():
        return redirect(url_for('login'))

    message = ''
    if request.method == 'POST':
        if queues:
            current = queues.pop(0)
            message = f"เรียกคิวหมายเลข {current['number']} คุณ {current['name']}"
        else:
            message = 'ไม่มีคิวค้างอยู่'

    call_html = f"""
    <h1>เรียกคิว</h1>
    <form method="post">
      <button type="submit">เรียกคิวถัดไป</button>
    </form>
    <p>{message}</p>
    """
    return render_template_string(call_html)

if __name__ == '__main__':
    app.run(debug=True)
