# -*- coding: utf-8 -*-

"""Contains all Tests for system app user"""

import collections
from main import db
from web_app.conf import app_config
from web_app.core.exceptions import EmailExists, UsernameExists
from web_app.db.models import User

from .base import TestBase


class TestUserModel(TestBase):
    """tests main User model class"""

    def setUp(self):
        super(TestUserModel, self).setUp()  # call the super class setUp method
        self.app.config.from_object(app_config.TestingConfig)
        db.init_app(self.app)

        db.session.commit()
        db.drop_all()
        db.create_all()

        _info = collections.namedtuple('User', ['username', 'email', 'password'])
        user_info = _info('giddy', 'giddy@email.com', 'gideonpassword')

        self.user = User(username=user_info.username, email=user_info.email, password=user_info.password)
        self.user_info = user_info
        self._info = _info

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_user_username(self):
        """
        assert whether the user created has the same username as `gideon`
        """
        self.user.save()
        # retrieve the username itself
        added_user = User.query.filter_by(username=self.user_info.username).first().username
        self.assertEqual(added_user, self.user_info.username)

    def test_user_email(self):
        """
        Assert if user created has the expected email
        """
        self.user.save()
        added_user = User.query.filter_by(email=self.user_info.email).first()

        self.assertEqual(added_user.email, self.user_info.email)

    def test_user_password(self):
        """
        Assert if the user created has the expected password
        """
        user_raw_password = 'gideonpassword'
        self.user.save()
        adder_user = User.query.filter_by(username=self.user_info.username).first()

        self.assertTrue(adder_user.verify_password(user_raw_password))

    def test_update(self):
        """
        test if user values are updated successfully and new values are
        reflected back when we run the query.
        :return:
        """
        self.user.save()
        _new_data = self._info('gideon', 'gideon@yahoo.com', 'gideonpassword')
        self.user.username = _new_data.username
        self.user.email = _new_data.email
        self.user.save()

        saved_user = User.query.filter_by(username=_new_data.username).first()

        self.assertTrue((saved_user.username == _new_data.username and
                         saved_user.email == _new_data.email))

    def test_can_authenticate(self):
        """
        test if `is_authenticate` property will return True if
        `authenticate()` method is called against the created
        user instance.
        """
        self.user.save()  # save user instance
        self.user.authenticate()  # call authenticate method
        saved_user = User.query.filter_by(username=self.user_info.username).first()
        self.assertTrue(saved_user.is_authenticated)  # test

    def test_can_deauthenticate(self):
        """
        test if user can deauthenticate successfully after authenticate method
        has been called
        :return:
        """
        self.user.save()
        saved_user = User.query.filter_by(username=self.user_info.username).first()

        # test if authenticated is set to False initially
        self.assertFalse(saved_user.is_authenticated)

        # call authenticate method and test it
        self.user.authenticate()
        self.assertTrue(self.user.authenticate())
        self.assertTrue(saved_user.is_authenticated)

        # finally deauthenticate and test it
        self.user.deauthenticate()
        self.assertFalse(saved_user.is_authenticated)

    def test_unique_username(self):
        """
        Check if an exception is raised if the username is already used
        """
        with self.assertRaises(UsernameExists):
            self.user.save()  # save the user for the first time

            # call save() method for the second time that will
            # try to save the data for the second time.
            self.user.check_username()

    def test_unique_email(self):
        """
        check if an exception is raised if a used email is used for the second time
        """
        with self.assertRaises(EmailExists):
            # save the first user
            User('anotheruser', self.user_info.email, 'anotheruserpass').save()

            # another user with the same email as the first user
            another_user = User('anotheruser1', self.user_info.email, 'anotheruserpass')

            # call check method
            another_user.check_email()


# class TestUserRegisterAndLogin(TestBase):
#     """test user registration and login"""
#     def setUp(self):
#         super(TestUserRegisterAndLogin, self).setUp()
#         self.client = self.app.test_client()
#         self.user_register_data = {
#             'username': 'gideon',
#             'password': 'gideonpassword',
#             'email': 'gideon@email.com'
#         }
#         self.api_register_url = '/shopping-list/api/v1/auth/register/'
#         self.api_login_url = '/shopping-list/api/v1/auth/login/'
#
#     def test_user_registration(self):
#         """
#         test if response code is 404
#             `we currently don't have an endpoint to handle registration`
#         """
#         response = self.client.post(self.api_register_url,
#                                     data=self.user_register_data)
#         self.assertEqual(response.status_code, 201)
#
#     def test_user_login(self):
#         """
#         test is response code is 404
#             `there is no api endpoint to handle user login as of yet`
#         """
#         login_data = {
#             'username': self.user_register_data.get('username'),
#             'password': self.user_register_data.get('password')
#         }
#         response = self.client.post(self.api_login_url, data=login_data)
#         self.assertEqual(response.status_code, 200)
