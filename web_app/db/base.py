# -*- coding: utf-8 -*-
"""
    This module contains all Manager classes used by;
        `User Model`
"""
from main import bcrypt


class BaseUserManager(object):
    """
    Manager classes are helpful in this web app.
    Methods and attributes defined in this class include.
        - hash_password
        - normalize_email
        - _verify_password
    """
    @classmethod
    def hash_password(cls, raw_password):
        """
        never store passwords in plaintext, this method
        hashes the raw password and returns hashed password.
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
        used to verify user password using the provided raw_password
        since password stored are hashed.
        """
        return bcrypt.check_password_hash(self.password, raw_password)
