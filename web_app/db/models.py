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
from .base import BaseUserManager, BaseModel


class User(BaseUserManager, BaseModel, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    shopping_lists = db.relationship('ShoppingList', backref='user',
                                     lazy=True, cascade='all, delete-orphan')
    date_joined = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, username, password, email, date_joined=None):
        self.username = username
        self.password = self.hash_password(password)
        self.email = self.normalize_email(email)
        self.date_joined = date_joined

    def verify_password(self, password):
        return self._verify_password(password)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return None

    def save(self):
        """
        using save() is a cleaner way.
        saves user object to db
        """
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return '<User %r>' % self.username


class ShoppingList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    shopping_items = db.relationship('ShoppingItem', backref='shopping_list',
                                     lazy=True, cascade='all, delete-orphan')
    timestamp = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return '<%(name) obj>' % dict(name=self.name.capitalize())


class ShoppingItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    shoppinglist_id = db.Column(db.Integer, db.ForeignKey('shopping_list.id'))
    timestamp = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return '<%(name) obj>' % dict(name=self.name.capitalize())
