from flask import render_template, request, redirect, url_for
from . import bp
from .utils import get_connection, sso_authenticated

@bp.route('/departments', methods=['GET', 'POST'])
def departments():
    if not sso_authenticated():
        return redirect(url_for('hrm.login'))

    message = ''
    edit_record = None
    open_modal = False
    conn = get_connection()
    try:
        if request.method == 'POST':
            form = request.form
            with conn.cursor() as cur:
                if form.get('orig_code'):
                    cur.execute(
                        'UPDATE departments SET dept_name=%s, description=%s WHERE dept_code=%s',
                        (form.get('dept_name'), form.get('description'), form.get('orig_code'))
                    )
                    message = 'แก้ไขข้อมูลเรียบร้อยแล้ว'
                else:
                    cur.execute(
                        'INSERT INTO departments (dept_code, dept_name, description) VALUES (%s,%s,%s)',
                        (form.get('dept_code'), form.get('dept_name'), form.get('description'))
                    )
                    message = 'เพิ่มข้อมูลเรียบร้อยแล้ว'
                conn.commit()

        edit_code = request.args.get('edit_code')
        if edit_code:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM departments WHERE dept_code=%s', (edit_code,))
                edit_record = cur.fetchone()
            open_modal = True
        elif request.args.get('add'):
            open_modal = True

        with conn.cursor() as cur:
            cur.execute('SELECT * FROM departments ORDER BY dept_code')
            rows = cur.fetchall()
    finally:
        conn.close()

    return render_template(
        'departments/index.html',
        departments=rows,
        edit_record=edit_record,
        open_modal=open_modal,
        message=message,
        title='หน่วยงาน'
    )
