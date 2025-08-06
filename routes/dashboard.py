from flask import render_template, redirect, url_for
from . import bp
from .utils import get_connection, sso_authenticated
from datetime import date, timedelta

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

            cur.execute(
                """
                SELECT DATE(checkin_time) AS d, COUNT(*) AS c
                FROM attendances
                WHERE checkin_time >= CURDATE() - INTERVAL 6 DAY
                GROUP BY d
                ORDER BY d
                """
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    stats_map = {row['d']: row['c'] for row in rows}
    last7 = [date.today() - timedelta(days=i) for i in range(6, -1, -1)]
    attendance_labels = [d.strftime('%d/%m') for d in last7]
    attendance_data = [stats_map.get(d, 0) for d in last7]

    return render_template(
        'dashboard/index.html',
        title='หน้าหลัก',
        staff_count=staff_count,
        today_attendance=today_attendance,
        leave_count=leave_count,
        training_count=training_count,
        activity_count=activity_count,
        behavior_count=behavior_count,
        attendance_labels=attendance_labels,
        attendance_data=attendance_data,
    )
