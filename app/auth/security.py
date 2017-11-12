# -*- coding: utf-8 -*-
"""
App module with function for checking it token has been blacklisted.
"""

from app import jwt
from ..models import BlacklistToken


@jwt.token_in_blacklist_loader
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
