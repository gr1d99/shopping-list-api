# -*- coding: utf-8 -*-

"""
User authentication endpoints definitions.
"""

from flask import Blueprint

from app import API

auth_blueprint = Blueprint('auth', __name__)

from .views import (PasswordResetTokenApi, PasswordResetApi, UserRegisterApi,
                    UserLoginApi, UserLogoutApi, UserProfileApi)

API.add_resource(UserProfileApi, 'auth/users', endpoint="user_detail")
API.add_resource(UserRegisterApi, 'auth/register', endpoint="user_register")
API.add_resource(UserLoginApi, 'auth/login', endpoint="user_login")
API.add_resource(UserLogoutApi, 'auth/logout', endpoint="user_logout")
API.add_resource(PasswordResetTokenApi, 'auth/reset-password', endpoint="password_token")
API.add_resource(PasswordResetApi, 'auth/reset-password/process', endpoint="password_reset")
