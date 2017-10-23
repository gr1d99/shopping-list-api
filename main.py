# -*- coding: utf-8 -*-

"""
Contains application main instances and configurations.
"""

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from app.conf import app_config

APP = Flask(__name__)
BCRYPT = Bcrypt(APP)
APP.config.from_object(app_config.DevelopmentConfig)
DB = SQLAlchemy(APP)
AUTH = HTTPBasicAuth()
API = Api(APP, prefix="/api/v1/")

from app import views


API.add_resource(views.UserRegisterApi, 'auth/register')
API.add_resource(views.UserLoginApi, 'auth/login')
API.add_resource(views.UserLogoutApi, 'auth/logout')
API.add_resource(views.AuthApi, 'auth')

if __name__ == '__main__':
    APP.run()
