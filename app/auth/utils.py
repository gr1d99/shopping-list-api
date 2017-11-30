# -*- coding: utf-8 -*-

"""
Contains authentication resource endpoints argument parsers.
"""

from collections import OrderedDict

from flask_mail import Message
from webargs import fields, validate

from app import mail, celery
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

update_account_args = OrderedDict(
    [
        ('email', fields.Str(location='form', required=False, validate=validate.Email())),
    ]
)

request_reset_token_args = OrderedDict(
    [
        ('email', fields.Str(required=True, location='query', validate=validate.Email()))
    ]
)

reset_password_args = OrderedDict(
    [
        ('username', fields.Str(location='form', required=True)),
        ('new_password', fields.Str(location='form', required=True, validate=validate.Length(min=6))),
        ('confirm', fields.Str(location='form', required=True, validate=validate.Length(min=6))),
        ('reset_token', fields.Str(location='form', required=True))
    ]
)

delete_account_args = OrderedDict(
    [
        ('confirm', fields.Bool(location='query', required=False))
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