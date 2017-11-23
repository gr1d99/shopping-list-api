import collections

from flask import json
from flask_restful import url_for
from flask_testing import TestCase

from app import APP, DB
from app.conf import app_config
from app.models import User


class TestBase(TestCase):

    def __init__(self, *args, **kwargs):
        super(TestBase, self).__init__(*args, **kwargs)
        # initialize to None because it is not defined in the
        # TestCase init
        model = collections.namedtuple('User', ['username', 'email', 'password'])
        user = model('gideon', 'gideon@gmail.com', 'gideonpassword')
        self.test_user = user

    def create_app(self):
        return APP

    def setUp(self):
        """
        Prepares test environment for each test method.

        What it does.
        1. sets application configuration to testing.
        2. create tables.
        """

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

    @staticmethod
    def query_user_from_db(username):
        user = User.get_user(username)
        return user

    def login_user(self, **cridentials):
        """
        Login and authenticate user.
        """

        url = url_for('user_login')
        return self.client.post(url, data=cridentials)

    def register_user(self, **details):
        """
        Register user.
        """

        data = details
        url = url_for('user_register')
        return self.client.post(url, data=data)

    # def logout_user(self, token):
    #     """
    #     Helper method to logout user.
    #     """
    #
    #     headers = dict(
    #         Authorization='Bearer %(token)s' % dict(token=token)
    #     )
    #
    #     url = url_for('user_logout')
    #
    #     return self.client.delete(url, content_type=self.content_type, headers=headers)
    #
    # def get_user_details(self, token):
    #     """
    #     Helper method to make a POST request to fetch user details.
    #     """
    #
    #     headers = dict(
    #         Authorization='Bearer %(token)s' % dict(token=token))
    #
    #     url = url_for('user_detail')
    #
    #     return self.client.get(url, content_type=self.content_type, headers=headers)
    #
    # def update_user_info(self, token, data):
    #     """
    #      Helper method to make a PUT request to update user details.
    #      """
    #
    #     data = json.dumps(data)
    #
    #     headers = dict(
    #         Authorization='Bearer %(token)s' % dict(token=token))
    #
    #     url = url_for('user_detail')
    #
    #     return self.client.put(url, data=data, content_type=self.content_type, headers=headers)
    #
    # def refresh_user_token(self, token):
    #     """
    #      Helper method to make a PUT request to update user details.
    #      """
    #
    #     headers = dict(
    #         Authorization='Bearer %(token)s' % dict(token=token)
    #     )
    #
    #     url = url_for('token_refresh')
    #
    #     return self.client.post(url, content_type=self.content_type, headers=headers)
    #
    # def reset_password(self, **data):
    #     """
    #     A method to make a post request with user details in order to reset user password.
    #     """
    #
    #     data = json.dumps(data)
    #
    #     url = url_for('password_reset')
    #
    #     return self.client.post(url, data=data, content_type=self.content_type)
    #
    # def delete_user(self, token):
    #     """
    #     Makes DELETE request as client to delete user account.
    #     :param token: client auth token.
    #     :return: resonse.
    #     """
    #
    #     url = url_for('user_detail')
    #
    #     headers = dict(
    #         Authorization='Bearer %(token)s' % dict(token=token))
    #
    #     return self.client.delete(url, headers=headers, content_type=self.content_type)