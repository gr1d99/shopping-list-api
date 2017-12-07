# -*- coding: utf-8 -*-

"""
This module implements argument parsers for authentication endpoint urls
providing a clean way to validate arguments included in urls.
"""

from collections import OrderedDict

from webargs import fields, validate

from app import celery
from .security import generate_token

registration_args = OrderedDict(
    [
        ('username', fields.Str(location='form', required=True)),
        ('email', fields.Str(location='form', message='Email required',
                             required=True, validate=validate.Email())),
        ('password', fields.Str(location='form', required=True,
                                validate=validate.Length(min=6))),
        ('confirm', fields.Str(location='form', required=True,
                               validate=validate.Length(min=6)))
    ]
)

update_args = OrderedDict(
    [
        ('email', fields.Str(location='form', required=False,
                             validate=validate.Email())),
    ]
)

reset_args = OrderedDict(
    [
        ('username', fields.Str(location='form', required=True)),
        ('new_password', fields.Str(location='form', required=True,
                                    validate=validate.Length(min=6))),
        ('confirm', fields.Str(location='form', required=True,
                               validate=validate.Length(min=6))),
        ('reset_token', fields.Str(location='form', required=True))
    ]
)

delete_args = OrderedDict(
    [
        ('password', fields.Str(location='form', required=True))
    ]
)


@celery.task()
def send_reset_token(user_id):
    token = generate_token(user_id)
    # html_msg = """
    # <h1 align="center">Password Reset</h1>
    # <p>Hi %(user)s, this is your password reset token %(token)s</p>
    # """ % dict(user=username, token=token)
    # msg = Message('', recipients=[email, ])
    # msg.html = html_msg
    # return mail.send(msg)
    return token
