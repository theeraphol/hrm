from flask import Flask, redirect, url_for
from config import Config
from routes import bp, register_routes
from routes.utils import init_oauth

VERSION = Config.VERSION

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY or 'dev'

@app.context_processor
def inject_globals():
    return {
        'app_version': VERSION,
        'default_checkin': Config.DEFAULT_CHECKIN_TIME,
        'default_checkout': Config.DEFAULT_CHECKOUT_TIME,
        'work_status': Config.WORK_STATUS,
    }

# Initialize OAuth for SSO if configured
init_oauth(app)

# Register route modules
register_routes()
app.register_blueprint(bp)

@app.route('/')
def root_redirect():
    return redirect(url_for('hrm.index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.SERVER_PORT, debug=True)
