# -*- coding: utf-8 -*-

"""
This module contains base class and base managers for
app models.

BaseModel contains methods that are used by all models.
BaseUserManager contains methods that are specific to only
User model.

"""

from app import BCRYPT, DB
from app.core.exceptions import EmailExists, UsernameExists


class BaseModel(DB.Model):
    """
    Base class for all models.
    Contains common methods used by all models.
    """
    __abstract__ = True

    # ----Attach custom exceptions to class----- #
    #       we will never have to import
    #        these exceptions to where
    #      User class has been imported
    UsernameExists = UsernameExists
    EmailExists = EmailExists
    # ------------------------------------------- #

    def delete(self):
        """Remove instance from the database."""
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
    """Manager class for User model."""

    def authenticate(self):
        """Method to authenticate user."""
        self.authenticated = True
        self.save()
        return True

    def deauthenticate(self):
        """Set is_authenticated column to false."""
        self.authenticated = False
        self.save()
        return True

    @property
    def is_authenticated(self):
        """A property to indicate whether the user is authenticated or not."""

        return self.authenticated

    @classmethod
    def hash_password(cls, raw_password):
        """
        Never store passwords in plaintext.

        This method hashes the raw password and returns hashed password.
        """

        return BCRYPT.generate_password_hash(raw_password)

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

        return BCRYPT.check_password_hash(self.password, raw_password)

    def validate_required(self):
        """
        A method to inspect required columns.

        Passing an empty string passes non-nullable flag,
        this method helps handle that flaw.
        Field names are included in the error message to
        assist in debugging.
        """
        error_message = '%(col)s is required'
        errors = {}
        for col in self.REQUIRED_COLUMNS:
            if getattr(self, col) == '':
                errors.update({col: error_message % dict(col=col)})

        if errors == {}:
            return None

        else:
            return errors

    def verify_password(self, password):
        """Outer method that verifies stored hashed password and returns either True or False."""

        return self._verify_password(password)

    # bcrypt saves us the work of checking password column.
    # we only need to add critical columns to REQUIRED_COLUMNS.

    # NB. This allows addition of other colums which appear in the Model.
    # passing a column which does not exist will raise AttributeError.
    REQUIRED_COLUMNS = ['username', 'email']
