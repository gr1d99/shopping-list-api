import collections

from webargs import fields, validate

shoppinglist_args = collections.OrderedDict(
    [
        ('name', fields.Str(required=True, validate=validate.Length(min=3)))
    ]
)

shoppinglist_update_args = collections.OrderedDict(
    [
        ('new_name', fields.Str(required=False)),
        ('is_active', fields.Bool(required=False))
    ]
)

shoppingitem_create_args = collections.OrderedDict(
    [
        ('name', fields.Str(required=True, validate=validate.Length(min=3))),
        ('price', fields.Decimal(required=True)),
        ('bought', fields.Bool(required=False))
    ]
)

shoppingitem_update_args = collections.OrderedDict(
    [
        ('name', fields.Str(required=False)),
        ('price', fields.Decimal(required=False)),
        ('bought', fields.Bool(required=False))
    ]
)