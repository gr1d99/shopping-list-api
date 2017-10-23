# -*- coding: utf-8 -*-

"""
Custom Exeption classes allows passing of additional information.
"""


class UsernameExists(Exception):
    """Raised when username already exists in the database"""


class EmailExists(Exception):
    """Raised when email already exists in the database"""
