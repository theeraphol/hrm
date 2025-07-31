from flask import render_template, request, redirect, url_for
from . import bp
from .utils import get_connection, sso_authenticated

@bp.route('/history', methods=['GET', 'POST'])
def history():
    if not sso_authenticated():
        return redirect(url_for('hrm.login'))

    message = ''
    edit_record = None
    open_modal = False
    conn = get_connection()
    try:
        if request.method == 'POST':
            form = request.form
            data = (
                form.get('national_id'),
                form.get('full_name'),
                form.get('position'),
                form.get('department'),
                form.get('division'),
                form.get('start_date'),
                form.get('email'),
                form.get('note'),
                form.get('phone'),
            )
            with conn.cursor() as cur:
                if form.get('id'):
                    cur.execute(
                        'UPDATE employee_histories SET national_id=%s, full_name=%s, position=%s, '
                        'department=%s, division=%s, start_date=%s, email=%s, note=%s, phone=%s WHERE id=%s',
                        data + (form.get('id'),),
                    )
                    message = 'แก้ไขข้อมูลเรียบร้อยแล้ว'
                else:
                    cur.execute(
                        'INSERT INTO employee_histories (national_id, full_name, position, department, '
                        'division, start_date, email, note, phone) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                        data
                    )
                    message = 'เพิ่มข้อมูลเรียบร้อยแล้ว'
                conn.commit()

        edit_id = request.args.get('edit_id')
        if edit_id:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM employee_histories WHERE id=%s', (edit_id,))
                edit_record = cur.fetchone()
            open_modal = True
        elif request.args.get('add'):
            open_modal = True

        with conn.cursor() as cur:
            cur.execute('SELECT * FROM employee_histories ORDER BY id')
            rows = cur.fetchall()
    finally:
        conn.close()
    return render_template(
        'history.html',
        history_list=rows,
        edit_record=edit_record,
        message=message,
        open_modal=open_modal,
        title='ประวัติพนักงาน',
    )
