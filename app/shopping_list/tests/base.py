"""
Contains Base classes for all shopping list and shopping item functionalities.
"""

import collections

from flask import json
from flask_restful import url_for
from flask_testing import TestCase

from app import APP, DB
from app.conf import app_config


class TestShoppingListBase(TestCase):
    """
    Base class for all test cases for ShoppingList functionality.
    """

    def __init__(self, *args, **kwargs):
        super(TestShoppingListBase, self).__init__(*args, **kwargs)

        self.content_type = 'application/json'

        # test data
        _ = collections.namedtuple('User', ['username', 'password', 'email'])
        __ = collections.namedtuple('ShoppingList', ['name', ])

        self.user = _('gideon', 'gideonpassword', 'gideon@gmail.com')
        self.user_two = _('user_two', "user_two_password", "user_two@gmail.com")
        self.shopping_list = __('testshoppinglist')
        self.shopping_list_two = __('testshoppinglisttwo')

    def create_app(self):
        """
        Creates an application instance.
        """

        return APP

    def setUp(self):
        """
        Prep app for testing.
        """

        # update app configuration to testing.
        self.app.config.from_object(app_config.TestingConfig)

        # create all models.
        DB.session.commit()
        DB.drop_all()
        DB.create_all()

    def tearDown(self):
        """
        Called after every test to remove all tables in the database.
        """

        DB.session.remove()
        DB.drop_all()

    def login_user(self):
        """
        Helper method to login client.

        Makes post request using client information initialized in
        the setUp method.
        """

        cridentials = dict(
            username=self.user.username,
            password=self.user.password)

        data = json.dumps(cridentials)
        url = url_for('user_login')
        return self.client.post(url, data=data, content_type=self.content_type)

    def login_user_two(self):
        """
        Helper method to login another client..

        Makes post request using client information initialized in
        the setUp method.
        """

        cridentials = dict(
            username=self.user_two.username,
            password=self.user_two.password)

        data = json.dumps(cridentials)
        url = url_for('user_login')

        return self.client.post(url, data=data, content_type=self.content_type)

    def register_user(self):
        """
        Helper method to register client.
        """

        user_info = dict(
            username=self.user.username,
            password=self.user.password,
            email=self.user.email)

        data = json.dumps(user_info)
        url = url_for('user_register')

        return self.client.post(url, data=data, content_type=self.content_type)

    def register_second_user(self):
        """
        Helper method to register another client.
        """

        user_info = dict(
            username=self.user_two.username,
            password=self.user_two.password,
            email=self.user_two.email)

        data = json.dumps(user_info)
        url = url_for('user_register')

        return self.client.post(url, data=data, content_type=self.content_type)

    def logout_user(self, token):
        """
        Helper method to logout client.
        """

        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token))

        url = url_for('user_logout')

        return self.client.delete(url, content_type=self.content_type, headers=headers)

    def create_shoppinglist(self, token, **data):
        """
        Method to make a post request to create shopping list.
        """

        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token))
        data = json.dumps(data)
        url = url_for('shoppinglist_list')
        return self.client.post(url, data=data, content_type=self.content_type, headers=headers)

    def get_user_shoppinglists(self, token):
        """
        Method to make get request to fetch user shopping lists.
        """

        headers = dict(Authorization='Bearer %(token)s' % dict(token=token))
        url = url_for('shoppinglist_list')

        return self.client.get(url, content_type=self.content_type, headers=headers)

    def get_user_shoppinglist_detail(self, token, id):
        """
        Method to make get request and fetch specific shopping list based on provided id.
        """

        # append shoppinglist id at the end of url.
        url = url_for('shoppinglist_detail', id=id)

        headers = dict(Authorization='Bearer %(token)s' % dict(token=token))

        return self.client.get(url, headers=headers, content_type=self.content_type)

    def update_user_shoppinglist(self, token, id, new_info):
        """
        Method to make PUT request to update user shoppinglist.
        :param token: user auth token
        :param id: shopping list id
        :param new_info: details to update
        :return: response
        """

        data = json.dumps(new_info)
        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token))
        url = url_for('shoppinglist_detail', id=id)

        return self.client.put(url, data=data, headers=headers, content_type=self.content_type)

    def delete_shoppinglist(self, token, id):
        """
        Makes a PUT request as client to delete shoppinglist.
        :param token: user auth token.
        :param id: shoppinglist id.
        :return: response from server.
        """

        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token))
        url = url_for('shoppinglist_detail', id=id)

        return self.client.delete(url, headers=headers, content_type=self.content_type)


