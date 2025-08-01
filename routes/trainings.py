from flask import render_template, request, redirect, url_for
from . import bp
from .utils import get_connection, sso_authenticated

@bp.route('/trainings', methods=['GET', 'POST'])
def trainings():
    if not sso_authenticated():
        return redirect(url_for('hrm.login'))

    message = ''
    edit_record = None
    open_modal = False
    departments = []
    staff_list = []
    conn = get_connection()
    try:
        if request.method == 'POST':
            form = request.form
            data = (
                form.get('staff_id'),
                form.get('topic'),
                form.get('place'),
                form.get('start_date'),
                form.get('end_date'),
                form.get('description'),
            )
            with conn.cursor() as cur:
                if form.get('id'):
                    cur.execute(
                        'UPDATE trainings SET staff_id=%s, topic=%s, place=%s, start_date=%s, end_date=%s, description=%s WHERE id=%s',
                        data + (form.get('id'),),
                    )
                    message = 'แก้ไขข้อมูลเรียบร้อยแล้ว'
                else:
                    cur.execute(
                        'INSERT INTO trainings (staff_id, topic, place, start_date, end_date, description) VALUES (%s,%s,%s,%s,%s,%s)',
                        data,
                    )
                    message = 'เพิ่มข้อมูลเรียบร้อยแล้ว'
                conn.commit()

        with conn.cursor() as cur:
            cur.execute('SELECT dept_name FROM departments ORDER BY dept_code')
            departments = cur.fetchall()

            cur.execute('SELECT id, full_name, department FROM staff ORDER BY department, full_name')
            staff_list = cur.fetchall()

        edit_id = request.args.get('edit_id')

        if edit_id:
            with conn.cursor() as cur:
                cur.execute('SELECT t.*, s.department FROM trainings t JOIN staff s ON t.staff_id=s.id WHERE t.id=%s', (edit_id,))
                edit_record = cur.fetchone()
            open_modal = True
        elif request.args.get('add'):
            open_modal = True

        with conn.cursor() as cur:
            cur.execute('SELECT t.*, s.full_name FROM trainings t JOIN staff s ON t.staff_id=s.id ORDER BY t.id')
            rows = cur.fetchall()
    finally:
        conn.close()

    return render_template(
        'trainings.html',
        training_list=rows,
        staff_list=staff_list,
        departments=departments,
        edit_record=edit_record,
        message=message,
        open_modal=open_modal,
        title='อบรม/ดูงาน',
    )
