from flask import Flask, request, session, redirect, url_for, render_template_string

app = Flask(__name__)
app.secret_key = 'change-me'

queues = []
next_queue = 1

# ----- HTML Helpers -----

def render_page(body_html: str, title: str = "Service Queue"):
    """Wrap the provided body HTML in a basic Bootstrap page."""
    page_html = f"""
    <!doctype html>
    <html lang="th">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
      <title>{title}</title>
    </head>
    <body class="container py-5">
      {body_html}
    </body>
    </html>
    """
    return render_template_string(page_html)

# ----- Utility -----

def sso_authenticated():
    """Return True if staff user logged in via SSO."""
    return session.get('staff_user') is not None

# ----- Routes -----

@app.route('/')
def index():
    form_html = """
    <h1 class="mb-4">จองบัตรคิว</h1>
    <form method="post" action="/book">
        <div class="mb-3">
          <label class="form-label">หมายเลขบัตรประชาชน:</label>
          <input type="text" name="id_card" class="form-control" required>
        </div>
      <button type="submit" class="btn btn-primary">จองคิว</button>
    </form>
    """
    return render_page(form_html, title="จองบัตรคิว")

@app.route('/book', methods=['POST'])
def book():
    global next_queue
    id_card = request.form['id_card']
    queue = {'number': next_queue, 'id_card': id_card}
    queues.append(queue)
    next_queue += 1
    success_html = f"<p class='alert alert-success'>จองคิวสำเร็จ หมายเลขคิว {queue['number']}</p>"
    return render_page(success_html, title="ผลการจองคิว")

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
    queue_list = ''.join(
        f"<li class='list-group-item'>{q['number']} - {q['id_card']}</li>" for q in queues
    )
    staff_html = f"""
    <h1 class="mb-4">รายการคิว</h1>
    <ul class="list-group mb-3">{queue_list}</ul>
    """
    return render_page(staff_html, title="รายการคิว")


@app.route('/staff/call', methods=['GET', 'POST'])
def call_next():
    if not sso_authenticated():
        return redirect(url_for('login'))

    message = ''
    if request.method == 'POST':
        if queues:
            current = queues.pop(0)
            message = f"เรียกคิวหมายเลข {current['number']} หมายเลขบัตร {current['id_card']}"
        else:
            message = 'ไม่มีคิวค้างอยู่'

    call_html = f"""
    <h1 class="mb-4">เรียกคิว</h1>
    <form method="post" class="mb-3">
      <button type="submit" class="btn btn-primary">เรียกคิวถัดไป</button>
    </form>
    <p>{message}</p>
    """
    return render_page(call_html, title="เรียกคิว")

if __name__ == '__main__':
    app.run(debug=True)
