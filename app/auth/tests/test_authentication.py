# -*- coding: utf-8 -*-

"""
This module tests user authentication endpoints.


Functionalities tested.
    1. User registration.
    2. User login.
    3. User logout.
    4. User account update.
    5. User account delete.
"""

import time
import flask

from ddt import ddt, file_data, data
from flask import json

from app.messages import *
from app.models import User
from .base import TestBase


@ddt
class TestUserAuth(TestBase):
    def test_user_can_register(self):
        response = self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        data = json.loads(response.get_data(as_text=True))

        # assertions.
        self.assertStatus(response, 201)  # status_code 201 created.
        self.assertTrue(data['status'], 'success')
        self.assertEqual(data['message'], account_created)
        self.assertIsNotNone(self.query_user_from_db(self.test_user.username))

    @data(" gideon", "     ", "  my   name")
    def test_cannot_register_with_username_that_startswith_spaces(self, name):
        response = self.register_user(
            username=name,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        data = json.loads(response.get_data(as_text=True))

        # assertions.
        self.assertStatus(response, 422)
        self.assertTrue(data['status'] == 'fail')

    # @data('1user', '333', '4562cfe')
    # def test_cannot_register_with_username_that_startswith_digits(self, digits):
    #     response = self.register_user(username=digits,
    #                                   email=self.test_user.email,
    #                                   password=self.test_user.password,
    #                                   confirm=self.test_user.password)
    #
    #     data = json.loads(response.get_data(as_text=True))
    #
    #     # assertions.
    #     self.assertStatus(response, 422)
    #     self.assertTrue(data['status'] == 'fail')

    @data("hello ", "hello world", "this is so invalid", "my   name")
    def test_cannot_register_with_username_that_contain_spaces(self, invalid):
        response = self.register_user(
            username=invalid,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        data = json.loads(response.get_data(as_text=True))

        # assertions.
        self.assertStatus(response, 422)
        self.assertTrue(data['status'] == 'fail')

    @data("http", "jerk", "https", "abuse", "damn")
    def test_cannot_register_with_reserved_and_unfriendly_words(self, invalid):
        response = self.register_user(
            username=invalid,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        data = json.loads(response.get_data(as_text=True))

        self.assertStatus(response, 422)
        self.assertTrue(data['status'] == 'fail')
        self.assertTrue(data['message'] == username_not_allowed)

    @data(' this password', '      ', '     sddfe')
    def test_cannot_register_with_password_that_startswith_with_spaces(self, password):
        response = self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password=password,
            confirm=password)

        data = json.loads(response.get_data(as_text=True))

        self.assertStatus(response, 422)
        self.assertTrue(data['status'] == 'fail')

    def test_cannot_register_with_passwords_that_donot_match(self):
        response = self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm='incorrectpassword')

        data = json.loads(response.get_data(as_text=True))

        # get user instance from database.
        user = self.query_user_from_db(self.test_user.username)  # should be None

        self.assert400(response)
        self.assertTrue(data['status'] == 'fail')
        self.assertTrue(data['message'] == passwords_donot_match)
        self.assertIsNone(user)

    def test_cannot_register_without_username(self):
        response = self.register_user(
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        # assertions.
        self.assertStatus(response, 422)

    def test_cannot_register_without_email(self):
        response = self.register_user(
            username=self.test_user.username,
            password=self.test_user.password)

        # assertions.
        self.assertStatus(response, 422)
        self.assertIsNone(self.query_user_from_db(self.test_user.username))

    def test_cannot_register_with_invalid_email(self):
        response = self.register_user(
            username=self.test_user.username,
            email="invalidemail",
            password="password")

        # assertions.
        self.assertStatus(response, 422)
        self.assertIsNone(self.query_user_from_db(self.test_user.username))

    def test_cannot_register_with_password_length_less_than_6(self):
        response = self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password="123")

        # assertions.
        self.assertStatus(response, 422)
        self.assertIsNone(self.query_user_from_db(self.test_user.username))

    def test_cannot_register_without_password(self):
        response = self.register_user(
            username=self.test_user.username,
            email=self.test_user.email)

        # assertions.
        self.assertStatus(response, 422)
        self.assertIsNone(self.query_user_from_db(self.test_user.username))

    def test_cannot_register_with_existing_username(self):
        # register first user.
        self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        # register second user with username already used.
        email = 'different@gmail.com'
        response = self.register_user(
            username=self.test_user.username,
            email=email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        data = json.loads(response.get_data(as_text=True))

        # assertions.
        self.assertStatus(response, 409)
        self.assertEqual(data['status'], 'fail')
        self.assertTrue(data['message'] == username_exists)
        self.assertIsNone(User.check_email(email))

    def test_cannot_register_with_existing_email(self):
        # register client first
        self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        new_username = 'newusername'
        response = self.register_user(
            username=new_username,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        data = json.loads(response.get_data(as_text=True))

        # assertions.
        self.assertStatus(response, 409)
        self.assertTrue(data['status'] == 'fail')
        self.assertTrue(data['message'] == email_exists)
        self.assertIsNone(self.query_user_from_db(new_username))

    def test_cannot_login_without_authorization_header(self):
        response = self.login_user(
            with_header=False,
            username=self.test_user.username,
            password=self.test_user.password)

        data = json.loads(
            response.get_data(as_text=True))

        self.assert401(response)
        self.assertTrue(data['message'] == cridentials_required)
        self.assertTrue(data['status'] == 'fail')

    def test_cannot_login_without_username(self):
        # login client.
        response = self.login_user(username='', password=self.test_user.password)
        self.assert401(response)

    def test_cannot_login_without_password(self):
        # login client.
        response = self.login_user(username=self.test_user.username, password='')
        self.assert401(response)

    def test_cannot_login_with_invalid_cridentials(self):
        # login
        response = self.login_user(username="someuser",
                                   password="somepassword")

        self.assertFalse(response.status_code == 200)
        self.assert401(response)
        self.assertTrue(user_does_not_exist,
                        response.get_data(as_text=True))

    def test_user_cannot_login_with_incorrect_password(self):
        # register user.
        self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        # login.
        response = self.login_user(
            username=self.test_user.username,
            password='this is not correct')

        data = json.loads(
            response.get_data(as_text=True))

        self.assertIsNot(response.status_code, 200)
        self.assertTrue(data['status'] == 'fail')
        self.assertTrue(incorrect_password == data['message'])

    def test_user_can_login_with_correct_cridentials(self):
        # register user.
        self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        # login user.
        response = self.login_user(
            username=self.test_user.username,
            password=self.test_user.password)

        data = json.loads(response.get_data(as_text=True))

        # assertions.
        self.assert200(response)
        # a response should be sent containing access token.
        self.assertEqual(successful_login, data['message'])
        self.assertIn('auth_token', data['data'].keys())

    def test_user_can_view_account_details(self):
        # register user first
        self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        # login user
        login_response = self.login_user(
            username=self.test_user.username,
            password=self.test_user.password)

        data = json.loads(login_response.get_data(as_text=True))

        token = data['data']['auth_token']

        # get client details
        view_resp = self.get_user_details(token)

        data = json.loads(view_resp.get_data(as_text=True))

        # query user from database.
        user = self.query_user_from_db(self.test_user.username)

        # format date_joined to string.
        date_joined = user.date_joined.strftime("%Y-%m-%d %H:%M:%S")

        # assert response and data
        self.assertIsNotNone(user)
        self.assert200(view_resp)
        self.assertEqual(user.username,
                         data['data']['username'])
        self.assertEqual(user.email,
                         data['data']['email'])
        self.assertEqual(date_joined,
                         data['data']['date_joined'])

    def test_user_can_update_account_details(self):
        # register user first
        self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        # login user
        login_response = self.login_user(
            username=self.test_user.username,
            password=self.test_user.password)

        new_details = {
            'username': 'new_admin',
            'email': 'new_admin@email.com'
        }

        data = json.loads(login_response.get_data(as_text=True))['data']

        # make update request
        token = data['auth_token']

        # make update request.
        update_resp = self.update_user_info(token=token, data=new_details)
        update_response_data = json.loads(update_resp.get_data(as_text=True))

        # assertions
        self.assert200(update_resp)
        self.assertEqual(account_updated, update_response_data['message'])
        self.assertEqual(new_details.get('username'), update_response_data['data']['username'])
        self.assertEqual(new_details.get('email'), update_response_data['data']['email'])

    def test_cannot_update_account_with_existing_data(self):
        # register user.
        self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        # username and email.
        target_username = 'existingusername'
        target_email = "existingemail@email.com"

        # register second user.
        self.register_user(
            username=target_username,
            email=target_email,
            password='password12',
            confirm='password12'
        )

        # login first user.
        login1_resp = self.login_user(
            username=self.test_user.username,
            password=self.test_user.password)

        token = json.loads(
            login1_resp.get_data(as_text=True))['data']['auth_token']

        # details that the first client intends to update.
        new_details1 = {
            'username': target_username,  # used username.
            'email': 'new_user1@email.com'}

        new_details2 = {
            'username': "anotherusername",
            'email': target_email  # used email
            }

        update_det1 = self.update_user_info(
            token=token, data=new_details1)

        update_det2 = self.update_user_info(
            token=token, data=new_details2)

        # assertions.
        self.assertFalse(update_det1.status_code == 200)
        self.assertFalse(update_det2.status_code == 200)
        self.assertStatus(update_det1, 409)
        self.assertStatus(update_det2, 409)
        self.assertTrue("User with %(uname)s exists" % dict(uname=target_username),
                      update_det1.get_data(as_text=True))

        self.assertIn("User with %(email)s exists" % dict(email=target_email),
                      update_det2.get_data(as_text=True))

    def test_no_change_is_applied_to_user_account_if_no_data_is_provided_in_update_request(self):
        self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        auth_token = json.loads(
            self.login_user(
                username=self.test_user.username,
                password=self.test_user.password
            ).get_data(as_text=True))['data']['auth_token']

        update_response = self.update_user_info(auth_token)
        update_response_data = json.loads(
            update_response.get_data(as_text=True))

        self.assert200(update_response)
        self.assertTrue(update_response_data['status'] == 'success')
        self.assertEqual(
            account_not_updated, update_response_data['message'])

    def test_user_can_logout(self):
        # register user.
        self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        # login user.
        login_response = self.login_user(
            username=self.test_user.username,
            password=self.test_user.password)

        # get auth_token.
        auth_token = json.loads(
            login_response.get_data(as_text=True)
        )['data']['auth_token']

        # make request to logout user.
        response = self.logout_user(auth_token)
        data = json.loads(
            response.get_data(as_text=True))

        # assertions.
        self.assert200(response)
        self.assertTrue(data['status'] == 'success')
        self.assertTrue(data['message'] == logout_successful)

        # try to get account details of logged in user.
        res = self.get_user_details(auth_token)

        # assert response.
        self.assert401(res)
        self.assertEqual(
            json.loads(
                res.get_data(as_text=True)
            )['msg'], 'Token has been revoked')

    def test_user_can_change_password(self):
        # old password and new password
        new_password = 'mynewpassword'

        # register user.
        self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        # login user.
        login_response = self.login_user(
            username=self.test_user.username,
            password=self.test_user.password)

        auth_token = json.loads(
            login_response.get_data(as_text=True))['data']['auth_token']

        # get password reset token.
        res = self.get_password_reset_token(auth_token)

        reset_token = json.loads(
            res.get_data(as_text=True))['data']['password_reset_token']

        # make actual response to change password.
        reset_response = self.reset_password(
            username=self.test_user.username,
            new_password=new_password,
            confirm=new_password,
            reset_token=reset_token)

        reset_response_data = json.loads(
            reset_response.get_data(as_text=True))

        # assert response.
        self.assert200(reset_response)
        self.assertEqual(
            reset_response_data['message'], password_changed)

        # login with new password.
        new_login_response = self.login_user(
            username=self.test_user.username,
            password=new_password)

        # response status code should be 200.
        self.assert200(new_login_response)

    def test_user_can_delete_account(self):
        # register user.
        self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        # login user
        login_response = self.login_user(
            username=self.test_user.username,
            password=self.test_user.password)

        # logout client.
        token = json.loads(
            login_response.get_data(as_text=True)['data']['auth_token'])

        # make delete request.
        delete_response = self.delete_user(token=token, confirm=True)

        data = json.loads(
            delete_response.get_data(as_text=True))
        self.assertStatus(delete_response, 200)
        self.assertTrue(delete_response['status'] == 'success')
        self.assertTrue(data['message'] == account_deleted)

        # @file_data("test_data/valid_userinfo.json")
    # def test_cannot_update_password_without_username_or_email(self, info):
    #     """
    #     Test client cannot update password without username or password.
    #     """
    #
    #     # register client.
    #     self.register_user(
    #         username=info[0], password=info[1], email=info[2])
    #
    #     # login user
    #     login_response = self.login_user(
    #         username=info[0], password=info[1]
    #     )
    #
    #     # old password and new password
    #     old_password = info[1]
    #     new_password = 'mynewpassword'
    #
    #     # make a post request to reset password api.
    #     reset_response = self.reset_password(
    #         old_password=old_password,
    #         new_password=new_password,
    #         confirm=new_password
    #     )
    #
    #     # get data returned.
    #     reset_response_data = json.loads(reset_response.get_data(as_text=True))
    #
    #     # assert reset password response.
    #     self.assert401(reset_response)
    #     self.assertTrue(reset_response_data['status'] == 'fail')
    #     self.assertTrue(reset_response_data['message'] == username_or_email_required)
    #
    # @file_data("test_data/valid_userinfo.json")
    # def test_can_update_password_with_username_only(self, info):
    #     """
    #     Test client can update password with username only.
    #     """
    #
    #     # register client.
    #     self.register_user(
    #         username=info[0], password=info[1], email=info[2])
    #
    #     # login client.
    #     login_response = self.login_user(
    #         username=info[0], password=info[1]
    #     )
    #
    #     # assert status code from login response
    #     self.assertStatus(login_response, 200)
    #
    #     # old password and new password
    #     old_password = info[1]
    #     new_password = 'mynewpassword'
    #
    #     # make a post request to reset password api
    #     reset_response = self.reset_password(
    #         username=info[0],
    #         old_password=old_password,
    #         new_password=new_password,
    #         confirm=new_password
    #     )
    #
    #     # get data returned
    #     reset_response_data = json.loads(
    #         reset_response.get_data(as_text=True))
    #
    #     # assert reset password response
    #     self.assert200(reset_response)
    #     self.assertTrue(reset_response_data['status'] == 'success')
    #     self.assertTrue(reset_response_data['message'] == password_changed)
    #
    # @file_data("test_data/valid_userinfo.json")
    # def test_can_update_password_with_email_only(self, info):
    #     """
    #     Test client can update password with email only.
    #     """
    #
    #     # register client.
    #     self.register_user(
    #         username=info[0], password=info[1], email=info[2])
    #
    #     # login client.
    #     self.login_user(
    #         username=info[0], password=info[1]
    #     )
    #
    #     # old password and new password.
    #     old_password = info[1]
    #     new_password = 'mynewpassword'
    #
    #     # make a post request to reset password api.
    #     reset_response = self.reset_password(
    #         email=info[2],
    #         old_password=old_password,
    #         new_password=new_password,
    #         confirm=new_password
    #     )
    #
    #     # get data returned
    #     reset_response_data = json.loads(reset_response.get_data(as_text=True))
    #
    #     # assert reset password response
    #     self.assert200(reset_response)
    #     self.assertTrue(reset_response_data['status'] == 'success')
    #     self.assertTrue(reset_response_data['message'] == password_changed)
    #
    # @file_data("test_data/valid_userinfo.json")
    # def test_cannot_update_password_with_incorrect_old_password(self, info):
    #     """
    #     Test client cannot update password without correct old_password.
    #     """
    #
    #     # register client.
    #     self.register_user(
    #         username=info[0], password=info[1], email=info[2])
    #
    #     # login client.
    #     self.login_user(
    #         username=info[0], password=info[1]
    #     )
    #
    #     # old password and new password.
    #     old_password = info[1]
    #     new_password = 'mynewpassword'
    #
    #     # make a post request to reset password api.
    #     reset_response = self.reset_password(
    #         username=info[0],
    #         old_password='somerandompassword',
    #         new_password=new_password,
    #         confirm=new_password
    #     )
    #
    #     # get data returned.
    #     reset_response_data = json.loads(reset_response.get_data(as_text=True))
    #
    #     # assert reset password response
    #     self.assert401(reset_response)
    #     self.assertTrue(reset_response_data['status'] == 'fail')
    #     self.assertTrue(reset_response_data['message'] == incorrect_old_password)
    #
    # @file_data("test_data/valid_userinfo.json")
    # def test_cannot_update_password_with_unmatched_passwords(self, info):
    #     """
    #     Test client cannot update password with new_password and confirm password that dont match.
    #     """
    #
    #     # register client.
    #     self.register_user(
    #         username=info[0], password=info[1], email=info[2])
    #
    #     # login client.
    #     self.login_user(
    #         username=info[0], password=info[1]
    #     )
    #
    #     # old password and new password.
    #     old_password = info[1]
    #     new_password = 'mynewpassword'
    #
    #     # make a post request to reset password api.
    #     reset_response = self.reset_password(
    #         username=info[0],
    #         old_password=old_password,
    #         new_password='somerandompassword',
    #         confirm=new_password
    #     )
    #
    #     # get data returned
    #     reset_response_data = json.loads(reset_response.get_data(as_text=True))
    #
    #     # assert reset password response
    #     self.assert401(reset_response)
    #     self.assertTrue(reset_response_data['status'] == 'fail')
    #     self.assertTrue(reset_response_data['message'] == passwords_donot_match)
    #