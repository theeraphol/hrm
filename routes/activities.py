from flask import render_template, request, redirect, url_for
from . import bp
from .utils import get_connection, sso_authenticated

@bp.route('/activities', methods=['GET', 'POST'])
def activities():
    if not sso_authenticated():
        return redirect(url_for('hrm.login'))

    message = ''
    departments = []
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
                'SELECT a.id, s.full_name, s.department, a.activity_name, a.activity_date, a.description '
                'FROM activities a JOIN staff s ON a.staff_id=s.id '
                'ORDER BY a.activity_date DESC, a.id DESC'
            )
            rows = cur.fetchall()
            cur.execute('SELECT id, full_name FROM staff ORDER BY full_name')
            staff_list = cur.fetchall()
            cur.execute('SELECT dept_name FROM departments ORDER BY dept_code')
            departments = cur.fetchall()
    finally:
        conn.close()

    return render_template(
        'activities/index.html',
        activities=rows,
        staff_list=staff_list,
        departments=departments,
        message=message,
        title='กิจกรรม',
    )
