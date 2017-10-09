# -*- coding: utf-8 -*-
"""
    all app models are defined in this module.
        models:
            1. `User`
"""

from main import db
from .base import BaseUserManager


class User(BaseUserManager, db.Model):
    """A model class used to store user detail"""
    ___tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)

    def __init__(self, username, password, email):
        self.username = username
        self.password = self.hash_password(password)
        self.email = self.normalize_email(email)

    def verify_password(self, password):
        """
        provides a way to verify if the stored password
        matches with the passed `password` argument
        """
        return self._verify_password(password)

    def __repr__(self):
        return '<User %r>' % self.username
