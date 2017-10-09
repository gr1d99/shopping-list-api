# -*- coding: utf-8 -*-

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from web_app.conf import app_config

app = Flask(__name__)
app.config.from_object(app_config.DevelopmentConfig)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

# ---------------------------
from web_app import views
# ---------------------------


app.add_url_rule(
    '/api/v1/auth/', view_func=views.UserRegisterView.as_view('api_reqister')
)

if __name__ == '__main__':
    app.run()
