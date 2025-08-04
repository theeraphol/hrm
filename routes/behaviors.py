from flask import render_template, request, redirect, url_for
from . import bp
from .utils import get_connection, sso_authenticated

@bp.route('/behaviors', methods=['GET', 'POST'])
def behaviors():
    if not sso_authenticated():
        return redirect(url_for('hrm.login'))

    message = ''
    open_modal = False
    departments = []
    staff_list = []
    conn = get_connection()
    try:
        if request.method == 'POST':
            form = request.form
            with conn.cursor() as cur:
                cur.execute(
                    'INSERT INTO behaviors (staff_id, behavior_date, description, note) '
                    'VALUES (%s,%s,%s,%s)',
                    (
                        form.get('staff_id'),
                        form.get('behavior_date'),
                        form.get('description'),
                        form.get('note'),
                    ),
                )
                conn.commit()
                message = 'เพิ่มข้อมูลเรียบร้อยแล้ว'

        with conn.cursor() as cur:
            cur.execute(
                'SELECT b.id, s.full_name, s.department, b.behavior_date, b.description, b.note '
                'FROM behaviors b JOIN staff s ON b.staff_id=s.id '
                'ORDER BY b.behavior_date DESC, b.id DESC'
            )
            rows = cur.fetchall()
            cur.execute('SELECT id, full_name FROM staff ORDER BY full_name')
            staff_list = cur.fetchall()
            cur.execute('SELECT dept_name FROM departments ORDER BY dept_code')
            departments = cur.fetchall()
    finally:
        conn.close()

    if request.args.get('add'):
        open_modal = True

    return render_template(
        'behaviors.html',
        behaviors=rows,
        staff_list=staff_list,
        departments=departments,
        message=message,
        open_modal=open_modal,
        title='บันทึกพฤติกรรม',
    )
