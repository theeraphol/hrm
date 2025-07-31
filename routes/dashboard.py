from flask import render_template, redirect, url_for
from . import bp
from .utils import get_connection, sso_authenticated

@bp.route('/')
def index():
    if not sso_authenticated():
        return redirect(url_for('hrm.login'))

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT COUNT(*) AS c FROM staff')
            staff_count = cur.fetchone()['c']

            cur.execute('SELECT COUNT(*) AS c FROM attendances WHERE DATE(checkin_time)=CURDATE()')
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
