"""
app/transaction/__init__.py
- creates an api instance and adds routes
- '/transaction': ['POST', 'GET']
- '/transaction/<int:id>': ['GET', 'UPDATE', 'DELETE']
"""

from flask_restful import Api

from app.common.config.custom_errors import errors
from app.transaction.transaction_controller import TransactionResource#, TransactionIdResource

api = Api(prefix='/api/v1/', errors=errors, catch_all_404s=True)

api.add_resource(TransactionResource, '/transaction')
# api.add_resource(TransactionIdResource, '/transaction/<transaction_id>')
