# -*- coding: utf-8 -*-

"""
Contains app shoppinglists and shoppingitems url definations.
"""

from flask import Blueprint

from app import API

from .views import \
    (ShoppingListsApi, ShoppingListDetailApi,
     ShoppingItemDetailApi, SearchShoppingListApi)

SHOPPINGLIST = Blueprint('shopping_list', __name__)

API.add_resource(
    ShoppingListsApi, 'shopping-lists', endpoint='shoppinglist_list')

API.add_resource(
    ShoppingListDetailApi, 'shopping-lists/<int:id>', endpoint='shoppinglist_detail')

API.add_resource(
    ShoppingItemDetailApi, 'shopping-lists/<int:shoppinglistId>/shopping-items',
    endpoint='shoppingitem_detail')

API.add_resource(
    ShoppingItemDetailApi, 'shopping-lists/<int:shoppinglistId>/shopping-items/<int:shoppingitemId>',
    endpoint='shoppingitem_edit')

API.add_resource(
    SearchShoppingListApi, 'shopping-lists/search', endpoint='shoppinglist_search')
