from datetime import datetime, timedelta
from flask import current_app, Flask, make_response, jsonify
from flask_restful import reqparse, abort, Api, Resource
from flask_sqlalchemy import SQLAlchemy
import jwt
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.login import User

class Transaction(db.Model):
    __tablename__ = 'Transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow())
    updated_date = db.Column(db.DateTime, default=None, onupdate=datetime.utcnow())

    def __init__(self, user_id, amount, description):
        self.user_id = user_id
        self.amount = amount
        self.description = description

    def as_dict(self):
        return {
            'id': self.id,
            'amount': format(self.amount, '.2f'),
            'description': self.description,
            'created_date': self.created_date,
            'updated_date': self.updated_date
        }

    def __repr__(self):
        return '<Transaction %r>' % self.user_id

create_parser = reqparse.RequestParser(bundle_errors=True)
create_parser.add_argument('X-Auth', location='headers', required=True)
create_parser.add_argument('amount', type=str, required=True, help='Amount is required')
create_parser.add_argument('description', type=str, required=True, help='Description is required')
create_parser.add_argument('transactionType', type=str, required=True, help='Transaction Type is required')

get_parser = reqparse.RequestParser(bundle_errors=True)
get_parser.add_argument('X-Auth', location='headers', required=True)

class TransactionIdResource(Resource):
    def put(self, transaction_id):
        # Get the request data e.g. amount, description
        request_data = create_parser.parse_args()
        print(request_data)

        if request_data['transactionType'].lower() == 'debit':
            transaction_amount = -float(request_data['amount'])
        elif request_data['transactionType'].lower() == 'credit':
            transaction_amount = float(request_data['amount'])
        else: 
            response = {'message': 'Transaction Type must be credit or debit'}
            status = 400
            return make_response(jsonify(response), status)

        try:
            token = jwt.decode(
                request_data['X-Auth'],
                current_app.config['SECRET_KEY'],
                algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError as e:
            print(e)
            response = {'message': 'Token expired. Please login.'}
            status = 400
            return make_response(jsonify(response), status)
        except Exception as e:
            print(e)
            response = {'message': 'Internal server error.'}
            status = 500
            return make_response(jsonify(response), status)

        # Check that the user exists if not send an error
        try:
            db_user = User.query.filter_by(id=token['sub']).first()
            if db_user:
                # Make sure the transaction you're updating exists and is assigned to the user
                transaction = Transaction.query.filter(Transaction.user_id == token['sub'], Transaction.id == transaction_id).first()
                print(transaction)

                if transaction:
                    # Update the transaction
                    transaction.amount = transaction_amount
                    transaction.description = request_data['description']
                    db.session.add(transaction)
                    db.session.commit()
                    response = {
                        'message': 'Transaction Created',
                        'transaction_id': new_transaction.id,
                    }
                    status = 200
                else:
                    response = {'message': 'Transaction does not exist.'}
                    status = 400
            else:
                response = {'message': 'User does not exist.'}
                status = 400
        except Exception as e:
            print(e)
            response = {'message': 'Internal server error.'}
            status = 500

        return make_response(jsonify(response), status)

    def delete(self, transaction_id):
        request_data = get_parser.parse_args()
        print(request_data)

        try:
            token = jwt.decode(
                request_data['X-Auth'],
                current_app.config['SECRET_KEY'],
                algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError as e:
            print(e)
            response = {'message': 'Token expired. Please login.'}
            status = 400
            return make_response(jsonify(response), status)
        except Exception as e:
            print(e)
            response = {'message': 'Internal server error.'}
            status = 500
            return make_response(jsonify(response), status)

        # Check that the user exists if not send an error
        try:
            db_user = User.query.filter_by(id=token['sub']).first()
            if db_user:
                # Make sure the transaction you're updating exists and is assigned to the user
                old_transaction = Transaction.query.filter(Transaction.user_id == token['sub'], Transaction.id == transaction_id).first()
                print(old_transaction)

                #  If the transaction exists delete it
                if old_transaction:
                    db.session.delete(old_transaction)
                    db.session.commit()
                    response = {
                        'message': 'Transaction Deleted'
                    }
                    status = 200
                else:
                    response = {'message': 'Transaction does not exist.'}
                    status = 400
            else:
                response = {'message': 'User does not exist.'}
                status = 400
        except Exception as e:
            print(e)
            response = {'message': 'Internal server error.'}
            status = 500

        return make_response(jsonify(response), status)

class TransactionResource(Resource):
    def post(self):
        # Get the request data e.g. amount, description
        request_data = create_parser.parse_args()
        print(request_data)

        if request_data['transactionType'].lower() == 'debit':
            transaction_amount = -float(request_data['amount'])
        elif request_data['transactionType'].lower() == 'credit':
            transaction_amount = float(request_data['amount'])
        else: 
            response = {'message': 'Transaction Type must be credit or debit'}
            status = 400
            return make_response(jsonify(response), status)

        try:
            token = jwt.decode(
                request_data['X-Auth'],
                current_app.config['SECRET_KEY'],
                algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError as e:
            print(e)
            response = {'message': 'Token expired. Please login.'}
            status = 400
            return make_response(jsonify(response), status)
        except Exception as e:
            print(e)
            response = {'message': 'Internal server error.'}
            status = 500
            return make_response(jsonify(response), status)

        # Check that the user exists if not send an error
        try:
            db_user = User.query.filter_by(id=token['sub']).first()
            if db_user:
                # Create a new transaction
                new_transaction = Transaction(
                    token['sub'], 
                    transaction_amount, 
                    request_data['description']
                )
                db.session.add(new_transaction)
                db.session.commit()
                response = {
                    'message': 'Transaction Created',
                    'transaction_id': new_transaction.id,
                }
                # Send success 200 response
                status = 200
            else:
                response = {'message': 'User does not exist.'}
                status = 400
        except Exception as e:
            print(e)
            response = {'message': 'Internal server error.'}
            status = 500

        return make_response(jsonify(response), status)

    def get(self):
        request_data = get_parser.parse_args()
        print(request_data)

        try:
            token = jwt.decode(
                request_data['X-Auth'],
                current_app.config['SECRET_KEY'],
                algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError as e:
            print(e)
            response = {'message': 'Token expired. Please login.'}
            status = 400
            return make_response(jsonify(response), status)
        except Exception as e:
            print(e)
            response = {'message': 'Internal server error.'}
            status = 500
            return make_response(jsonify(response), status)

        try:
            # Get all transactions
            db_transactions = Transaction.query.filter(Transaction.user_id == token['sub']).order_by(Transaction.created_date.desc()).all()
            print(db_transactions)
        except Exception as e:
            print(e)
            response = {'message': 'Internal server error.'}
            status = 500
            return make_response(jsonify(response), status)

        total = 0.0
        response_trans = []
        for tran in db_transactions:
            response_trans.append(
                tran.as_dict()
            )
            total += tran.amount
        print(response_trans)

        response = {
            'transactions': response_trans,
            'total': format(total, '.2f')
        }
        status = 200

        return make_response(jsonify(response), status)
