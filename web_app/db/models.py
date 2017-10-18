# -*- coding: utf-8 -*-
"""
    all app models are defined in this module.
        models:
            1. `User`
            2. `ShoppingList`
            3. `ShoppingItem`
"""
from main import db
from web_app.utils.date_helpers import datetime
from web_app.utils.callables import CallableFalse, CallableTrue
from .base import BaseUserManager, BaseModel


class User(BaseUserManager, BaseModel,  db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    shopping_lists = db.relationship('ShoppingList', backref='user',
                                     lazy='dynamic', cascade='all, delete-orphan')
    is_authenticated = db.Column(db.Boolean, default=CallableFalse)
    date_joined = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, username, password, email, date_joined=None):
        self.username = username
        self.password = self.hash_password(password)
        self.email = self.normalize_email(email)
        self.date_joined = date_joined

    def authenticate(self):
        self.is_authenticated = CallableTrue
        self.save()
        return CallableTrue

    def deauthenticate(self):
        self.is_authenticated = CallableFalse
        self.save()
        return CallableTrue

    def verify_password(self, password):
        return self._verify_password(password)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return None

    def __repr__(self):
        return '<User %r>' % self.username


class ShoppingList(BaseModel, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    shopping_items = db.relationship('ShoppingItem', backref='shopping_list',
                                     lazy='dynamic', cascade='all, delete-orphan')
    timestamp = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return '<%(name)s obj>' % dict(name=self.name.capitalize())


class ShoppingItem(BaseModel, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    shoppinglist_id = db.Column(db.Integer, db.ForeignKey('shopping_list.id'))
    timestamp = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return '<%(name)s obj>' % dict(name=self.name.capitalize())
