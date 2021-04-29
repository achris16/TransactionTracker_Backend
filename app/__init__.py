"""
application.py
- creates a Flask app instance and registers the database object
"""

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
# from flask_marshmallow import Marshmallow

db = SQLAlchemy()

def create_app(app_name='TRANSACTION_TRACKER_API'):
    app = Flask(app_name)
    app.config.from_object('app.config.BaseConfig')

    cors = CORS(app, resources={r"/api/v1/*": {"origins": "*"}})

    from app.login import api as login_api
    login_api.init_app(app)
    
    from app.transaction import api as transaction_api
    transaction_api.init_app(app)

    db.init_app(app)   

    return app

