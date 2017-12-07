# -*- coding: utf-8 -*-
"""
Application module with helper functions that handle authentication and authorization.
"""

import secrets
from app import JWT
from ..models import BlacklistToken, ResetToken, User


@JWT.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    """
    Checks if token is stored in blacklist model.

    :param decrypted_token: auth token.
    :return: True|False
    """

    jti = decrypted_token['jti']
    token = BlacklistToken.query.filter_by(token=jti).first()

    if token:
        return True

    else:
        return False


def generate_token(user_id):
    """
    generates password reset tokens.

    :param user_id: id
    :return: string
    """
    token = secrets.token_urlsafe(20)
    reset_token = ResetToken(user_id, token)
    reset_token.save()
    return token


def check_user(username):
    """
    Check if username provided is associated to any user in the application.

    :param username: user username
    :return: user object
    """
    user = User.get_by_username(username)
    return user
