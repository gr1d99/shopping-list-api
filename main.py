# -*- coding: utf-8 -*-

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from web_app.conf import app_config

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config.from_object(app_config.TestingConfig)
db = SQLAlchemy(app)


if __name__ == '__main__':
    app.run()
