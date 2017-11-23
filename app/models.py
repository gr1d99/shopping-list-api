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
    date_joined = DB.Column(DB.DateTime(timezone=True),
                            default=datetime.now(tz=pytz.timezone(TIME_ZONE)).now)
    timestamp = DB.Column(DB.DateTime(timezone=True),
                          default=datetime.now(tz=pytz.timezone(TIME_ZONE)).now)
    updated = DB.Column(DB.DateTime(timezone=True),
                        default=datetime.now(tz=pytz.timezone(TIME_ZONE)).now,
                        onupdate=datetime.now(tz=pytz.timezone(TIME_ZONE)).now)

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
    timestamp = DB.Column(DB.DateTime(timezone=True),
                          default=datetime.now(tz=pytz.timezone(TIME_ZONE)).now)
    updated = DB.Column(DB.DateTime(timezone=True),
                        default=datetime.now(tz=pytz.timezone(TIME_ZONE)).now,
                        onupdate=datetime.now(tz=pytz.timezone(TIME_ZONE)).now)

    def __init__(self, token):
        self.token = token

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
    description = DB.Column(DB.Text(), nullable=True, default="")
    timestamp = DB.Column(DB.DateTime(timezone=True),
                          default=datetime.now(tz=pytz.timezone(TIME_ZONE)).now)
    updated = DB.Column(DB.DateTime(timezone=True),
                        default=datetime.now(tz=pytz.timezone(TIME_ZONE)).now,
                        onupdate=datetime.now(tz=pytz.timezone(TIME_ZONE)).now)

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

    def __repr__(self):
        return '<%(name)s obj>' % dict(name=self.name.capitalize())


class ShoppingItem(BaseModel, DB.Model):
    """Model used to store Shopping List items"""

    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(100), nullable=False)
    quantity = DB.Column(DB.Float(precision=2), nullable=False)
    price = DB.Column(DB.Float, nullable=False)
    bought = DB.Column(DB.Boolean, default=False)
    shoppinglist_id = DB.Column(DB.Integer, DB.ForeignKey('shopping_list.id'))
    timestamp = DB.Column(DB.DateTime(timezone=True),
                          default=datetime.now(tz=pytz.timezone(TIME_ZONE)).now)
    updated = DB.Column(DB.DateTime(timezone=True),
                        default=datetime.now(tz=pytz.timezone(TIME_ZONE)).now,
                        onupdate=datetime.now(tz=pytz.timezone(TIME_ZONE)).now)

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

    def total_amount(self):
        """
        Calculates total amount(item price * quantity).
        :return: calculated price.
        """

        return self.price * self.quantity

    def __repr__(self):
        return '<%(name)s obj>' % dict(name=self.name.capitalize())


class ResetToken(BaseModel, DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    user_id = DB.Column(DB.Integer, DB.ForeignKey('users.id'))
    token = DB.Column(DB.String(50), nullable=False)
    expired = DB.Column(DB.Boolean, default=False)
    timestamp = DB.Column(DB.DateTime(timezone=True),
                          default=datetime.now(tz=pytz.timezone(TIME_ZONE)).now)
    updated = DB.Column(DB.DateTime(timezone=True),
                        default=datetime.now(tz=pytz.timezone(TIME_ZONE)).now,
                        onupdate=datetime.now(tz=pytz.timezone(TIME_ZONE)).now)

    def expire_token(self):
        self.token = True
        self.save()

    @property
    def is_expired(self):
        return self.expired
