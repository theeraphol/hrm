from flask import render_template, redirect, url_for
from . import bp
from .utils import sso_authenticated

@bp.route('/about')
def about():
    if not sso_authenticated():
        return redirect(url_for('hrm.login'))
    return render_template('about.html', title='เกี่ยวกับระบบ')
