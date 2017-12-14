import collections
from base64 import b64encode
from flask_restful import url_for
from flask_testing import TestCase

from app import DB
from app.conf import app_config
from .base import TestBaseCase


class TestAuthenticationBaseCase(TestBaseCase):
    """
    Base class for authentication tests.
    """

    def setUp(self):
        """
        Prepares test environment for each test method.

        What it does.
        1. sets application configuration to testing.
        2. create tables.
        3. initialize test data and keywords.
        """

        self.model = collections.namedtuple('User', ['username', 'email', 'password'])
        self.test_user = self.model('gideon', 'gideon@gmail.com', 'g1Deonp@ssword')
        self.header_name = 'x-access-token'
        self.header = {}

        self.app.config.from_object(app_config.TestingConfig)

        DB.session.commit()
        DB.drop_all()
        DB.create_all()

    def tearDown(self):
        """
        Remove test tables and data.
        """

        DB.session.remove()
        DB.drop_all()

    def login_user(self, with_header=True, **credentials):
        """
        Login and authenticate user.
        """

        url = url_for('user_login')
        return self.client.post(url, data=credentials)

    def register_user(self, **details):
        """
        Helper method to register a user.

        :param details: username, email and password.
        :return: response.
        """
        data = details
        url = url_for('user_register')
        return self.client.post(url, data=data)

    def get_user_details(self, token):
        """
        Helper method to make a POST request to fetch user details.
        """

        url = url_for('user_detail')

        return self.client.get(url, headers={self.header_name: token})

    def update_user_info(self, token, data=None):
        """
         Helper method to update user details.
         """

        url = url_for('user_detail')
        return self.client.put(url, data=data, headers={self.header_name: token})

    def logout_user(self, token):
        """
        Helper method to make requests to logout logged in users.
        """

        url = url_for('user_logout')
        return self.client.delete(url, headers={self.header_name: token})

    def get_password_reset_token(self, data):
        """
        Makes POST request to get password reset token.

        :param data: user email.
        :return: response.
        """

        url = url_for('password_token')
        return self.client.post(url, data=data)

    def reset_password(self, data):
        """
        A helper method to make request to reset user password.

        :param data: username, email.
        :return: response.
        """

        url = url_for('password_reset')
        return self.client.post(url, data=data)

    def delete_user(self, token, password):
        """
        Helper method to make request to delete user account.

        :param token: user auth token.
        :param password: user password.
        :return: response.
        """

        url = url_for('user_detail')
        return self.client.delete(url, headers={self.header_name: token}, data=dict(password=password))