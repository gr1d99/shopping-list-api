# -*- coding: utf-8 -*-

"""
This module provides argument parsers for authentication endpoint urls
providing a clean way to validate arguments sent to endpoints.
"""

from collections import OrderedDict

from webargs import fields, validate


registration_args = OrderedDict(
    [
        ('username', fields.Str(location='form', required=True,
                                validate=validate.Length(min=3))),
        ('email', fields.Str(location='form', message='Email required',
                             required=True, validate=validate.Email())),
        ('password', fields.Str(location='form', required=True,
                                validate=validate.Length(min=8))),
        ('confirm', fields.Str(location='form', required=True,
                               validate=validate.Length(min=8)))
    ]
)

login_args = OrderedDict(
    [
        ('username', fields.Str(location='form', required=True)),
        ('password', fields.Str(location='form', required=True,
                                validate=validate.Length(min=6))),
    ]
)

update_args = OrderedDict(
    [
        ('username', fields.Str(location='form', required=False,
                                validate=validate.Length(min=3))),
    ]
)

get_password_token_args = OrderedDict(
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

