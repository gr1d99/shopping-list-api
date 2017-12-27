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

from flask import json

from app import messages as msg
from app.models import User
from .auth_base import TestAuthenticationBaseCase


class TestUserAuth(TestAuthenticationBaseCase):
    def test_user_can_register(self):
        response = self.register_user(
            username=self.test_user.username, email=self.test_user.email,
            password=self.test_user.password, confirm=self.test_user.password)

        data = json.loads(response.get_data(as_text=True))

        # assertions.
        self.assertStatus(response, 201)  # status_code 201 created.
        self.assertEqual(data['message'], msg.account_created)
        self.assertIsNotNone(User.get_by_username(self.test_user.username))

    def test_user_login_with_correct_credentials(self):
        # register user.
        self.register_user(
            username=self.test_user.username, email=self.test_user.email,
            password=self.test_user.password, confirm=self.test_user.password)

        # login user.
        response = self.login_user(
            username=self.test_user.username, password=self.test_user.password)

        data = json.loads(response.get_data(as_text=True))

        # assertions.
        self.assert200(response)

        # response should be sent containing access token.
        self.assertEqual(msg.successful_login, data['message'])
        self.assertIn('auth_token', data['data'].keys())

    def test_user_can_view_account_details(self):
        # register user first
        self.register_user(
            username=self.test_user.username, email=self.test_user.email,
            password=self.test_user.password, confirm=self.test_user.password)

        # login user
        login_response = self.login_user(
            username=self.test_user.username, password=self.test_user.password)

        data = json.loads(login_response.get_data(as_text=True))

        token = data['data']['auth_token']

        # get client details
        view_resp = self.get_user_details(token)

        data = json.loads(view_resp.get_data(as_text=True))

        # query user from database.
        user = User.get_by_username(self.test_user.username)

        # format date_joined to string.
        date_joined = user.date_joined.strftime("%Y-%m-%d %H:%M:%S")

        # assert response and data
        self.assertIsNotNone(user)
        self.assert200(view_resp)
        self.assertEqual(user.username, data['data']['username'])
        self.assertEqual(user.email, data['data']['email'])
        self.assertEqual(date_joined, data['data']['date_joined'])

    def test_user_can_update_account_details(self):
        # register user first
        self.register_user(
            username=self.test_user.username, email=self.test_user.email,
            password=self.test_user.password, confirm=self.test_user.password)

        # login user
        login_response = self.login_user(
            username=self.test_user.username, password=self.test_user.password)

        new_details = {'username': '@user100'}

        data = json.loads(login_response.get_data(as_text=True))['data']

        # make update request
        token = data['auth_token']

        # make update request.
        update_resp = self.update_user_info(token=token, data=new_details)
        update_response_data = json.loads(update_resp.get_data(as_text=True))

        # get user instance using new username.
        user = User.get_by_username(new_details.get('username'))

        # assertions
        self.assert200(update_resp)
        self.assertEqual(msg.account_updated, update_response_data['message'])
        self.assertIsNotNone(user)
        self.assertEqual(user.email, self.test_user.email)

    def test_no_change_is_applied_to_user_account_if_no_data_is_provided_in_update_request(self):
        self.register_user(
            username=self.test_user.username, email=self.test_user.email,
            password=self.test_user.password, confirm=self.test_user.password)

        auth_token = json.loads(
            self.login_user(
                username=self.test_user.username,
                password=self.test_user.password
            ).get_data(as_text=True))['data']['auth_token']

        update_response = self.update_user_info(auth_token)
        update_response_data = json.loads(update_response.get_data(as_text=True))

        self.assert200(update_response)
        self.assertEqual(msg.account_not_updated, update_response_data['message'])

    def test_user_can_logout(self):
        # register user.
        self.register_user(
            username=self.test_user.username, email=self.test_user.email,
            password=self.test_user.password, confirm=self.test_user.password)

        # login user.
        login_response = self.login_user(
            username=self.test_user.username, password=self.test_user.password)

        # get auth_token.
        auth_token = json.loads(
            login_response.get_data(as_text=True)
        )['data']['auth_token']

        # make request to logout user.
        response = self.logout_user(auth_token)
        data = json.loads(response.get_data(as_text=True))

        # assertions.
        self.assert200(response)
        self.assertTrue(data['message'] == msg.logout_successful)

        # try to get account details of logged in user.
        res = self.get_user_details(auth_token)

        # assert response.
        self.assert401(res)
        self.assertEqual(json.loads(
            res.get_data(as_text=True))['msg'], 'Token has been revoked')

    def test_user_can_change_password(self):
        # old password.
        new_password = 'Mynewp@ssw0rd'

        # register user.
        self.register_user(
            username=self.test_user.username, email=self.test_user.email,
            password=self.test_user.password, confirm=self.test_user.password)

        # get password reset token.
        data = dict(email=self.test_user.email)
        res = self.get_password_reset_token(data)

        reset_token = json.loads(res.get_data(as_text=True))['data']['password_reset_token']

        details = dict(
            username=self.test_user.username, new_password=new_password,
            confirm=new_password, reset_token=reset_token)

        # make actual response to change password.
        reset_response = self.reset_password(details)

        reset_response_data = json.loads(reset_response.get_data(as_text=True))

        # assert response.
        self.assert200(reset_response)
        self.assertEqual(reset_response_data['message'], msg.password_changed)

        # login with new password.
        new_login_response = self.login_user(
            username=self.test_user.username, password=new_password)

        # response status code should be 200.
        self.assert200(new_login_response)

    def test_cannot_reset_password_with_expired_token(self):
        # old password.
        new_password = 'm@yN3wpassword'

        # register user.
        self.register_user(
            username=self.test_user.username, email=self.test_user.email,
            password=self.test_user.password, confirm=self.test_user.password)

        data = dict(email=self.test_user.email)

        # get password reset token.
        res = self.get_password_reset_token(data)

        reset_token = json.loads(res.get_data(as_text=True))['data']['password_reset_token']

        # make actual response to change password.
        details = dict(
            username=self.test_user.username, new_password=new_password,
            confirm=new_password, reset_token=reset_token)

        self.reset_password(details)

        # make another request with the same token provided.
        response = self.reset_password(details)

        response_data = json.loads(response.get_data(as_text=True))

        self.assertStatus(response, 422)
        self.assertEqual(response_data['message'], msg.reset_token_expired)

    def test_user_can_delete_account(self):
        # register user.
        self.register_user(
            username=self.test_user.username, email=self.test_user.email,
            password=self.test_user.password, confirm=self.test_user.password)

        # login user
        login_response = self.login_user(
            username=self.test_user.username, password=self.test_user.password)

        # logout client.
        token = json.loads(login_response.get_data(as_text=True))['data']['auth_token']

        # make delete request.
        delete_response = self.delete_user(token, self.test_user.password)

        data = json.loads(delete_response.get_data(as_text=True))

        self.assertStatus(delete_response, 200)
        self.assertTrue(data['message'] == msg.account_deleted)
