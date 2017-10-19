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


class User(BaseUserManager, BaseModel,  db.Model):

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.Binary(200), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    shopping_lists = db.relationship('ShoppingList', backref='user',
                                     lazy='dynamic', cascade='all, delete-orphan')
    authenticated = db.Column(db.Boolean, default=False)
    date_joined = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, username, password, email, authenticated=False, date_joined=None):
        self.username = username
        self.password = self.hash_password(password)
        self.email = self.normalize_email(email)
        self.authenticated = authenticated
        self.date_joined = date_joined

    def check_email(self):
        if db.session.query(self).filter_by(email=self.email).first():
            raise User.EmailExists

    def check_username(self):
        if db.session.query(User).filter_by(username=self.username).first():
            raise User.UsernameExists

    def save(self):
        """Override the default save method to enable inspection of required fields"""
        # if None is returned, continue and save data
        if self.validate_required() is None:
            return self._save()

        else:
            # throw error message and do not save data
            return self.validate_required()

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
