from flask import render_template, redirect, url_for
from . import bp
from .utils import get_connection, sso_authenticated

@bp.route('/staff')
def staff():
    if not sso_authenticated():
        return redirect(url_for('hrm.login'))

    conn = get_connection()
    departments = []
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT id, national_id, full_name, position, department, division, start_date, email, phone, note FROM staff ORDER BY id')
            rows = cur.fetchall()
            cur.execute('SELECT dept_name FROM departments ORDER BY dept_code')
            departments = cur.fetchall()
    finally:
        conn.close()
    return render_template('staff.html', staff_list=rows, departments=departments, title='ข้อมูลบุคลากร')
