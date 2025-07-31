from flask import render_template, redirect, url_for
from . import bp
from .utils import get_connection, sso_authenticated

@bp.route('/behaviors')
def behaviors():
    if not sso_authenticated():
        return redirect(url_for('hrm.login'))

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT b.id, s.full_name, b.behavior_date, b.description, b.note '
                'FROM behaviors b JOIN staff s ON b.staff_id=s.id '
                'ORDER BY b.behavior_date DESC, b.id DESC'
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    return render_template('behaviors.html', behaviors=rows, title='บันทึกพฤติกรรม')
