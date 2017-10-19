# -*- coding: utf-8 -*-

"""
    Contains tests for user authentication functinalities through app api endpoints.

    Functionalities to be tested include.
        1. User registration.
        2. User Login.
        3. User data update(username, email, password).

    All functionalities are to be tested through the application
    api(v1) endpoints.

    Current api version is v1.
"""

import collections
import json

from flask import jsonify
from main import db
from web_app.conf import app_config
from .base import TestBase


class TestUserAuth(TestBase):
    """
    Test class for app user authentication funtionalities.

    Note: this is integration testing  # http://www.agilenutshell.com/episodes/41-testing-pyramid
    """

    def setUp(self):
        """
        Call super class setUp method.

        We need to override the setUp method because there is need
        to set the app config environment to testing.
        """
        super(TestUserAuth, self).setUp()
        db.session.commit()
        db.drop_all()
        db.create_all()

        _ = collections.namedtuple('User', ['username', 'password', 'email'])
        _user_info = _('gideon', 'gideonpassword', 'gideon@gmail.com')
        self.app.config.from_object(app_config.TestingConfig)
        self.base_url_prefix = '/api/v1/'
        self.content_type = 'application/json'
        self.user_info = _user_info

    def tearDown(self):
        """
        Called after every test to remove all tables in the database.
        """
        db.session.remove()
        db.drop_all()

    def test_user_can_register(self):
        """
        Testing call to /auth/register/.
        """
        # register url
        url = self.base_url_prefix + 'auth/register/'
        resp = self.client.post(url,
                                data=json.dumps(dict(username=self.user_info.username,
                                                     email=self.user_info.email,
                                                     password=self.user_info.password)),
                                content_type=self.content_type)

        # returned data
        rtn_data = resp.get_data()

        self.assertTrue(resp.status_code == 201)  # status_code 210 created.

        # username and email we used to create user should be in
        # returned data.
        self.assertIn(self.user_info.username, rtn_data)
        self.assertIn(self.user_info.email, rtn_data)

    def test_user_can_login(self):
        """
        Test call to /auth/login/
        """

        # register user first
        # register url
        reg_url = self.base_url_prefix + 'auth/register/'
        reg_resp = self.client.post(reg_url,
                                    data=json.dumps(dict(username=self.user_info.username,
                                                         email=self.user_info.email,
                                                         password=self.user_info.password)),
                                    content_type=self.content_type)

        # confirm registration response
        self.assertTrue(reg_resp.status_code == 201)
        self.assertIn(self.user_info.username, reg_resp.get_data())
        self.assertIn(self.user_info.email, reg_resp.get_data())

        # login user
        # login url
        login_url = self.base_url_prefix + 'auth/login/'
        resp = self.client.post(login_url,
                                data=dict(username=self.user_info.username,
                                          password=self.user_info.password),
                                content_type=self.content_type)
        self.assertTrue(resp.status_code == 200)

    def test_logout(self):
        """
        Test call to /auth/logout/
        """
        url = self.base_url_prefix + 'auth/logout/'

        # register user first
        # register url
        reg_url = self.base_url_prefix + 'auth/register/'
        reg_resp = self.client.post(reg_url,
                                    data=json.dumps(dict(username=self.user_info.username,
                                                         email=self.user_info.email,
                                                         password=self.user_info.password)),
                                    content_type=self.content_type)

        # confirm registration response
        self.assertTrue(reg_resp.status_code == 201)
        self.assertIn(self.user_info.username, reg_resp.get_data())
        self.assertIn(self.user_info.email, reg_resp.get_data())

        # login user
        # login url
        login_url = self.base_url_prefix + 'auth/login/'
        login_resp = self.client.post(login_url,
                                      data=dict(username=self.user_info.username,
                                                password=self.user_info.password),
                                      content_type=self.content_type)
        self.assertTrue(login_resp.status_code == 200)

        # make request to logout
        logout_resp = self.client.get(url)
        self.assertTrue(logout_resp.status_code == 200)
