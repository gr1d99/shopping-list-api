# -*- coding: utf-8 -*-

"""
Contains authentication resource endpoints argument parsers.
"""

from collections import OrderedDict

from webargs import fields, validate

auth_args = {
    'username': fields.Str(required=True)
}

registration_args = OrderedDict(
    [
        ('username', fields.Str(required=True)),
        ('email', fields.Str(message='Email required', required=True, validate=validate.Email())),
        ('password', fields.Str(required=True, validate=validate.Length(min=6)))
    ]
)

update_account_args = OrderedDict(
    [
        ('username', fields.Str(required=False)),
        ('email', fields.Str(required=False, validate=validate.Email())),
    ]
)

login_args = OrderedDict(
    [
        ('username', fields.Str(required=True)),
        ('password', fields.Str(required=True))
    ]
)

reset_password_args = OrderedDict(
    [
        ('username', fields.Str(required=False)),
        ('email', fields.Str(required=False, validate=validate.Email())),
        ('old_password', fields.Str(required=True, validate=validate.Length(min=6))),
        ('new_password', fields.Str(required=True, validate=validate.Length(min=6))),
        ('confirm', fields.Str(required=True, validate=validate.Length(min=6)))
    ]
)
