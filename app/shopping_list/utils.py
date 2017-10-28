import collections

from webargs import fields, validate

shoppinglist_args = collections.OrderedDict(
    [
        ('name', fields.Str(required=True, validate=validate.Length(min=5)))
    ]
)

shoppinglist_update_args = collections.OrderedDict(
    [
        ('new_name', fields.Str(required=False, validate=validate.Length(min=5)))
    ]
)