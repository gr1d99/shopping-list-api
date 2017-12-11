# -*- coding: utf-8 -*-
"""
    all app models are defined in this module.
        models:
            1. `User`
            2. `ShoppingList`
            3. `ShoppingItem`
"""

import pytz
from datetime import datetime

from app import DB
from app.conf.settings import TIME_ZONE
from .core.exceptions import UsernameExists, EmailExists
from .db.base import BaseUserManager, BaseModel


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
    reset_tokens = DB.relationship('ResetToken', backref='user',
                                    lazy='dynamic', cascade='all, delete-orphan')
    date_joined = DB.Column(DB.DateTime(timezone=True),
                            default=datetime.now(tz=pytz.timezone(TIME_ZONE)).now)


    def __init__(self, username, password, email):
        """Initialize model values."""
        self.username = username
        self.password = self.hash_password(password)
        self.email = self.normalize_email(email)

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
    def get_by_username(username):
        """
        Gets user instance using provided username.

        :param username: user username.
        :return: instance.
        """

        return DB.session.query(User).filter_by(username=username).first()

    @staticmethod
    def get_by_email(email):
        """
        Gets user instance using provided email.

        :param email: user email.
        :return: instance.
        """

        return DB.session.query(User).filter_by(email=email).first()

    def __repr__(self):
        return '<%(username)s obj>' % dict(username=self.username.capitalize())


class BlacklistToken(BaseModel, DB.Model):
    """
    Token model for storing JWT tokens
    """
    id = DB.Column(DB.Integer, primary_key=True)
    token = DB.Column(DB.String(500), unique=True, nullable=False)

    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return '<id: token: {}'.format(self.token)


class ShoppingList(BaseModel, DB.Model):
    """Model used to store user shopping lists"""

    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(100), nullable=False)
    owner_id = DB.Column(DB.Integer, DB.ForeignKey('users.id'))
    shopping_items = DB.relationship('ShoppingItem', backref='shopping_list',
                                     lazy='dynamic', cascade='all, delete-orphan')
    description = DB.Column(DB.Text(), nullable=True, default="")


    @staticmethod
    def get(shoppinglistId, ownerId):
        """
        Method to get shoppinglist instance by its id and its owner id to
        ensure other users dont query instances that dont belong to them.

        :param shoppinglistId: shopping list id.
        :param ownerId: user id.
        :return: instance.
        """
        instance = DB.session.query(ShoppingList).filter_by(id=shoppinglistId,
                                                            owner_id=ownerId).first()
        return instance

    def cost(self):
        """
        Calculates total amount(item price * quantity).
        :return: calculated price.
        """

        return sum([item.price for item in
                    DB.session.query(self.__class__).
                   filter_by(id=self.id).first().
                   shopping_items.all()])

    def __repr__(self):
        return '<%(name)s obj>' % dict(name=self.name.capitalize())


class ShoppingItem(BaseModel, DB.Model):
    """Model used to store Shopping List items"""

    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(100), nullable=False)
    quantity_description = DB.Column(DB.String(200), nullable=False)
    price = DB.Column(DB.Float, nullable=False)
    bought = DB.Column(DB.Boolean, default=False)
    shoppinglist_id = DB.Column(DB.Integer, DB.ForeignKey('shopping_list.id'))

    def __repr__(self):
        return '<%(name)s obj>' % dict(name=self.name.capitalize())


class ResetToken(BaseModel, DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    token = DB.Column(DB.String(50), nullable=False)
    user_id = DB.Column(DB.Integer, DB.ForeignKey('users.id'))
    expired = DB.Column(DB.Boolean, default=False)

    def __init__(self, user_id, token):
        self.user_id = user_id
        self.token = token

    def expire_token(self):
        self.expired = True
        self.save()

    @property
    def is_expired(self):
        return self.expired

    @staticmethod
    def get_instance(token, user_id):
        instance = DB.session.query(ResetToken).filter_by(token=token, user_id=user_id).first()
        return instance
