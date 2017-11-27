import collections
from base64 import b64encode
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

    def login_user(self, with_header=True, **cridentials):
        """
        Login and authenticate user.
        """
        auth = b64encode(
            bytes(
                cridentials.get('username', '') + ":" + cridentials.get('password', ''), 'ascii')
        ).decode('ascii')

        header = dict(Authorization='Basic %(auth)s' % dict(auth=auth))
        url = url_for('user_login')

        if with_header:
            return self.client.post(url, headers=header)

        else:
            return self.client.post(url)

    def register_user(self, **details):
        data = details
        url = url_for('user_register')
        return self.client.post(url, data=data)

    def get_user_details(self, token):
        """
        Helper method to make a POST request to fetch user details.
        """

        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token))

        url = url_for('user_detail')

        return self.client.get(url, headers=headers)

    def update_user_info(self, token, data=None):
        """
         Helper method to make a PUT request to update user details.
         """

        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token))

        url = url_for('user_detail')

        return self.client.put(url, data=data, headers=headers)

    def logout_user(self, token):
        """
        Helper method to make requests to logout logged in users.
        """

        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token)
        )

        url = url_for('user_logout')

        return self.client.delete(url, headers=headers)

    def get_password_reset_token(self, auth_token):
        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=auth_token))
        url = url_for('password_reset')
        return self.client.get(url, headers=headers)

    def reset_password(self, **data):
        """
        A method to make a post request with user details in order to reset user password.
        """

        url = url_for('password_reset')

        return self.client.post(url, data=data)

    def delete_user(self, token, confirm=False):
        """
        Makes DELETE request as client to delete user account.
        :param token: client auth token.
        :param confirm: True|False flag to authorize account delete.
        :return: resonse.
        """

        url = url_for('user_detail', confirm=confirm)

        headers = dict(
            Authorization='Bearer %(token)s' % dict(token=token))

        return self.client.delete(url, headers=headers)