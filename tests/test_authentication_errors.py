# -*- coding: utf-8 -*-

"""
This module tests for errors in user authentication endpoints.
"""

from ddt import ddt, data
from flask import json

from app import messages as msg
from app.models import User
from .auth_base import TestAuthenticationBaseCase


@ddt
class TestUserAuthErrorsCase(TestAuthenticationBaseCase):
    @data(" G1deon#", "     ", "  my  name", "@@@@@@@@@@@@@@@")
    def test_cannot_register_with_invalid_username(self, name):
        response = self.register_user(
            username=name, email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        self.assertStatus(response, 422)

    @data("http", "jerk", "https", "abuse", "damn")
    def test_cannot_register_with_reserved_and_unfriendly_words(self, invalid):
        response = self.register_user(
            username=invalid, email=self.test_user.email,
            password=self.test_user.password, confirm=self.test_user.password)

        res_data = json.loads(response.get_data(as_text=True))

        self.assertStatus(response, 422)
        self.assertTrue(res_data['message'] == msg.username_not_allowed)

    def test_cannot_register_with_passwords_that_dont_match(self):
        response = self.register_user(
            username=self.test_user.username, email=self.test_user.email,
            password=self.test_user.password, confirm='incorrectpassword')

        res_data = json.loads(response.get_data(as_text=True))

        self.assert400(response)
        self.assertTrue(res_data['message'] == msg.passwords_donot_match)

    def test_cannot_register_without_username(self):
        response = self.register_user(
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        self.assertStatus(response, 422)

    def test_cannot_register_without_email(self):
        response = self.register_user(
            username=self.test_user.username, password=self.test_user.password)

        self.assertStatus(response, 422)
        self.assertIsNone(User.get_by_username(self.test_user.username))

    def test_cannot_register_with_invalid_email(self):
        response = self.register_user(
            username=self.test_user.username,
            email="invalidemail",
            password="password")

        self.assertStatus(response, 422)
        self.assertIsNone(User.get_by_username(self.test_user.username))

    def test_cannot_register_with_password_length_less_than_6(self):
        response = self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password="123")

        self.assertStatus(response, 422)
        self.assertIsNone(User.get_by_username(self.test_user.username))

    @data('111111111111', 'password', '           ')
    def test_cannot_register_with_invalid_password(self, password):
        response = self.register_user(
            username=self.test_user.username, email=self.test_user.email,
            password=password, confirm=password)

        self.assertStatus(response, 422)
        self.assertIsNone(User.get_by_username(self.test_user.username))

    def test_cannot_register_with_existing_username(self):
        # register first user.
        self.register_user(
            username=self.test_user.username, email=self.test_user.email,
            password=self.test_user.password, confirm=self.test_user.password)

        # register second user with username already used.
        email = 'different@gmail.com'
        response = self.register_user(
            username=self.test_user.username, email=email,
            password=self.test_user.password, confirm=self.test_user.password)

        res_data = json.loads(response.get_data(as_text=True))

        self.assertStatus(response, 409)
        self.assertTrue(res_data['message'] == msg.username_exists)

    def test_cannot_register_with_existing_email(self):
        # register client first
        self.register_user(
            username=self.test_user.username, email=self.test_user.email,
            password=self.test_user.password, confirm=self.test_user.password)

        new_username = 'newusername'
        response = self.register_user(
            username=new_username, email=self.test_user.email,
            password=self.test_user.password, confirm=self.test_user.password)

        res_data = json.loads(response.get_data(as_text=True))

        self.assertStatus(response, 409)
        self.assertTrue(res_data['message'] == msg.email_exists)

    def test_cannot_login_with_invalid_credentials(self):
        # login
        response = self.login_user(username="someuser", password="somepassword")

        self.assertFalse(response.status_code == 200)
        self.assert404(response)
        self.assertTrue(msg.user_does_not_exist, response.get_data(as_text=True))

    def test_user_cannot_login_with_incorrect_password(self):
        self.register_user(
            username=self.test_user.username, email=self.test_user.email,
            password=self.test_user.password, confirm=self.test_user.password)

        # login.
        response = self.login_user(username=self.test_user.username, password='this is not correct')

        res_data = json.loads(response.get_data(as_text=True))

        self.assertIsNot(response.status_code, 200)
        self.assertTrue(msg.incorrect_password == res_data['message'])

    def test_cannot_update_account_with_existing_data(self):
        self.register_user(
            username=self.test_user.username, email=self.test_user.email,
            password=self.test_user.password, confirm=self.test_user.password)

        # register second user.
        self.register_user(
            username='newuser', email='somenewemail@gmail.com',
            password='Password12@', confirm='Password12@')

        login1_resp = self.login_user(
            username=self.test_user.username, password=self.test_user.password)

        token = json.loads(
            login1_resp.get_data(as_text=True))['data']['auth_token']

        # update first user with second user username.
        new_details = {'username': 'newuser'}
        update_det = self.update_user_info(token, new_details)

        self.assertFalse(update_det.status_code == 200)
        self.assertStatus(update_det, 409)
        self.assertIn(msg.new_username_exists % dict(username=new_details.get('username')),
                      update_det.get_data(as_text=True))

    @data('@#$&', 'invalid username', '""""', '     ')
    def test_cannot_update_account_with_invalid_email(self, username):
        self.register_user(
            username=self.test_user.username, email=self.test_user.email,
            password=self.test_user.password, confirm=self.test_user.password)

        # login user.
        login_response = self.login_user(
            username=self.test_user.username, password=self.test_user.password)

        token = json.loads(login_response.get_data(as_text=True))['data']['auth_token']
        update_det = {'username': username}
        update_response = self.update_user_info(token=token, data=update_det)

        self.assertStatus(update_response, 422)

    def test_cannot_get_reset_token_with_email_that_does_not_exist(self):
        self.register_user(
            username=self.test_user.username, email=self.test_user.email,
            password=self.test_user.password, confirm=self.test_user.password)

        # get password reset token.
        res_data = dict(email="empty@gmail.com")
        res = self.get_password_reset_token(res_data)
        res_data = json.loads(res.get_data(as_text=True))

        self.assertFalse(res.status_code == 200)
        self.assertEqual(res_data['message'], msg.email_does_not_exist)

    def test_user_cannot_reset_password_without_reset_token(self):
        # old password.
        new_password = 'th1s 1s N$w'

        self.register_user(
            username=self.test_user.username, email=self.test_user.email,
            password=self.test_user.password, confirm=self.test_user.password)

        details = dict(
            username=self.test_user.username, new_password=new_password,
            confirm=new_password, reset_token='')

        reset_response = self.reset_password(details)
        err = json.loads(reset_response.get_data(as_text=True))

        self.assertStatus(reset_response, 422)
        self.assertTrue(err['message'], msg.reset_token_required)

    @data('hdbvhbdjbdbdbvd', 'dcece345678cuye7', "    dfghjcbvgsc")
    def test_cannot_reset_password_with_invalid_token(self, token):
        # old password.
        new_password = 'this is a new password'

        # register user.
        self.register_user(
            username=self.test_user.username, email=self.test_user.email,
            password=self.test_user.password, confirm=self.test_user.password)

        details = dict(
            username=self.test_user.username, new_password=new_password,
            confirm=new_password, reset_token=token)

        reset_response = self.reset_password(details)
        err = json.loads(reset_response.get_data(as_text=True))

        self.assertStatus(reset_response, 422)
        self.assertTrue(err['message'], msg.reset_token_does_not_exist)

    def test_cannot_reset_password_with_non_existing_username(self):
        # old password.
        new_password = 'm@yN3wpassword'

        self.register_user(
            username=self.test_user.username, email=self.test_user.email,
            password=self.test_user.password, confirm=self.test_user.password)

        res_data = dict(email=self.test_user.email)

        # get password reset token.
        res = self.get_password_reset_token(res_data)
        reset_token = json.loads(res.get_data(as_text=True))['data']['password_reset_token']

        # make actual response to change password.
        details = dict(
            username="anonymous", new_password=new_password,
            confirm=new_password, reset_token=reset_token)

        self.reset_password(details)

        # make another request with the same token provided.
        response = self.reset_password(details)
        self.assertStatus(response, 403)

    def test_cannot_reset_password_with_passwords_that_dont_match(self):
        # old password.
        new_password = 'm@yN3wpassword'

        # register user.
        self.register_user(
            username=self.test_user.username, email=self.test_user.email,
            password=self.test_user.password, confirm=self.test_user.password)

        res_data = dict(email=self.test_user.email)

        # get password reset token.
        res = self.get_password_reset_token(res_data)

        reset_token = json.loads(res.get_data(as_text=True))['data']['password_reset_token']

        # make actual response to change password.
        details = dict(
            username=self.test_user.username, new_password=new_password,
            confirm="incorrect", reset_token=reset_token)

        self.reset_password(details)

        # make another request with the same token provided.
        response = self.reset_password(details)
        self.assertStatus(response, 409)

    # def test_cannot_delete_account_with_incorrect_passwords(self):
    #     # register user.
    #     self.register_user(
    #         username=self.test_user.username, email=self.test_user.email,
    #         password=self.test_user.password, confirm=self.test_user.password)
    #
    #     # login user
    #     login_response = self.login_user(
    #         username=self.test_user.username, password=self.test_user.password)
    #
    #     # logout client.
    #     token = json.loads(login_response.get_data(as_text=True))['data']['auth_token']
    #
    #     # make delete request.
    #     delete_response = self.delete_user(token, "very incorrect")
    #
    #     res_data = json.loads(delete_response.get_data(as_text=True))
    #
    #     self.assertStatus(delete_response, 409)
    #     self.assertTrue(res_data['message'] == msg.incomplete_delete)
