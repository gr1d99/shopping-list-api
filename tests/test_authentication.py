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

from ddt import ddt, data
from flask import json

from app.messages import *
from app.models import User
from .auth_base import TestAuthenticationBaseCase


@ddt
class TestUserAuth(TestAuthenticationBaseCase):
    def test_user_can_register(self):
        response = self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        data = json.loads(response.get_data(as_text=True))

        # assertions.
        self.assertStatus(response, 201)  # status_code 201 created.
        self.assertEqual(data['message'], account_created)
        self.assertIsNotNone(User.get_by_username(self.test_user.username))

    @data(" G1deon#", "     ", "  my  name", "@@@@@@@@@@@@@@@")
    def test_cannot_register_with_invalid_username(self, name):
        response = self.register_user(
            username=name,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        # assertions.
        self.assertStatus(response, 422)

    @data("http", "jerk", "https", "abuse", "damn")
    def test_cannot_register_with_reserved_and_unfriendly_words(self, invalid):
        response = self.register_user(
            username=invalid,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        data = json.loads(response.get_data(as_text=True))

        self.assertStatus(response, 422)
        self.assertTrue(data['message'] == username_not_allowed)

    def test_cannot_register_with_passwords_that_donot_match(self):
        response = self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm='incorrectpassword')

        data = json.loads(response.get_data(as_text=True))

        # get user instance from database.
        user = User.get_by_username(self.test_user.username)  # should be None

        self.assert400(response)
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
        self.assertIsNone(User.get_by_username(self.test_user.username))

    def test_cannot_register_with_invalid_email(self):
        response = self.register_user(
            username=self.test_user.username,
            email="invalidemail",
            password="password")

        # assertions.
        self.assertStatus(response, 422)
        self.assertIsNone(User.get_by_username(self.test_user.username))

    def test_cannot_register_with_password_length_less_than_6(self):
        response = self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password="123")

        # assertions.
        self.assertStatus(response, 422)
        self.assertIsNone(User.get_by_username(self.test_user.username))

    @data('111111111111', 'password', '           ')
    def test_cannot_register_with_invalid_password(self, password):
        response = self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password=password,
            confirm=password)

        # assertions.
        self.assertStatus(response, 422)
        self.assertIsNone(User.get_by_username(self.test_user.username))

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
        self.assertTrue(data['message'] == email_exists)
        self.assertIsNone(User.get_by_username(new_username))

    def test_cannot_login_with_invalid_credentials(self):
        # login
        response = self.login_user(username="someuser",
                                   password="somepassword")

        self.assertFalse(response.status_code == 200)
        self.assert404(response)
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
        self.assertTrue(incorrect_password == data['message'])

    def test_user_can_login_with_correct_credentials(self):
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
            username=self.test_user.username,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        # login user
        login_response = self.login_user(
            username=self.test_user.username,
            password=self.test_user.password)

        new_details = {
            'username': '@user100'
        }

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
        self.assertEqual(account_updated, update_response_data['message'])
        self.assertIsNotNone(user)
        self.assertEqual(user.email, self.test_user.email)

    def test_cannot_update_account_with_existing_data(self):
        # register user.
        self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        # register second user.
        self.register_user(
            username='newuser',
            email='somenewemail@gmail.com',
            password='Password12@',
            confirm='Password12@'
        )

        # login first user.
        login1_resp = self.login_user(
            username=self.test_user.username,
            password=self.test_user.password)

        token = json.loads(
            login1_resp.get_data(as_text=True))['data']['auth_token']

        # update first user with second user username.

        new_details = {'username': 'newuser'}
        update_det = self.update_user_info(token, new_details)

        # assertions.
        self.assertFalse(update_det.status_code == 200)
        self.assertStatus(update_det, 409)
        self.assertIn(new_username_exists % dict(username=new_details.get('username')),
                      update_det.get_data(as_text=True))

    @data('@#$&', 'invalid username', '""""', '     ')
    def test_cannot_update_account_with_invalid_email(self, username):
        self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        # login user.
        login_response = self.login_user(
            username=self.test_user.username,
            password=self.test_user.password)

        token = json.loads(
            login_response.get_data(as_text=True))['data']['auth_token']

        update_det = {'username': username}

        update_response = self.update_user_info(
            token=token, data=update_det)

        # query from user objects from db.
        obj = User.get_by_username(username)

        # assertions.
        self.assertStatus(update_response, 422)
        self.assertIsNone(obj)

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
        data = json.loads(response.get_data(as_text=True))

        # assertions.
        self.assert200(response)
        self.assertTrue(data['message'] == logout_successful)

        # try to get account details of logged in user.
        res = self.get_user_details(auth_token)

        # assert response.
        self.assert401(res)
        self.assertEqual( json.loads(
            res.get_data(as_text=True))['msg'], 'Token has been revoked')

    def test_cannot_get_reset_token_with_email_that_does_not_exist(self):
        # old password.
        new_password = 'Mynewp@ssw0rd'

        # register user.
        self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        # get password reset token.
        data = dict(email="empty@gmail.com")
        res = self.get_password_reset_token(data)
        res_data = json.loads(res.get_data(as_text=True))

        self.assertFalse(res.status_code == 200)
        self.assertEqual(res_data['message'], email_does_not_exist)

    def test_user_can_change_password(self):
        # old password.
        new_password = 'Mynewp@ssw0rd'

        # register user.
        self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        # get password reset token.
        data = dict(email=self.test_user.email)
        res = self.get_password_reset_token(data)

        reset_token = json.loads(
            res.get_data(as_text=True))['data']['password_reset_token']

        details = dict(
            username=self.test_user.username,
            new_password=new_password,
            confirm=new_password,
            reset_token=reset_token)

        # make actual response to change password.
        reset_response = self.reset_password(details)

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

    def test_user_cannot_reset_password_without_reset_token(self):
        # old password.
        new_password = 'th1s 1s N$w'

        # register user.
        self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        details = dict(
            username=self.test_user.username,
            new_password=new_password,
            confirm=new_password,
            reset_token='')

        reset_response = self.reset_password(details)

        err = json.loads(
            reset_response.get_data(as_text=True))

        # assertions.
        self.assertStatus(reset_response, 422)
        self.assertTrue(err['message'], reset_token_required)

    @data('hdbvhbdjbdbdbvd', 'dcece345678cuye7', "    dfghjcbvgsc")
    def test_cannot_reset_password_with_invalid_token(self, token):
        # old password.
        new_password = 'this is a new password'

        # register user.
        self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        details = dict(
            username=self.test_user.username,
            new_password=new_password,
            confirm=new_password,
            reset_token=token)

        reset_response = self.reset_password(details)

        err = json.loads(
            reset_response.get_data(as_text=True))

        # assertions.
        self.assertStatus(reset_response, 422)
        self.assertTrue(
            err['message'], reset_token_does_not_exist)

    # @data('@gmail.com', 'invalidemail.com', '""@gmail.com', '   @gmail.com')
    # def test_user_cannot_reset_password_with_invalid_email(self, email):
    #     # make reset request.
    #     response = self.get_password_reset_token(email)
    #     self.assertStatus(response, 422)
    #     self.assertNotIn('reset_token', response.get_data(as_text=True))

    def test_cannot_reset_password_with_expired_token(self):
        # old password.
        new_password = 'm@yN3wpassword'

        # register user.
        self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        data = dict(email=self.test_user.email)

        # get password reset token.
        res = self.get_password_reset_token(data)

        reset_token = json.loads(
            res.get_data(as_text=True))['data']['password_reset_token']

        # make actual response to change password.
        details = dict(
            username=self.test_user.username,
            new_password=new_password,
            confirm=new_password,
            reset_token=reset_token)

        self.reset_password(details)

        # make another request with the same token provided.
        response = self.reset_password(details)

        response_data = json.loads(
            response.get_data(as_text=True))

        self.assertStatus(response, 422)
        self.assertEqual(response_data['message'], reset_token_expired)

    def test_cannot_reset_password_with_non_existing_username(self):
        # old password.
        new_password = 'm@yN3wpassword'

        # register user.
        self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        data = dict(email=self.test_user.email)

        # get password reset token.
        res = self.get_password_reset_token(data)

        reset_token = json.loads(
            res.get_data(as_text=True))['data']['password_reset_token']

        # make actual response to change password.
        details = dict(
            username="anonymous",
            new_password=new_password,
            confirm=new_password,
            reset_token=reset_token)

        self.reset_password(details)

        # make another request with the same token provided.
        response = self.reset_password(details)

        response_data = json.loads(
            response.get_data(as_text=True))

        self.assertStatus(response, 403)

    def test_cannot_reset_password_with_passwords_that_dont_match(self):
        # old password.
        new_password = 'm@yN3wpassword'

        # register user.
        self.register_user(
            username=self.test_user.username,
            email=self.test_user.email,
            password=self.test_user.password,
            confirm=self.test_user.password)

        data = dict(email=self.test_user.email)

        # get password reset token.
        res = self.get_password_reset_token(data)

        reset_token = json.loads(
            res.get_data(as_text=True))['data']['password_reset_token']

        # make actual response to change password.
        details = dict(
            username=self.test_user.username,
            new_password=new_password,
            confirm="incorrect",
            reset_token=reset_token)

        self.reset_password(details)

        # make another request with the same token provided.
        response = self.reset_password(details)

        self.assertStatus(response, 409)

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
            login_response.get_data(as_text=True))['data']['auth_token']

        # make delete request.
        delete_response = self.delete_user(token, self.test_user.password)

        data = json.loads(
            delete_response.get_data(as_text=True))

        self.assertStatus(delete_response, 200)
        self.assertTrue(data['message'] == account_deleted)

    def test_cannot_delete_account_with_incorrect_passwords(self):
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
            login_response.get_data(as_text=True))['data']['auth_token']

        # make delete request.
        delete_response = self.delete_user(token, "very incorrect")

        data = json.loads(delete_response.get_data(as_text=True))

        self.assertStatus(delete_response, 409)
        self.assertTrue(data['message'] == incomplete_delete)
        self.assertIsNotNone(User.get_by_username(self.test_user.username))
