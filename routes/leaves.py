from flask import render_template, request, redirect, url_for
from . import bp
from .utils import get_connection, sso_authenticated

@bp.route('/leaves', methods=['GET', 'POST'])
def leaves():
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
                form.get('staff_id'),
                form.get('start_date'),
                form.get('end_date'),
                form.get('leave_type'),
                form.get('reason'),
                form.get('status'),
            )
            with conn.cursor() as cur:
                if form.get('id'):
                    cur.execute(
                        'UPDATE leaves SET staff_id=%s, start_date=%s, end_date=%s, leave_type=%s, reason=%s, status=%s WHERE id=%s',
                        data + (form.get('id'),),
                    )
                    message = 'แก้ไขข้อมูลเรียบร้อยแล้ว'
                else:
                    cur.execute(
                        'INSERT INTO leaves (staff_id, start_date, end_date, leave_type, reason, status) VALUES (%s,%s,%s,%s,%s,%s)',
                        data,
                    )
                    message = 'เพิ่มข้อมูลเรียบร้อยแล้ว'
                conn.commit()

        edit_id = request.args.get('edit_id')
        if edit_id:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM leaves WHERE id=%s', (edit_id,))
                edit_record = cur.fetchone()
            open_modal = True
        elif request.args.get('add'):
            open_modal = True

        with conn.cursor() as cur:
            cur.execute(
                'SELECT l.*, s.full_name FROM leaves l JOIN staff s ON l.staff_id=s.id ORDER BY l.start_date DESC'
            )
            rows = cur.fetchall()

            cur.execute('SELECT id, full_name FROM staff ORDER BY full_name')
            staff_rows = cur.fetchall()
    finally:
        conn.close()

    return render_template(
        'leaves.html',
        leave_list=rows,
        staff_list=staff_rows,
        edit_record=edit_record,
        message=message,
        open_modal=open_modal,
        title='การลา',
    )
