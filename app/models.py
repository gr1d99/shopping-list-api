# -*- coding: utf-8 -*-
"""
    all app models are defined in this module.
        models:
            1. `User`
            2. `ShoppingList`
            3. `ShoppingItem`
"""
import datetime as dt
import jwt

from app import APP, DB
from .core.exceptions import UsernameExists, EmailExists
from .db.base import BaseUserManager, BaseModel
from .utils.date_helpers import datetime


class User(BaseUserManager, BaseModel, DB.Model):
    """
    Model used to store app user details and also used for auth purposes.
    """

    __tablename__ = 'users'

    id = DB.Column(DB.Integer, primary_key=True, nullable=False)
    username = DB.Column(DB.String(100), unique=True, nullable=False)
    password = DB.Column(DB.Binary(200), nullable=False)
    email = DB.Column(DB.String(30), unique=True, nullable=False)
    shopping_lists = DB.relationship('ShoppingList', backref='user',
                                     lazy='dynamic', cascade='all, delete-orphan')
    authenticated = DB.Column(DB.Boolean, default=False)
    date_joined = DB.Column(DB.DateTime, default=datetime.now())

    def __init__(self, username, password, email, authenticated=False, date_joined=None):
        """Initialize model values."""
        self.username = username
        self.password = self.hash_password(password)
        self.email = self.normalize_email(email)
        self.authenticated = authenticated
        self.date_joined = date_joined

    @staticmethod
    def check_email(email):
        """
        Check if email exists and raise an exception.
        """

        if User.query.filter_by(email=email).first():
            raise EmailExists

    @staticmethod
    def check_username(username):
        """
        Check if username exists and raise an exception.
        """

        if User.query.filter_by(username=username).first():
            raise UsernameExists

    def save(self):
        """
        Override the default save method to enable inspection of required fields
        """

        # if None is returned, continue and save data
        if not self.validate_required():
            # if there are no errors just call the original save method
            return super(User, self).save()

        else:
            # throw error message and do not save data
            return self.validate_required()

    def __repr__(self):
        return '<%(username)s obj>' % dict(username=self.username.capitalize())


class BlacklistToken(BaseModel, DB.Model):
    """
    Token model for storing JWT tokens
    """
    id = DB.Column(DB.Integer, primary_key=True)
    token = DB.Column(DB.String(500), unique=True, nullable=False)
    blacklisted_on = DB.Column(DB.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = dt.datetime.utcnow()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)


class ShoppingList(BaseModel, DB.Model):
    """Model used to store user shopping lists"""

    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(100), nullable=False, unique=True)
    owner_id = DB.Column(DB.Integer, DB.ForeignKey('users.id'))
    shopping_items = DB.relationship('ShoppingItem', backref='shopping_list',
                                     lazy='dynamic', cascade='all, delete-orphan')
    timestamp = DB.Column(DB.DateTime, default=DB.func.current_timestamp())
    date_modified = DB.Column(
        DB.DateTime, default=DB.func.current_timestamp(),
        onupdate=DB.func.current_timestamp())

    def __repr__(self):
        return '<%(name)s obj>' % dict(name=self.name.capitalize())


class ShoppingItem(BaseModel, DB.Model):
    """Model used to store Shopping List items"""

    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(100), nullable=False, unique=True)
    shoppinglist_id = DB.Column(DB.Integer, DB.ForeignKey('shopping_list.id'))
    timestamp = DB.Column(DB.DateTime, default=datetime.now())

    def __repr__(self):
        return '<%(name)s obj>' % dict(name=self.name.capitalize())
