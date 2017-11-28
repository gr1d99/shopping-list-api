# -*- coding: utf-8 -*-
"""
App module with function for checking it token has been blacklisted.
"""

import secrets
from functools import wraps
from flask import Response, make_response, jsonify
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
    token = secrets.token_urlsafe(20)
    rt = ResetToken(user_id, token)
    rt.save()
    return token


def check_user(username):
    user = User.get_by_username(username)
    return user
