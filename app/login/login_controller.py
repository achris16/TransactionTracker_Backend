"""
app/login/login_controller.py
- '/login': ['POST']
"""

from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

from app import db

class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=True, nullable=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return '<User %r>' % self.username

# User
class UserResource(Resource):
    def get(self, user_id):
        print(user_id)
        try:
            data = User.query.get(user_id)
        except SQLAlchemyError as err:
            print(err)
            abort(400, error=err)
        print(data)
        if data is None:
            abort(400, error="User could not be found.")

        return {"User": data.username}

# class RegisterResource(Resource):
#     def post(self):
        # Get the request data e.g. email, password
        # Check that the email is not registered already if it is send an error
        # Hash the password and add the user to the database
        # Send success 201 response


# class LoginResource(Resource):
#     def post(self):
        # Get the request data e.g. email, password
        # Query the database via email if no user send an error
        # Check that the users password in the payload matches database
        # Issue a new JWT with 200 response
    