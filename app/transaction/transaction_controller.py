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
            'amount': self.amount,
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

class TransactionResource(Resource):
    def post(self):
        # Get the request data e.g. amount, description
        request_data = create_parser.parse_args()
        print(request_data)

        if request_data['transactionType'].lower() == 'debit':
            tansaction_amount = -float(request_data['amount'])
        elif request_data['transactionType'].lower() == 'credit':
            tansaction_amount = float(request_data['amount'])
        else: 
            response = {'message': 'Transaction Type must be credit or debit'}
            status = 400
            return make_response(jsonify(response), status)

        token = jwt.decode(
            request_data['X-Auth'],
            current_app.config['SECRET_KEY'],
            algorithms=["HS256"]
        )
        # Check that the user exists if not send an error
        db_user = User.query.filter_by(id=token['sub']).first()
        if db_user:
            try:
                # Create a new transaction
                new_transaction = Transaction(
                    token['sub'], 
                    tansaction_amount, 
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
            except Exception as e:
                print(e)
                response = {'message': 'Internal server error.'}
                status = 500
        else:
            response = {'message': 'User does not exist.'}
            status = 400

        return make_response(jsonify(response), status)

    # @TODO: implement error handling
    def get(self):
        request_data = get_parser.parse_args()
        print(request_data)

        token = jwt.decode(
            request_data['X-Auth'],
            current_app.config['SECRET_KEY'],
            algorithms=["HS256"]
        )

        db_transactions = Transaction.query.filter(Transaction.user_id == token['sub']).all()
        print(db_transactions)

        response_trans = []
        for tran in db_transactions:
            response_trans.append(
                tran.as_dict()
            )
        print(response_trans)

        response = {
            'transactions': response_trans,
        }
        status = 200

        return make_response(jsonify(response), status)
