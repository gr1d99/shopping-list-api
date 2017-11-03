import collections
from flask import json
from flask_restful import url_for
from flask_testing import TestCase

from app import APP, DB

from app.conf import app_config
from app.messages import *


class TestBase(TestCase):

    def __init__(self, *args, **kwargs):
        super(TestBase, self).__init__(*args, **kwargs)
        # initialize to None because it is not defined in the
        # TestCase init
        self.content_type = 'application/json'
        self.user_info = None
        self.require_field_err = data_required
        self.invalid_email_err = invalid_email

    def create_app(self):
        return APP

    def setUp(self):
        """
        Call super class setUp method.

        We need to override the setUp method because there is need
        to set the app config environment to testing.
        """

        self.app.config.from_object(app_config.TestingConfig)
        DB.session.commit()
        DB.drop_all()
        DB.create_all()

        _ = collections.namedtuple('User', ['username', 'password', 'email'])
        _user_info = _('gideon', 'gideonpassword', 'gideon@gmail.com')
        self.user_info = _user_info

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

        data = json.dumps(cridentials)

        url = url_for('user_login')

        return self.client.post(url, data=data, content_type=self.content_type)

    def register_user(self, **details):
        """
        Helper method to login user.

        Makes post request using user information initialized in
        the setUp method.
        """

        data = json.dumps(details)

        url = url_for('user_register')

        return self.client.post(url, data=data, content_type=self.content_type)

    def logout_user(self, token):
        """
        Helper method to logout user.
        """

        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token)
        )

        url = url_for('user_logout')

        return self.client.delete(url, content_type=self.content_type, headers=headers)

    def get_user_details(self, token):
        """
        Helper method to make a POST request to fetch user details.
        """

        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token))

        url = url_for('user_detail')

        return self.client.get(url, content_type=self.content_type, headers=headers)

    def update_user_info(self, token, data):
        """
         Helper method to make a PUT request to update user details.
         """

        data = json.dumps(data)

        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token))

        url = url_for('user_detail')

        return self.client.put(url, data=data, content_type=self.content_type, headers=headers)

    def refresh_user_token(self, token):
        """
         Helper method to make a PUT request to update user details.
         """

        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token)
        )

        url = url_for('token_refresh')

        return self.client.post(url, content_type=self.content_type, headers=headers)

    def reset_password(self, **data):
        """
        A method to make a post request with user details in order to reset user password.
        """

        data = json.dumps(data)

        url = url_for('password_reset')

        return self.client.post(url, data=data, content_type=self.content_type)

    def delete_user(self, token):
        """
        Makes DELETE request as client to delete user account.
        :param token: client auth token.
        :return: resonse.
        """

        url = url_for('user_detail')

        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token))

        return self.client.delete(url, headers=headers, content_type=self.content_type)