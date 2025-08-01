from flask import Blueprint

bp = Blueprint('hrm', __name__, url_prefix='/hrm')

# utility functions and oauth will be set up in app.py and imported here

def register_routes():
    from . import dashboard, auth, attendance, staff, history, activities, trainings, leaves, behaviors, projects, backup, about, departments
    # modules register their routes with bp when imported