class TestShoppingItemsBase(TestShoppingListBase):
    """
    Base class for shopping items tests.
    """
    def __init__(self, *args, **kwargs):
        super(TestShoppingItemsBase, self).__init__(*args, **kwargs)
        _testdata = collections.namedtuple('ShoppingItem', ['name', 'price', 'bought'])
        self.testdata_1 = _testdata('bread', 90.0, False)
        self.testdata_2 = _testdata('blueband', 100.5, False)

    def create_shoppingitem(self, token, shoppinglistId, data):
        """
        Makes POST request as client to create shoppingitems.
        :param token: user auth token.
        :param shoppinglistId: shoppinglist id.
        :param data: shoppingitem details
        :return: response.
        """

        data = json.dumps(data)
        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token))
        url = url_for('shoppingitem_create', shoppinglistId=shoppinglistId)

        return self.client.post(url, data=data, headers=headers, content_type=self.content_type)

    def get_shoppingitems(self, token, shoppinglistId):
        """
        Makes POST request as client to create shoppingitems.
        :param token: user auth token.
        :param shoppinglistId: shoppinglist id.
        :return: response.
        """

        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token))
        url = url_for('shoppingitem_detail', shoppinglistId=shoppinglistId)

        return self.client.get(url, headers=headers, content_type=self.content_type)

    def get_shoppingitem_detail(self, token, shoppinglistId, shoppingitemId):
        """
        Makes GET request as client to retrieve specific shoppingitem.
        :param token: user auth token.
        :param shoppinglistId: ID of shoppinglist..
        :param shoppingitemId: ID of shoppingitem.
        :return: response.
        """

        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token))
        url = url_for('shoppingitem_edit', shoppinglistId=shoppinglistId,
                      shoppingitemId=shoppingitemId)

        return self.client.get(url, headers=headers, content_type=self.content_type)

    def update_shoppingitem(self, token, shoppinglistId, shoppingitemId, data):
        """
        Method to make PUT request as a client and update shoppingitem.
        :param token: user auth token.
        :param shoppinglistId: shopping list id.
        :param shoppingitemId: shopping item id.
        :param data: new data.
        :return: response.
        """

        headers = dict(Authorization='Bearer %(token)s' % dict(token=token))
        data = json.dumps(data)
        url = url_for('shoppingitem_edit',
                      shoppinglistId=shoppinglistId, shoppingitemId=shoppingitemId)

        return self.client.put(url, data=data, headers=headers, content_type=self.content_type)

    def delete_shoppingitem(self, token, shoppinglistId, shoppingitemId):
        """
        Makes DELETE request as a client to delete associated shopping item.
        :param token: user auth token.
        :param id: shopping item id.
        :return: response
        """

        headers = dict(Authorization='Bearer %(token)s' % dict(token=token))
        url = url_for('shoppingitem_edit',
                      shoppinglistId=shoppinglistId, shoppingitemId=shoppingitemId)

        return self.client.delete(url, headers=headers, content_type=self.content_type)


class TestSearchAndPagination(TestShoppingItemsBase):
    """
    Base test case class for testing search functionality and pagination.
    """

    def __init__(self, *args, **kwargs):
        super(TestSearchAndPagination, self).__init__(*args, **kwargs)
        self.shoppinglists = ['Birthday', 'School', 'Breakfast', 'Lunch', 'Camping']

    def init(self, use_limit=False, per_page=False,
             limit=None, page=None):
        # register and authenticate client.
        self.register_user()
        login_resp = self.login_user()

        # get auth token.
        token = json.loads(login_resp.get_data(as_text=True))['auth_token']

        # create shoppinglists.
        for shl in self.shoppinglists:
            self.create_shoppinglist(token=token, name=shl)

        if any([use_limit, per_page]):
            if use_limit and per_page:
                return token, limit, page

            if use_limit and not per_page:
                return token, limit

            if not use_limit and per_page:
                return token, page

        return token

    def search_shoppinglist(self, token, keyword, limit=None, page=None):
        """
        Method to make search shopping lists.
        :param token: user auth token.
        :param keyword: word used to make search.
        :return: response.
        """

        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token))

        url = url_for('shoppinglist_search', q=keyword, limit=limit, page=page)
        return self.client.get(url, content_type=self.content_type, headers=headers)

