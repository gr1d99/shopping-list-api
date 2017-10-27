import collections

from webargs import fields, validate

shopping_list_args = collections.OrderedDict(
    [
        ('name', fields.Str(required=True, validate=validate.Length(min=5)))
    ]
)
