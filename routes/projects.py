from flask import render_template, request, redirect, url_for
from . import bp
from .utils import get_connection, sso_authenticated


@bp.route('/projects', methods=['GET', 'POST'])
def projects():
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
                form.get('project_name'),
                form.get('start_date'),
                form.get('end_date'),
                form.get('status'),
                form.get('description'),
            )
            with conn.cursor() as cur:
                if form.get('id'):
                    cur.execute(
                        'UPDATE projects SET project_name=%s, start_date=%s, end_date=%s, status=%s, description=%s WHERE id=%s',
                        data + (form.get('id'),),
                    )
                    message = 'แก้ไขข้อมูลเรียบร้อยแล้ว'
                else:
                    cur.execute(
                        'INSERT INTO projects (project_name, start_date, end_date, status, description) VALUES (%s,%s,%s,%s,%s)',
                        data,
                    )
                    message = 'เพิ่มข้อมูลเรียบร้อยแล้ว'
                conn.commit()

        edit_id = request.args.get('edit_id')
        if edit_id:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM projects WHERE id=%s', (edit_id,))
                edit_record = cur.fetchone()
            open_modal = True
        elif request.args.get('add'):
            open_modal = True

        with conn.cursor() as cur:
            cur.execute('SELECT * FROM projects ORDER BY start_date DESC, id DESC')
            rows = cur.fetchall()
    finally:
        conn.close()

    return render_template(
        'projects/index.html',
        project_list=rows,
        edit_record=edit_record,
        message=message,
        open_modal=open_modal,
        title='โครงการ',
    )
