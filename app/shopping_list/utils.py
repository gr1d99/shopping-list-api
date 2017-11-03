import collections

from flask import jsonify, make_response
from webargs import fields, validate

from ..messages import invalid_limit, invalid_page, negative_limit, negative_page

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

pagination_args = collections.OrderedDict(
    [
        ('page', fields.Int(required=False)),
        ('limit', fields.Int(required=False))
    ]
)

search_args = collections.OrderedDict(
    [
        ('q', fields.Str(required=True, location='querystring')),
        ('page', fields.Int(required=False, location='querystring')),
        ('limit', fields.Int(required=False, location='querystring')),
    ]
)


class MakePaginationUrls(object):
    def __init__(self, request, page, limit):
        self.request = request
        self.page = page
        self.limit = limit

    def make_url(self):
        _url = "%(base)s?page=%(page)s&limit=%(limit)s"

        url = _url % dict(base=self.request.base_url,
                          page=self.page,
                          limit=self.limit)

        return url


def prep_keyword(keyword):
    operator = '%'
    _term = '%(op)s%(kw)s%(op)s'
    term = _term % dict(op=operator, kw=keyword)
    return term

urlmaker = MakePaginationUrls
