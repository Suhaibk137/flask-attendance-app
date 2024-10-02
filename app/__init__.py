# app/__init__.py

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'  # Replace with a secure secret key

    # Get the absolute path of the project root directory
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Set the database URI to use the absolute path
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'attendance.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    # Register blueprints
    from .routes import main
    app.register_blueprint(main)

    return app
