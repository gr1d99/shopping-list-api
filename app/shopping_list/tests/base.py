"""
Contains TestShoppingList Base class for all shopping list funtionalities.
"""
import collections

from flask import json
from flask_testing import TestCase

from app import APP, DB
from app.conf import app_config
from app.auth.tests import LOGIN_URL, REGISTER_URL, LOGOUT_URL

from . import CREATE_SHOPPING_LIST_URL


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
        self.shopping_list = __('test_shopping_list')

    def tearDown(self):
        """
        Called after every test to remove all tables in the database.
        """

        DB.session.remove()
        DB.drop_all()

    def login_user(self, **cridentials):
        """
        Helper method to login user.

        Makes post request using user information initialized in
        the setUp method.
        """

        return self.client.post(
            LOGIN_URL, data=json.dumps(cridentials), content_type=self.content_type)

    def register_user(self, **details):
        """
        Helper method to login user.

        Makes post request using user information initialized in
        the setUp method.
        """

        return self.client.post(
            REGISTER_URL, data=json.dumps(dict(details)), content_type=self.content_type)

    def logout_user(self, token):
        """
        Helper method to logout user.
        """

        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token)
        )
        url = LOGOUT_URL
        return self.client.delete(url, content_type=self.content_type, headers=headers)

    def create_shopping_list(self, token, **data):
        """
        Method to make a post request to create shopping list.
        """

        url = CREATE_SHOPPING_LIST_URL
        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token)
        )
        return self.client.post(url, data=json.dumps(dict(data)),
                                content_type=self.content_type, headers=headers,)
