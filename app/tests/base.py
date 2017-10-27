"""Base class for all tests"""

import collections
from flask import json
from flask_testing import TestCase


from . import \
    (app_config, APP, CONTENT_TYPE, DB, INVALID_EMAIL_ERR, LOGIN_URL, LOGOUT_URL,
     REFRESH_USER_TOKEN_URL, REGISTER_URL, REQUIRED_FIELDS_ERR, UPDATE_USER_DETAILS_URL,
     USER_DETAILS_URL)


class TestBase(TestCase):

    def __init__(self, *args, **kwargs):
        super(TestBase, self).__init__(*args, **kwargs)
        # initialize to None because it is not defined in the
        # TestCase init
        self.user_info = None
        self.require_field_err = REQUIRED_FIELDS_ERR
        self.invalid_email_err = INVALID_EMAIL_ERR

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

        return self.client.post(
            LOGIN_URL, data=json.dumps(cridentials), content_type=CONTENT_TYPE)

    def register_user(self, **details):
        """
        Helper method to login user.

        Makes post request using user information initialized in
        the setUp method.
        """

        return self.client.post(
            REGISTER_URL, data=json.dumps(dict(details)), content_type=CONTENT_TYPE)

    def logout_user(self, token):
        """
        Helper method to logout user.
        """

        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token)
        )
        url = LOGOUT_URL
        return self.client.delete(url, content_type=CONTENT_TYPE, headers=headers)

    def get_user_details(self, token):
        """
        Helper method to make a POST request to fetch user details.
        """

        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token)
        )

        return self.client.get(USER_DETAILS_URL, content_type=CONTENT_TYPE, headers=headers)

    def update_user_info(self, token, data):
        """
         Helper method to make a PUT request to update user details.
         """
        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token)
        )

        url = UPDATE_USER_DETAILS_URL
        return self.client.put(url, data=json.dumps(data), content_type=CONTENT_TYPE, headers=headers)

    def refresh_user_token(self, token):
        """
         Helper method to make a PUT request to update user details.
         """
        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token)
        )

        url = REFRESH_USER_TOKEN_URL
        return self.client.post(url, content_type=CONTENT_TYPE, headers=headers)

