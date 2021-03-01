"""
app/login/__init__.py
- creates an api instance and adds routes
- '/user/<int:id>': ['GET']
"""

from flask_restful import Api

from app.common.config.custom_errors import errors
from app.login.login_controller import UserResource, RegisterResource, LoginResource

api = Api(errors=errors, catch_all_404s=True)

api.add_resource(UserResource, '/users/<user_id>')
api.add_resource(RegisterResource, '/register')
api.add_resource(LoginResource, '/login')
