# -*- coding: utf-8 -*-

"""
Contains application main instances and configurations.
"""

from flask import Flask, redirect
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from app.conf import app_config, settings

APP = Flask(__name__)
bcrypt = Bcrypt(APP)
APP.config.from_object(app_config.DevelopmentConfig)
DB = SQLAlchemy(APP)
API = Api(APP, prefix="/api/v1.0/")
JWT = JWTManager(APP)

from app.auth import security
from app.auth.urls import auth_blueprint
from app.shoppinglist.urls import SHOPPINGLIST


APP.register_blueprint(auth_blueprint)
APP.register_blueprint(SHOPPINGLIST)


@APP.route('/')
def index():
    return redirect('https://app.swaggerhub.com/apis/gr1d99/shoppinglist-api/1.0')


if __name__ == '__main__':
    APP.run(threaded=True)
