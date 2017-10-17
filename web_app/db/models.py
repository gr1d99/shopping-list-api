# -*- coding: utf-8 -*-
"""
    all app models are defined in this module.
        models:
            1. `User`
            2. `ShoppingList`
            3. `ShoppingItem`
"""
import datetime
from main import db
from ..settings import TIME_ZONE
from .base import BaseUserManager


class User(BaseUserManager, db.Model):
    ___tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    shopping_lists = db.relationship('ShoppingList',
                                     backref='owner',
                                     lazy=True,
                                     cascade='all, delete-orphan')
    date_joined = db.Column(db.DateTime,
                            default=datetime.datetime.now(tz=TIME_ZONE))

    def __init__(self, username, password, email):
        self.username = username
        self.password = self.hash_password(password)
        self.email = self.normalize_email(email)

    def verify_password(self, password):
        return self._verify_password(password)

    def __repr__(self):
        return '<User %r>' % self.username


class ShoppingList(db.Model):
    __tablename__ = 'shopping_lists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'))
    shoppingitems = db.relationship('ShoppingItem', backref='shoppinglist',
                                    lazy=True,
                                    cascade='all, delete-orphan')
    timestamp = db.Column(db.DateTime,
                          default=datetime.datetime.now(tz=TIME_ZONE))

    def __repr__(self):
        return '<%(name) obj>' % dict(name=self.name.capitalize())


class ShoppingItem(db.Model):
    __tablename__ = 'shopping_item'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    shoppinglist_id = db.Column(db.Integer, db.ForeignKey('shoppinglist.id'))
    timestamp = db.Column(db.DateTime,
                          default=datetime.datetime.now(tz=TIME_ZONE))

    def __repr__(self):
        return '<%(name) obj>' % dict(name=self.name.capitalize())
