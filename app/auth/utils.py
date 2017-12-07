# -*- coding: utf-8 -*-

"""
This module implements argument parsers for authentication endpoint urls
providing a clean way to validate arguments included in urls.
"""

from collections import OrderedDict

from webargs import fields, validate

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
