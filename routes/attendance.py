from flask import render_template, request, redirect, url_for
import json
from datetime import date
from . import bp
from .utils import get_connection, sso_authenticated

@bp.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if not sso_authenticated():
        return redirect(url_for('hrm.login'))

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
                    (year,)
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
