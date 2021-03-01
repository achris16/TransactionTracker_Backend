"""
app/config.py
- settings for the flask application object
"""


class BaseConfig(object):
    # Flask
    DEBUG = True

    # SQLAlchemy
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///todo.db'
    SQLALCHEMY_DATABASE_URI = 'mysql://flask_user:test@localhost/flask_dev'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    SECRET_KEY = 'f028ddf9faebed44d1f8bc60b98dd504'
