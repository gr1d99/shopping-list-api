# -*- coding: utf-8 -*-

"""
Contains application main instances and configurations.
"""

from flask import Blueprint, Flask
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from app.conf import app_config

APP = Flask(__name__)
BCRYPT = Bcrypt(APP)
APP.config.from_object(app_config.DevelopmentConfig)
DB = SQLAlchemy(APP)
AUTH = HTTPBasicAuth()
API = Api(APP, prefix="/api/v1/")
jwt = JWTManager(APP)

from .models import BlacklistToken

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    token = BlacklistToken.query.filter_by(token=jti).first()
    if token:
        return True

    else:
        return False

from app.auth.urls import urls

for url in urls:
    API.add_resource(url.resource, url.route)

if __name__ == '__main__':
    APP.run()
