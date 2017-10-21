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
from ddt import ddt, file_data
import json

from . import \
    (account_created, app_config, db,
     User, TestBase)


@ddt
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
        self.app.config.from_object(app_config.TestingConfig)
        db.session.commit()
        db.drop_all()
        db.create_all()

        _ = collections.namedtuple('User', ['username', 'password', 'email'])
        _user_info = _('gideon', 'gideonpassword', 'gideon@gmail.com')
        self.base_url_prefix = '/api/v1/'
        self.content_type = 'application/json'
        self.user_info = _user_info
        self.register_url = self.base_url_prefix + 'auth/register'
        self.login_url = self.base_url_prefix + 'auth/login'
        self.logout_url = self.base_url_prefix + 'auth/logout/'

    def tearDown(self):
        """
        Called after every test to remove all tables in the database.
        """
        db.session.remove()
        db.drop_all()

    def register_user(self, username, password, email):
        """
        Helper method to register a user.

        Makes post request using user information initialized in
        the setUp method.
        """
        resp = self.client.post(self.register_url,
                                data=json.dumps(dict(username=username,
                                                     email=email,
                                                     password=password)),
                                content_type=self.content_type)
        return resp

    def login_user(self, username, password):
        """
        Helper method to login user.

        Makes post request using user information initialized in
        the setUp method.
        """
        resp = self.client.post(self.login_url,
                                data=json.dumps(dict(username=username,
                                                     password=password)),
                                content_type=self.content_type)
        return resp

    def logout_user(self, username):
        """
        Helper method to login user.

        Makes post request using user information initialized in
        the setUp method.
        """
        url = self.logout_url + username
        resp = self.client.get(url)
        return resp

    @file_data("test_data/valid_userinfo.json")
    def test_user_can_register(self, info):
        """
        Testing call to /auth/register/.
        """

        # register user
        resp = self.register_user(username=info[0],
                                  password=info[1],
                                  email=info[2])

        # returned data
        rtn_data = resp.data

        self.assertTrue(resp.status_code == 201)  # status_code 210 created.

        # username and email we used to create user should be in
        # returned data.
        self.assertIn(account_created, rtn_data)

    @file_data("test_data/valid_userinfo.json")
    def test_authenticated_login(self, info):
        """
        Test user cannot login again if authenticated.
        """
        # register user first
        # register
        reg_resp = self.register_user(username=info[0],
                                      password=info[1],
                                      email=info[2])

        # confirm registration response
        self.assertTrue(reg_resp.status_code == 201)
        reg_resp = reg_resp.get_data().decode()
        self.assertIn(account_created, reg_resp)

        # login user
        first_resp = self.login_user(username=info[0],
                                     password=info[1])

        self.assert200(first_resp)
        self.assertIn('Logged in',
                      first_resp.get_data().decode())

        # call make request to login again
        second_resp = self.login_user(username=info[0],
                                      password=info[1])

        self.assert200(second_resp)
        self.assertIn('Already logged in',
                      second_resp.get_data().decode())

    def test_registration_without_username(self):
        """
        Test registration without username.
        """
        expected_error_message = 'Provide a username'

        reg_resp = self.client.post(self.register_url,
                                    data=json.dumps(dict(email=self.user_info.email,
                                                         password=self.user_info.password)),
                                    content_type=self.content_type)

        self.assertIn(expected_error_message,
                      reg_resp.get_data().decode())
        self.assert400(reg_resp)

    def test_register_without_email(self):
        """
        Test registration without email.
        """
        expected_error_message = 'Provide an email'
        reg_url = self.base_url_prefix + 'auth/register'
        reg_resp = self.client.post(reg_url,
                                    data=json.dumps(dict(username=self.user_info.username,
                                                         password=self.user_info.password)),
                                    content_type=self.content_type)

        self.assertIn(expected_error_message,
                      reg_resp.get_data().decode())
        self.assert400(reg_resp)

    def test_register_without_password(self):
        """
        Test registration without password.
        """
        expected_error_message = 'Provide a password'
        reg_resp = self.client.post(self.register_url,
                                    data=json.dumps(dict(username=self.user_info.username,
                                                         email=self.user_info.email)),
                                    content_type=self.content_type)

        self.assertIn(expected_error_message,
                      reg_resp.get_data().decode())
        self.assert400(reg_resp)

    @file_data("test_data/valid_userinfo.json")
    def test_register_with_existing_username(self, info):
        """
        Test registration with existing username.
        """
        # register user first
        # register user
        self.register_user(username=info[0],
                           password=info[1],
                           email=info[2])

        second_reg_resp = self.register_user(username=info[0],
                                             password=info[1],
                                             email="different@gmail.com")

        self.assert400(second_reg_resp)
        self.assertIn('User with that username exists',
                      second_reg_resp.get_data().decode())

    @file_data("test_data/valid_userinfo.json")
    def test_register_with_existing_email(self, info):
        """
        Test registration with existing email.
        """
        # register user first
        # register
        self.register_user(username=info[0],
                           password=info[1],
                           email=info[2])

        second_reg_resp = self.register_user(username="newusername",
                                             password=info[1],
                                             email=info[2])

        self.assert400(second_reg_resp)
        self.assertIn('User with that email exists',
                      second_reg_resp.get_data().decode())

    def test_login_without_username(self):
        """A user should not be able to login without a username."""
        # login
        first_resp = self.client.post(self.login_url,
                                      data=json.dumps(dict(password=self.user_info.password)),
                                      content_type=self.content_type)

        self.assert400(first_resp)
        self.assertIn('Provide a username',
                      first_resp.get_data().decode())

    def test_login_without_password(self):
        """A user should not be able to login without a password."""
        # login
        first_resp = self.client.post(self.login_url,
                                      data=json.dumps(dict(username=self.user_info.email)),
                                      content_type=self.content_type)

        self.assert400(first_resp)
        self.assertIn('Provide a password',
                      first_resp.get_data().decode())

    def test_invalid_cridentials(self):
        """Test invalid cridentials provided by user."""
        # login
        resp = self.client.post(self.login_url,
                                data=json.dumps(dict(username="someuser",
                                                     password="somepassword")),
                                content_type=self.content_type)

        self.assert401(resp)
        self.assertIn('Incorrect username or password!!',
                      resp.get_data().decode())

    @file_data("test_data/valid_userinfo.json")
    def test_user_can_login(self, info):
        """
        Test call to /auth/login/
        """

        # register user first
        # register
        reg_resp = self.register_user(username=info[0],
                                      password=info[1],
                                      email=info[2])

        # confirm registration response
        self.assertTrue(reg_resp.status_code == 201)
        self.assertIn(account_created, reg_resp.data)

        # login user
        # login
        resp = self.login_user(username=info[0], password=info[1])

        self.assert200(resp)
        self.assertIn('Logged in', resp.data)

    @file_data("test_data/valid_userinfo.json")
    def test_view_account_details(self, info):
        """Test user can view account details."""

        # register user first
        # register
        reg_resp = self.register_user(username=info[0],
                                      password=info[1],
                                      email=info[2])

        # confirm registration response
        self.assertTrue(reg_resp.status_code == 201)
        self.assertIn(account_created, reg_resp.data)

        # login user
        # login
        resp = self.login_user(username=info[0], password=info[1])

        self.assert200(resp)
        self.assertIn('Logged in', resp.data)

        # view details url
        get_url = self.base_url_prefix + 'auth/%(username)s' \
                                         % dict(username=info[0])

        view_resp = self.client.get(get_url, content_type=self.content_type)

        user = User.query.filter_by(username=info[0]).first()

        # format date_joined to string.
        date_joined = user.date_joined.strftime("%a, %d %b %Y")
        self.assert200(view_resp)
        self.assertIn(user.username, view_resp.data)
        self.assertIn(user.email, view_resp.data)
        self.assertIn(date_joined, view_resp.data)

    @file_data("test_data/valid_userinfo.json")
    def test_update_user_details(self, info):
        """Test user can update details."""
        # register user first
        # register
        reg_resp = self.register_user(username=info[0],
                                      password=info[1],
                                      email=info[2])

        # confirm registration response
        self.assertTrue(reg_resp.status_code == 201)
        self.assertIn(account_created,
                      reg_resp.get_data().decode())

        # login user
        # login
        resp = self.login_user(username=info[0], password=info[1])

        self.assert200(resp)
        self.assertIn('Logged in',
                      resp.get_data().decode())

        # make update request
        update_url = self.base_url_prefix + 'auth/%(username)s' \
                                            % dict(username=info[0])

        new_details = {
            'username': 'newusername',
            'password': 'newpassword',
            'email': 'new@email.com'
        }

        data = json.dumps(new_details)

        update_resp = self.client.put(update_url,
                                      data=data,
                                      content_type=self.content_type)
        self.assert200(update_resp)
        self.assertIn("Account updated",
                      update_resp.get_data().decode())

    @file_data("test_data/valid_userinfo.json")
    def test_unautheticated_update_request(self, info):
        """Test cannot update account without being authenticated."""
        # register user first
        # register
        reg_resp = self.register_user(username=info[0],
                                      password=info[1],
                                      email=info[2])

        # confirm registration response
        self.assertTrue(reg_resp.status_code == 201)
        self.assertIn(account_created,
                      reg_resp.get_data().decode())

        # update url
        update_url = self.base_url_prefix + 'auth/%(username)s' \
                                            % dict(username=info[0])

        new_details = {
            'username': 'updatedusername',
            'password': 'updatedpassword',
            'email': 'updated@email.com'
        }

        data = json.dumps(new_details)

        update_resp = self.client.put(update_url,
                                      data=data,
                                      content_type=self.content_type)

        self.assert401(update_resp)
        self.assertIn("Login first",
                      update_resp.get_data().decode())

    @file_data("test_data/valid_userinfo.json")
    def test_update_with_none_existing_user(self, info):
        """Test non-existing user cannot update."""
        # update url
        update_url = self.base_url_prefix + 'auth/%(username)s' \
                                            % dict(username=info[0])

        new_details = {
            'username': 'updatedusername',
            'password': 'updatedpassword',
            'email': 'updated@email.com'
        }

        data = json.dumps(new_details)

        update_resp = self.client.put(update_url,
                                      data=data,
                                      content_type=self.content_type)

        self.assert401(update_resp)
        self.assertIn("Create account or login",
                      update_resp.get_data().decode())

    @file_data("test_data/valid_userinfo.json")
    def test_update_with_existing_data(self, info):
        """Test cannot update account with pre-existing data."""
        # register user first
        # register first user
        reg_resp = self.register_user(username=info[0],
                                      password=info[1],
                                      email=info[2])

        # register second user
        target_username = 'existingusername'
        target_email = "existingemail@email.com"
        reg_resp2 = self.register_user(username=target_username,
                                       password=info[1],
                                       email=target_email)

        # confirm registration responses
        self.assertTrue(reg_resp.status_code == 201)
        self.assertIn(account_created,
                      reg_resp.get_data().decode())

        self.assertTrue(reg_resp.status_code == 201)
        self.assertIn(account_created,
                      reg_resp2.get_data().decode())

        # login first user
        # login
        resp = self.login_user(username=info[0], password=info[1])

        self.assert200(resp)
        self.assertIn('Logged in',
                      resp.get_data().decode())

        # update url
        update_url = self.base_url_prefix + 'auth/%(username)s' \
                                            % dict(username=info[0])

        new_details2 = {
            'username': target_username,  # same as reg_resp2 username
            'password': 'somepassword',
            'email': 'new_user1@email.com'
        }

        new_details3 = {
            'username': "new_detailuser",
            'password': 'updatedpassword',
            'email': target_email  # same as reg2_resp email
        }

        # PUT data
        data2 = json.dumps(new_details2)
        data3 = json.dumps(new_details3)

        # make a PUT request
        update_det2 = self.client.put(update_url,
                                      data=data2,
                                      content_type=self.content_type)

        update_det3 = self.client.put(update_url,
                                      data=data3,
                                      content_type=self.content_type)

        # assertions
        self.assert400(update_det2)
        self.assert400(update_det3)
        self.assertIn("User with %(uname)s exists" %
                      dict(uname=target_username),
                      update_det2.get_data().decode())
        self.assertIn("User with %(email)s exists" %
                      dict(email=target_email),
                      update_det3.get_data().decode())

    @file_data("test_data/valid_userinfo.json")
    def test_logout(self, info):
        """
        Test user can logout.
        """
        # register user first
        # register
        reg_resp = self.register_user(username=info[0],
                                      password=info[1],
                                      email=info[2])

        # confirm registration response
        self.assertTrue(reg_resp.status_code == 201)
        self.assertIn(account_created,
                      reg_resp.get_data().decode())

        # login user
        # login
        resp = self.login_user(username=info[0], password=info[1])

        self.assert200(resp)
        self.assertIn('Logged in',
                      resp.get_data().decode())

        # logout user
        logout_resp = self.logout_user(info[0])

        self.assert200(logout_resp)
