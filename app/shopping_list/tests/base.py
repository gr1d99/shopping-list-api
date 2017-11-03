"""
Contains TestShoppingList Base class for all shopping list funtionalities.
"""
import collections

from flask import json
from flask_restful import url_for
from flask_testing import TestCase

from app import APP, DB
from app.conf import app_config
from app.auth.tests import LOGIN_URL, REGISTER_URL, LOGOUT_URL

from . import ALL_SHOPPINGITEMS_URL, PREFIX_ONE, PREFIX_TWO, CREATE_SHOPPINGITEMS_URL, UPDATE_SHOPPINGITEMS_URL, DELETE_SHOPPINGITEMS_URL


class TestShoppingListBase(TestCase):
    """
    Base class for all test cases for ShoppingList functionality.
    """

    def __init__(self, *args, **kwargs):
        super(TestShoppingListBase, self).__init__(*args, **kwargs)
        self.content_type = 'application/json'

    def create_app(self):
        """
        Creates an application instance.
        """

        return APP

    def setUp(self):
        """
        A method to prep app for testing.
        """

        # update app configuration to testing.
        self.app.config.from_object(app_config.TestingConfig)

        # create all models.
        DB.session.commit()
        DB.drop_all()
        DB.create_all()

        # test data
        _ = collections.namedtuple('User', ['username', 'password', 'email'])
        __ = collections.namedtuple('ShoppingList', ['name', ])

        self.user = _('gideon', 'gideonpassword', 'gideon@gmail.com')
        self.user_two = _('user_two', "user_two_password", "user_two@gmail.com")
        self.shopping_list = __('testshoppinglist')
        self.shopping_list_two = __('testshoppinglisttwo')

    def tearDown(self):
        """
        Called after every test to remove all tables in the database.
        """

        DB.session.remove()
        DB.drop_all()

    def login_user(self):
        """
        Helper method to login user.

        Makes post request using user information initialized in
        the setUp method.
        """

        cridentials = dict(
            username=self.user.username,
            password=self.user.password
        )

        return self.client.post(
            LOGIN_URL, data=json.dumps(cridentials), content_type=self.content_type)

    def login_user_two(self):
        """
        Helper method to login user.

        Makes post request using user information initialized in
        the setUp method.
        """

        cridentials = dict(
            username=self.user_two.username,
            password=self.user_two.password
        )

        return self.client.post(
            LOGIN_URL, data=json.dumps(cridentials), content_type=self.content_type)

    def register_user(self):
        """
        Helper method to login user.

        Makes post request using user information initialized in
        the setUp method.
        """

        user_info = dict(
            username=self.user.username,
            password=self.user.password,
            email=self.user.email
        )

        return self.client.post(
            REGISTER_URL, data=json.dumps(user_info), content_type=self.content_type)

    def register_second_user(self):
        """
        Helper method to register another user.

        Makes post request using user information initialized in
        the setUp method.
        """

        user_info = dict(
            username=self.user_two.username,
            password=self.user_two.password,
            email=self.user_two.email
        )

        return self.client.post(
            REGISTER_URL, data=json.dumps(user_info), content_type=self.content_type)

    def logout_user(self, token):
        """
        Helper method to logout user.
        """

        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token)
        )
        url = LOGOUT_URL
        return self.client.delete(url, content_type=self.content_type, headers=headers)

    def create_shoppinglist(self, token, **data):
        """
        Method to make a post request to create shopping list.
        """

        url = PREFIX_ONE
        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token)
        )

        data = json.dumps(data)
        return self.client.post(url, data=data,
                                content_type=self.content_type, headers=headers)

    def get_user_shoppinglists(self, token):
        """
        Method to make get request to fetch user shopping lists.
        """

        url = PREFIX_ONE
        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token)
        )
        return self.client.get(
            url, content_type=self.content_type, headers=headers
        )

    def get_user_shoppinglist_detail(self, token, id):
        """
        Method to make get request and fetch specific shopping list based on provided id.
        """

        # append shoppinglist id at the end of url.
        url = PREFIX_TWO + str(id)

        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token)
        )

        return self.client.get(url, headers=headers, content_type=self.content_type)

    def update_user_shoppinglist(self, token, id, new_info):
        """
        Method to make PUT request to update user shoppinglist.
        :param token: user auth token
        :param id: shopping list id
        :param new_info: details to update
        :return: response
        """

        url = PREFIX_TWO + str(id)

        data = json.dumps(new_info)

        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token)
        )

        return self.client.put(url, data=data, headers=headers,
                               content_type=self.content_type)

    def delete_shoppinglist(self, token, id):
        """
        Makes a PUT request as client to delete shoppinglist.
        :param token: user auth token.
        :param id: shoppinglist id.
        :return: response from server.
        """

        url = PREFIX_TWO + str(id)

        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token)
        )

        return self.client.delete(url, headers=headers, content_type=self.content_type)

    def search_shoppinglist(self, token, keyword):
        """
        Method to make search shopping lists.
        :param token: user auth token.
        :param keyword: word used to make search.
        :return: response.
        """

        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token)
        )

        url = url_for('shoppinglist_search', q=keyword)
        return self.client.get(url, content_type=self.content_type, headers=headers)


class TestShoppingItemsBase(TestShoppingListBase):
    def setUp(self):
        super(TestShoppingItemsBase, self).setUp()
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
            Authorization='Bearer %(token)s' % dict(token=token)
        )
        url = CREATE_SHOPPINGITEMS_URL % dict(id=shoppinglistId)
        return self.client.post(url, data=data, headers=headers, content_type=self.content_type)

    def get_shoppingitems(self, token, shoppinglistId):
        """
        Makes POST request as client to create shoppingitems.
        :param token: user auth token.
        :param shoppinglistId: shoppinglist id.
        :return: response.
        """

        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token)
        )
        url = CREATE_SHOPPINGITEMS_URL % (dict(id=shoppinglistId))
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

        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token)
        )
        url = UPDATE_SHOPPINGITEMS_URL % dict(shl_id=shoppinglistId, shi_id=shoppingitemId)
        data = json.dumps(
            data)

        return self.client.put(url, data=data, headers=headers, content_type=self.content_type)

    def delete_shoppingitem(self, token, shoppinglistId, shoppingitemId):
        """
        Makes DELETE request as a client to delete associated shopping item.
        :param token: user auth token.
        :param id: shopping item id.
        :return: response
        """

        url = DELETE_SHOPPINGITEMS_URL % dict(shl_id=shoppinglistId, shi_id=shoppingitemId)
        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token)
        )
        return self.client.delete(url, headers=headers, content_type=self.content_type)