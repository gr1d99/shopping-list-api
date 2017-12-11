# -*- coding: utf-8 -*-

"""
This module define helper argument parsers and classes.

The helper argument parsers check and validate arguments
passed in the endpoint url. If the argument provided in the
url does not pass the parsing stage then the request terminated
and a response of status code 422 is returned back to the client.
"""

import collections

from webargs import fields, validate

__all__ = [
    'detail_args', 'pagination_args', 'prep_keyword',
    'item_update_args', 'search_args', 'item_create_args',
    'create_args', 'update_args', 'urlmaker'
]

create_args = collections.OrderedDict(
    [
        ('name', fields.Str(required=True,
                            validate=validate.Length(min=3),
                            location='form')),
        ('description', fields.Str(required=False,
                                   location='form'))
    ]
)

update_args = collections.OrderedDict(
    [
        ('name', fields.Str(required=False, location='form')),
        ('description', fields.Str(required=False, location='form'))
    ]
)

item_create_args = collections.OrderedDict(
    [
        ('name', fields.Str(required=True, validate=validate.Length(min=3))),
        ('price', fields.Decimal(required=True)),
        ('quantity_description', fields.Str(required=True)),
    ]
)

item_update_args = collections.OrderedDict(
    [
        ('name', fields.Str(required=False)),
        ('price', fields.Decimal(required=False)),
        ('quantity_description', fields.Str(required=False)),
        ('bought', fields.Str(required=False))
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

detail_args = collections.OrderedDict(
    [
        ('id', fields.Int(required=True, location='query'))
    ]
)


class MakePaginationUrls(object):
    """
    Generates previous page or next page urls.
    """

    def __init__(self, request, page, limit):
        self.request = request
        self.page = page
        self.limit = limit

    def make_url(self):
        """
        Method to generate pagination urls.

        :return: url.
        """

        _url = "%(base)s?page=%(page)s&limit=%(limit)s"

        url = _url % dict(base=self.request.base_url,
                          page=self.page,
                          limit=self.limit)

        return url


def prep_keyword(keyword):
    """
    prepares keywords used for search.
    :param keyword: raw text.
    :return: formatted text.
    """

    operator = '%'
    _term = '%(op)s%(kw)s%(op)s'
    term = _term % dict(op=operator, kw=keyword)
    return term


urlmaker = MakePaginationUrls
