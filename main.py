# -*- coding: utf-8 -*-

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from web_app.conf import app_config

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config.from_object(app_config.DevelopmentConfig)
db = SQLAlchemy(app)
auth = HTTPBasicAuth()
api = Api(app, prefix="/api/v1/")

from web_app import views

api.add_resource(views.UserRegisterApi, 'auth/register')
api.add_resource(views.UserLoginApi, 'auth/login')
api.add_resource(views.AuthApi, 'auth/<string:username_id>', endpoint='users')

if __name__ == '__main__':
    app.run()
