# -*- coding: utf-8 -*-


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from shopping_list import config
from shopping_list.app.urls import urlpatterns

app = Flask(__name__)
app.config.from_object(config.DevelopmentConfig)
db = SQLAlchemy(app)

for url in urlpatterns:
    app.add_url_rule(url[0], view_func=url[1])

if __name__ == '__main__':
    app.run()
