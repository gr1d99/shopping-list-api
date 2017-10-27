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

login_args = OrderedDict(
    [
        ('username', fields.Str(required=True)),
        ('password', fields.Str(required=True))
    ]
)
