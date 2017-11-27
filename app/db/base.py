# -*- coding: utf-8 -*-

"""
This module contains base class and base managers for
app models.

BaseModel contains methods that are used by all models.
BaseUserManager contains methods that are specific to only
User model.

"""
import pytz
from datetime import datetime

from app import bcrypt, DB
from app.conf.settings import TIME_ZONE
from app.core.exceptions import EmailExists, UsernameExists


class BaseModel(DB.Model):
    """
    Base class for all models.
    Contains common methods used by all models.
    """
    __abstract__ = True

    # ----Attach custom exceptions to class----- #
    #       we will never have to import
    #       these exceptions to where
    #       User class has been imported
    #
    #     Example:
    #     try:
    #         ...
    #     Except User.UsernameExists:
    #         ...
    #         do something
    #         ...

    UsernameExists = UsernameExists
    EmailExists = EmailExists
    # ------------------------------------------- #

    def delete(self):
        """
        Remove instance from the database.
        """

        DB.session.delete(self)
        DB.session.commit()
        return None

    def save(self):
        """
        Calls protected method to populate the database with data.

        """

        return self._save()

    def _save(self):
        DB.session.add(self)
        DB.session.commit()


class BaseUserManager(object):
    """
    Manager class for User model.
    """

    @classmethod
    def hash_password(cls, raw_password):
        """
        Never store passwords in plaintext.

        This method hashes the raw password and returns hashed password.
        """

        return bcrypt.generate_password_hash(raw_password)

    @classmethod
    def normalize_email(cls, email):
        """
        Normalize the email address by lowercasing the domain part of it.
        """

        email = email or ''

        try:
            email_name, domain_part = email.strip().rsplit('@', 1)

        except ValueError:
            pass

        else:
            email = '@'.join([email_name, domain_part.lower()])

        return email

    def _verify_password(self, raw_password):
        """
        Used to verify user password using the provided raw_password
        since password stored are hashed.
        """

        return bcrypt.check_password_hash(self.password, raw_password)

    def verify_password(self, password):
        """Outer method that verifies stored hashed password and returns either True or False."""

        return self._verify_password(password)
