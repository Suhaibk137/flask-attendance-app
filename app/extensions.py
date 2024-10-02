# app/extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

@login_manager.user_loader
def load_user(user_id):
    from .models import Employee, Admin
    user = Employee.query.get(int(user_id))
    if not user:
        user = Admin.query.get(int(user_id))
    return user
