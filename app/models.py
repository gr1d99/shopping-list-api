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

    @staticmethod
    def get_user(username):
        """
        Gets user instance using provided username.

        :param username: user username.
        :return: instance.
        """

        return DB.session.query(User).filter_by(username=username).first()

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
    is_active = DB.Column(DB.Boolean, default=True)
    timestamp = DB.Column(DB.DateTime, default=DB.func.current_timestamp())
    updated = DB.Column(
        DB.DateTime, default=DB.func.current_timestamp(),
        onupdate=DB.func.current_timestamp())

    @staticmethod
    def get(shoppinglistId, ownerId):
        """
        Method to get shoppinglist instance by its id and its owner id to
        ensure other users dont query instances that dont belong to them.

        :param shoppinglistId: shopping list id.
        :param ownerId: user id.
        :return: instance.
        """
        instance = DB.session.query(ShoppingList).filter_by(id=shoppinglistId, owner_id=ownerId).first()
        return instance

    def __repr__(self):
        return '<%(name)s obj>' % dict(name=self.name.capitalize())


class ShoppingItem(BaseModel, DB.Model):
    """Model used to store Shopping List items"""

    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(100), nullable=False)
    price = DB.Column(DB.Float, nullable=False)
    bought = DB.Column(DB.Boolean, default=False)
    shoppinglist_id = DB.Column(DB.Integer, DB.ForeignKey('shopping_list.id'))
    timestamp = DB.Column(DB.DateTime, default=DB.func.current_timestamp())
    updated = DB.Column(
        DB.DateTime, default=DB.func.current_timestamp(),
        onupdate=DB.func.current_timestamp())

    @staticmethod
    def exists(shl_id, name):
        """
        Method to check if shopping item with a given name exists in a given shoppinglist.

        Different shoppinglists may have similar item names but one single shoppinglist
        may not have more than one item with similar names.
        .
        :param shl_id: shopping list id.
        :param name: shopping item name.
        :return: Bool
        """

        # get the specified shoppinglist.
        shoppinglist = DB.session.query(ShoppingList).filter_by(id=shl_id).first()

        # filter out items by their names.
        shoppingitem = shoppinglist.shopping_items.filter_by(name=name).first()

        if shoppingitem is None:
            return False

        return True

    def __repr__(self):
        return '<%(name)s obj>' % dict(name=self.name.capitalize())
