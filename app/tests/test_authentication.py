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
import time

from ddt import ddt, file_data
from flask import json

from . import account_created, User, BlacklistToken
from .base import TestBase


@ddt
class TestUserAuth(TestBase):
    """
    Test class for app user authentication funtionalities.

    Note: this is integration testing  # http://www.agilenutshell.com/episodes/41-testing-pyramid
    """

    @file_data("test_data/valid_userinfo.json")
    def test_user_can_register(self, info):
        """
        Testing call to /auth/register/.
        """

        # register user
        resp = self.register_user(username=info[0], password=info[1], email=info[2])

        self.assertStatus(resp, 201)  # status_code 201 created.

        # username and email we used to create user should be in
        # returned data.
        self.assertIn(account_created, resp.get_data().decode())
        self.assertIn('token', resp.get_data().decode())
        self.assertIn('refresh_token', resp.get_data().decode())

    def test_registration_without_username(self):
        """
        Test registration without username.
        """

        reg_resp = self.register_user(email=self.user_info.email, password=self.user_info.password)
        err = json.loads(reg_resp.get_data(as_text=True))["messages"]["username"]
        self.assertIn(self.require_field_err, err)
        self.assertStatus(reg_resp, 422)

    def test_register_without_email(self):
        """
        Test registration without email.
        """

        expected_error_message = 'Email required'
        reg_resp = self.register_user(username=self.user_info.username,
                                      password=self.user_info.password)

        self.assertStatus(reg_resp, 422)
        error = json.loads(reg_resp.get_data(as_text=True))
        self.assertIn(self.require_field_err, error['messages']['email'])

    def test_invalid_email(self):
        """
        Test registration with invalid email does not pass.
        """

        reg_resp = self.register_user(username=self.user_info.username,
                                      email="invalidemail", password="password")

        err = json.loads(reg_resp.get_data(as_text=True))["messages"]["email"]
        self.assertIn(self.invalid_email_err, err)
        self.assertStatus(reg_resp, 422)

    def test_too_short_password(self):
        """
        Test short password not allowed.
        """

        reg_resp = self.register_user(username=self.user_info.username,
                                      email=self.user_info.email,
                                      password="123")

        err = json.loads(reg_resp.get_data(as_text=True))["messages"]["password"]
        self.assertIn("Shorter than minimum length 6.", err)
        self.assertStatus(reg_resp, 422)

    def test_register_without_password(self):
        """
        Test registration without password.
        """

        reg_resp = self.register_user(username=self.user_info.username,
                                      email=self.user_info.email)

        err = json.loads(reg_resp.get_data(as_text=True))["messages"]["password"]
        self.assertIn(self.require_field_err, err)
        self.assertStatus(reg_resp, 422)

    @file_data("test_data/valid_userinfo.json")
    def test_register_with_existing_username(self, info):
        """
        Test registration with existing username.
        """

        # register user first
        self.register_user(username=info[0], password=info[1], email=info[2])

        second_reg_resp = self.\
            register_user(username=info[0], password=info[1], email="different@gmail.com")

        self.assertStatus(second_reg_resp, 202)
        self.assertIn('User with that username exists',
                      second_reg_resp.get_data().decode())

    @file_data("test_data/valid_userinfo.json")
    def test_register_with_existing_email(self, info):
        """
        Test registration with existing email.
        """

        # register user first
        self.register_user(username=info[0], password=info[1], email=info[2])

        second_resp = self.register_user(username="newusername", password=info[1], email=info[2])

        self.assertStatus(second_resp, 202)
        self.assertIn('User with that email exists', second_resp.get_data().decode())

    def test_login_without_username(self):
        """
        Test user should not be able to login without a username.
        """

        # login
        first_resp = self.login_user(password=self.user_info.password)
        err = json.loads(first_resp.get_data(as_text=True))["messages"]["username"]

        self.assertStatus(first_resp, 422)
        self.assertIn(self.require_field_err, err)

    def test_login_without_password(self):
        """
        Test user should not be able to login without a password.
        """

        # login
        first_resp = self.login_user(username=self.user_info.email)

        err = json.loads(first_resp.get_data(as_text=True))["messages"]["password"]

        self.assertStatus(first_resp, 422)
        self.assertIn(self.require_field_err, err)

    def test_invalid_cridentials(self):
        """
        Test cridentials which don't exist in database provided by user.
        """

        # login
        resp = self.login_user(username="someuser", password="somepassword")

        self.assert401(resp)
        self.assertIn('Incorrect username or password!!', resp.get_data().decode())

    @file_data("test_data/valid_userinfo.json")
    def test_user_can_login(self, info):
        """
        Test user can login with correct cridentials.
        """

        # register user first
        reg_resp = self.register_user(username=info[0], password=info[1], email=info[2])

        # confirm registration response
        self.assertTrue(reg_resp.status_code == 201)
        self.assertIn(account_created, reg_resp.get_data().decode())

        # login user
        resp = self.login_user(username=info[0], password=info[1])

        self.assert200(resp)

        # a response should be sent containing access token and refresh_token
        self.assertIn('Logged in', resp.get_data().decode())
        self.assertIn('auth_token', resp.get_data().decode())
        self.assertIn('refresh_token', resp.get_data().decode())

    @file_data("test_data/valid_userinfo.json")
    def test_view_account_details(self, info):
        """
        Test user can view account details.
        """

        # register user first
        reg_resp = self.register_user(username=info[0], password=info[1], email=info[2])

        # confirm registration response
        self.assertTrue(reg_resp.status_code == 201)
        self.assertIn(account_created, reg_resp.get_data().decode())

        # login user
        resp = self.login_user(username=info[0], password=info[1])

        self.assert200(resp)
        self.assertIn('Logged in', resp.get_data().decode())

        token = json.loads(resp.get_data().decode())['auth_token']

        # get user details
        view_resp = self.get_user_details(token)

        # query user
        user = User.query.filter_by(username=info[0]).first()

        # format date_joined to string.
        date_joined = user.date_joined.strftime("%a, %d %b %Y")

        # assert response and data
        self.assert200(view_resp)
        self.assertIn(user.username, view_resp.get_data().decode())
        self.assertIn(user.email, view_resp.get_data().decode())
        self.assertIn(date_joined, view_resp.get_data().decode())

    @file_data("test_data/valid_userinfo.json")
    def test_update_user_details(self, info):
        """
        Test user can update details.
        """

        # register user first
        reg_resp = self.register_user(username=info[0], password=info[1], email=info[2])

        # confirm registration response
        self.assertTrue(reg_resp.status_code == 201)
        self.assertIn(account_created, reg_resp.get_data().decode())

        # login user
        resp = self.login_user(username=info[0], password=info[1])

        self.assert200(resp)
        self.assertIn('Logged in', resp.get_data().decode())

        new_details = {
            'username': 'new_admin',
            'password': 'newpassword',
            'email': 'new_admin@email.com'
        }

        # make update request
        token = json.loads(resp.get_data().decode())['auth_token']
        update_resp = self.update_user_info(token=token, data=new_details)

        data = json.loads(update_resp.get_data(as_text=True))['data']
        self.assert200(update_resp)
        self.assertIn("Account updated", update_resp.get_data().decode())
        self.assertTrue(new_details.get('username') == data['username'])
        self.assertTrue(new_details.get('email') == data['email'])

    @file_data("test_data/valid_userinfo.json")
    def test_update_with_existing_data(self, info):
        """
        Test cannot update account with pre-existing data.
        """

        # register first user
        reg_resp = self.register_user(username=info[0], password=info[1], email=info[2])

        # username and email that the first user will try to update to.
        target_username = 'existingusername'
        target_email = "existingemail@email.com"

        # register second user
        reg_resp2 = self.register_user(username=target_username, password=info[1], email=target_email)

        # confirm first user registration response
        self.assertStatus(reg_resp, 201)
        self.assertIn(account_created, reg_resp.get_data().decode())

        # confirm second user registration response
        self.assertTrue(reg_resp2.status_code == 201)
        self.assertIn(account_created, reg_resp2.get_data().decode())

        # login first user
        resp = self.login_user(username=info[0], password=info[1])
        token = json.loads(resp.get_data().decode())['auth_token']

        # assert first user login response
        self.assert200(resp)
        self.assertIn('Logged in', resp.get_data().decode())

        # details that the first user intends to update
        new_details2 = {
            'username': target_username,  # used username.
            'password': 'somepassword',
            'email': 'new_user1@email.com'
        }

        new_details3 = {
            'new_username': "new_detailuser",
            'password': 'updatedpassword',
            'email': target_email  # used email
        }

        # make a PUT request
        update_det2 = self.update_user_info(token=token, data=new_details2)

        update_det3 = self.update_user_info(token=token, data=new_details3)

        # assertions

        self.assertStatus(update_det2, 400)
        self.assertStatus(update_det3, 400)
        self.assertIn("User with %(uname)s exists" % dict(uname=target_username),
                      update_det2.get_data().decode())
        self.assertIn("User with %(email)s exists" % dict(email=target_email),
                      update_det3.get_data().decode())

    @file_data("test_data/valid_userinfo.json")
    def test_logout(self, info):
        """
        Test user can logout successfully..
        """

        # register user first
        # register
        reg_resp = self.register_user(username=info[0], password=info[1], email=info[2])
        _reg_response = json.loads(reg_resp.get_data(as_text=True))

        # confirm registration response
        self.assertTrue(reg_resp.status_code == 201)
        self.assertIn(account_created, _reg_response['message'])

        # login user
        resp = self.login_user(username=info[0], password=info[1])

        self.assert200(resp)
        _response = json.loads(resp.get_data(as_text=True))
        self.assertIn('Logged in', _response['message'])

        # logout user
        token = _response['auth_token']
        logout_resp = self.logout_user(token)

        # assert response, response will be ok regardless
        response = json.loads(
            logout_resp.get_data().decode()
        )
        self.assertTrue(response['status'] == 'success')
        self.assertTrue(response['message'] == 'Successfully logged out')
        self.assert200(logout_resp)

    @file_data("test_data/valid_userinfo.json")
    def test_cannot_use_auth_token_after_logout(self, info):
        """
            Test user cannot use auth_token after successful_logout.
        """

        # register user first
        # register
        reg_resp = self.register_user(username=info[0], password=info[1], email=info[2])
        _reg_response = json.loads(reg_resp.get_data(as_text=True))

        # confirm registration response
        self.assertTrue(reg_resp.status_code == 201)
        self.assertIn(account_created, _reg_response['message'])

        # login user
        resp = self.login_user(username=info[0], password=info[1])

        self.assert200(resp)
        _response = json.loads(resp.get_data(as_text=True))
        self.assertIn('Logged in', _response['message'])

        # logout user
        token = _response['auth_token']

        self.logout_user(token)

        login_response = self.get_user_details(token)
        data = json.loads(login_response.get_data().decode())
        self.assertStatus(login_response, 401)
        self.assertTrue(data['msg'] == 'Token has been revoked')