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
from ddt import ddt, file_data
from flask import json

from . import account_created, User
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

        self.assertTrue(resp.status_code == 201)  # status_code 201 created.

        # username and email we used to create user should be in
        # returned data.
        self.assertIn(account_created,
                      resp.get_data().decode())

    @file_data("test_data/valid_userinfo.json")
    def test_authenticated_login(self, info):
        """
        Test user cannot login again if authenticated.
        """

        # register user first
        reg_resp = self.register_user(username=info[0], password=info[1], email=info[2])

        # confirm registration response
        self.assertTrue(reg_resp.status_code == 201)
        reg_resp = reg_resp.get_data().decode()
        self.assertIn(account_created, reg_resp)

        # login user
        first_resp = self.login_user(username=info[0], password=info[1])

        self.assert200(first_resp)
        self.assertIn('Logged in',
                      first_resp.get_data().decode())

        # call make request to login again
        second_resp = self.login_user(username=info[0], password=info[1])

        self.assert200(second_resp)
        self.assertIn('Already logged in',
                      second_resp.get_data().decode())

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

        self.assert400(second_reg_resp)
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

        self.assert400(second_resp)
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
        self.assertIn('Logged in', resp.get_data().decode())

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

        # get user details
        view_resp = self.get_user_details(username=info[0])

        # query user
        user = User.query.filter_by(username=info[0]).first()

        # format date_joined to string.
        date_joined = user.date_joined.strftime("%a, %d %b %Y")

        # assert response and data
        self.assert200(view_resp)
        self.assertIn(user.username, view_resp.get_data().decode())
        self.assertIn(user.email, view_resp.get_data().decode())
        self.assertIn(date_joined, view_resp.get_data().decode())

    def test_view_details_with_non_existing_user(self):
        """
        Test a user who does not exist cannot view any details.
        """

        # get user details
        view_resp = self.get_user_details(username="idontexist")

        self.assertStatus(view_resp, 401)
        self.assertIn('Please login or sign up first', view_resp.get_data(as_text=True))

    @file_data("test_data/valid_userinfo.json")
    def test_view_details_with_unauthenticated_user(self, info):
        """
        Test a user who is not authenticated cannot view any details.
        """

        # register user first
        reg_resp = self.register_user(username=info[0], password=info[1], email=info[2])

        # confirm registration response
        self.assertTrue(reg_resp.status_code == 201)
        self.assertIn(account_created, reg_resp.get_data(as_text=True))

        # get user details
        view_resp = self.get_user_details(username=info[0])
        err = json.loads(view_resp.get_data(as_text=True))["message"]

        self.assertIn("Please login", err)
        self.assertStatus(view_resp, 401)

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
            'username': 'newusername',
            'password': 'newpassword',
            'email': 'new@email.com'
        }

        # make update request
        update_resp = self.update_user_info(username=info[0], data=new_details)

        self.assert200(update_resp)
        self.assertIn("Account updated", update_resp.get_data().decode())

    @file_data("test_data/valid_userinfo.json")
    def test_unautheticated_update_request(self, info):
        """
        Test cannot update account without being authenticated.
        """

        # register user first
        reg_resp = self.register_user(username=info[0], password=info[1], email=info[2])

        # confirm registration response
        self.assertTrue(reg_resp.status_code == 201)
        self.assertIn(account_created, reg_resp.get_data().decode())

        new_details = {
            'username': 'updatedusername',
            'password': 'updatedpassword',
            'email': 'updated@email.com'
        }

        update_resp = self.update_user_info(username=info[0], data=new_details)

        self.assert401(update_resp)
        self.assertIn("Login first", update_resp.get_data().decode())

    @file_data("test_data/valid_userinfo.json")
    def test_update_with_none_existing_user(self, info):
        """
        Test non-existing user cannot update.
        """

        new_details = {
            'username': 'updatedusername',
            'password': 'updatedpassword',
            'email': 'updated@email.com'
        }

        update_resp = self.update_user_info(username=info[0], data=new_details)

        self.assert401(update_resp)
        self.assertIn("Create account or login", update_resp.get_data().decode())

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
        self.assertTrue(reg_resp.status_code == 201)
        self.assertIn(account_created, reg_resp.get_data().decode())

        # confirm second user registration response
        self.assertTrue(reg_resp.status_code == 201)
        self.assertIn(account_created, reg_resp2.get_data().decode())

        # login first user
        resp = self.login_user(username=info[0], password=info[1])

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
            'username': "new_detailuser",
            'password': 'updatedpassword',
            'email': target_email  # used email
        }

        # make a PUT request
        update_det2 = self.update_user_info(username=info[0], data=new_details2)

        update_det3 = self.update_user_info(username=info[0], data=new_details3)

        # assertions
        self.assert400(update_det2)
        self.assert400(update_det3)
        self.assertIn("User with %(uname)s exists" % dict(uname=target_username),
                      update_det2.get_data().decode())
        self.assertIn("User with %(email)s exists" % dict(email=target_email),
                      update_det3.get_data().decode())

    @file_data("test_data/valid_userinfo.json")
    def test_logout(self, info):
        """
        Test user can logout.
        """

        # register user first
        # register
        reg_resp = self.register_user(username=info[0], password=info[1], email=info[2])

        # confirm registration response
        self.assertTrue(reg_resp.status_code == 201)
        self.assertIn(account_created,
                      reg_resp.get_data().decode())

        # login user
        resp = self.login_user(username=info[0], password=info[1])

        self.assert200(resp)
        self.assertIn('Logged in', resp.get_data().decode())

        # logout user
        logout_resp = self.logout_user(info[0])

        # assert response, response will be ok regardless
        self.assert200(logout_resp)
