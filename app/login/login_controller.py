"""
app/login/login_controller.py
- '/login': ['POST']
- '/register': ['POST']
"""

from datetime import datetime, timedelta
from flask import current_app, Flask, make_response, jsonify
from flask_restful import reqparse, abort, Api, Resource
from flask_sqlalchemy import SQLAlchemy
import jwt
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash

from app import db

class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=True, nullable=False)

    def __init__(self, email, password):
        self.email = email
        self.password = generate_password_hash(password, method='sha256')

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return '<User %r>' % self.email

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('email', type=str, required=True, help='Email is required')
parser.add_argument('password', type=str, required=True, help='Password is required')

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

        return {"User": data.email}


class RegisterResource(Resource):
    def post(self):
        # Get the request data e.g. email, password
        request_data = parser.parse_args()
        print(request_data)
        
        # Check that the email is not registered already if it is send an error
        db_user = User.query.filter_by(email=request_data['email']).first()
        if not db_user:
            try:
                # Hash the password and add the user to the database
                new_user = User(request_data['email'], request_data['password'])
                db.session.add(new_user)
                db.session.commit()
                response = {
                    'message': 'Register success',
                    'email': new_user.email,
                }
                # Send success 201 response
                status = 201
            except Exception as e:
                print(e)
                response = {'message': 'Internal server error.'}
                status = 500
        else:
            response = {'message': 'User already exists. Please Log in.'}
            status = 400

        return make_response(jsonify(response), status)


class LoginResource(Resource):
    def post(self):
        # Get the request data e.g. email, password
        request_data = parser.parse_args()
        print(request_data)

        # Query the database via email, if no user send an error
        db_user = User.query.filter_by(email=request_data['email']).first()
        if db_user:
            try: 
                # Check that the users password in the payload matches database
                if check_password_hash(db_user.password, request_data['password']):
                    # Issue a new JWT with 200 response
                    token = jwt.encode(
                        {
                            'sub': db_user.id,
                            'iat': datetime.utcnow(),
                            'exp': datetime.utcnow() + timedelta(minutes=30)
                        }, 
                        current_app.config['SECRET_KEY'], 
                        algorithm="HS256"
                    )
                    response = { 
                        'message': 'Login success.',
                        'token': token,
                    }
                    status = 200
                else: 
                    response = {'message': 'Invalid username or password.'}
                    status = 400
            except Exception as e:
                print(e)
                response = {'message': 'Internal server error.'}
                status = 500    
        else:
            response = {'message': 'User does not exist. Please Register.'}
            status = 400
        
        return make_response(jsonify(response), status)
    

