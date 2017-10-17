# -*- coding: utf-8 -*-

"""Contains all Tests for system app user"""

import collections
import unittest
from main import db
from web_app.conf import app_config
from web_app.db.models import User

from .base import TestBase


class TestUserBase(TestBase):
    """Base class for User model and authentication"""
    def setUp(self):
        """Create instances and objects that will be used by the tests"""
        super(TestUserBase, self).setUp()
        self.app.config.from_object(app_config.TestingConfig)
        db.init_app(self.app)
        db.session.commit()
        db.drop_all()
        db.create_all()

    # def tearDown(self):
    #     db.session.remove()
    #     db.drop_all()


class TestUserModel(TestUserBase):
    """tests main User model class"""

    def setUp(self):
        super(TestUserModel, self).setUp()  # call the super class setUp method
        _test_user_data = collections.namedtuple('User', ['username', 'email', 'password'])
        test_user_data = _test_user_data('gideon', 'gideon@gmail.com', 'gideonpassword')
        self.test_user = User(username=test_user_data.username,
                              email=test_user_data.email,
                              password=test_user_data.password)

    # def test_user_username(self):
    #     """
    #     assert whether the user created has the same username as `gideon`
    #     """
    #     self.test_user.save()
    #
    #     # retrieve the username itself
    #     added_user = User.query.filter_by(username=self.
    #                                       test_user.username).first().username
    #
    #     self.assertEqual(added_user, self.test_user.username)
    #
    # def test_user_email(self):
    #     """
    #     Assert if user created has the expected email
    #     """
    #     self.test_user.save()
    #     added_user = User.query.filter_by(email=self.test_user.email).first()
    #     self.assertEqual(added_user.email, self.test_user.email)
    #
    # def test_user_password(self):
    #     """
    #     Assert if the user created has the expected password
    #     """
    #     user_raw_password = 'gideonpassword'
    #     self.test_user.save()
    #
    #     # query user details
    #     adder_user = User.query.filter_by(username=self.test_user.username).first()
    #     self.assertTrue(adder_user.verify_password(user_raw_password))

    def test_update_user(self):
        """
        Test if user details are updated
        :return:
        """
        new_name = 'gideonkim'
        self.test_user.save()
        saved_user = User.query.filter_by(username=self.test_user.username).first()
        saved_user.username = new_name
        saved_user.save()
        se


    def test_delete_user(self):
        """
        Test if user is deleted successfully from the database
        :return:
        """

# class TestUserRegisterAndLogin(TestUserBase):
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
#
#
# if __name__ == '__main__':
#     unittest.main()
