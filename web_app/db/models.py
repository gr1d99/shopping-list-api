# -*- coding: utf-8 -*-
"""
    all app models are defined in this module.
        models:
            1. `User`
"""

from main import db


class User(db.Model):
    ___tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username
