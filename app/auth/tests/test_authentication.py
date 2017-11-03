# -*- coding: utf-8 -*-

"""
    Contains tests for user authentication functinalities through app api endpoints.

    Functionalities to be tested include.
        1. User registration.
        2. User Login.
        3. User data update(username, email, password).
        4. User access tokens

    All functionalities are to be tested through the application
    api(v1) endpoints.

    Current api version is v1.
"""
import time

from ddt import ddt, file_data
from flask import json

from app.messages import *
from app.models import User
from .base import TestBase


@ddt
class TestUserAuth(TestBase):
    """
    Test class for app user authentication functionalities.

    http://www.agilenutshell.com/episodes/41-testing-pyramid
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
        self.assertIn(account_created, resp.get_data(as_text=True))

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
        Test client cannot register without email.
        """

        reg_resp = self.register_user(username=self.user_info.username,
                                      password=self.user_info.password)

        # assertions.
        self.assertStatus(reg_resp, 422)
        error = json.loads(reg_resp.get_data(as_text=True))
        self.assertIn(self.require_field_err, error['messages']['email'])

    def test_invalid_email(self):
        """
        Test client cannot register with invalid email.
        """

        reg_resp = self.register_user(username=self.user_info.username,
                                      email="invalidemail", password="password")

        # assertions.
        err = json.loads(reg_resp.get_data(as_text=True))["messages"]["email"]
        self.assertIn(self.invalid_email_err, err)
        self.assertStatus(reg_resp, 422)

    def test_too_short_password(self):
        """
        Test client cannot register with short password.
        """

        reg_resp = self.register_user(username=self.user_info.username,
                                      email=self.user_info.email,
                                      password="123")

        # assertions.
        err = json.loads(reg_resp.get_data(as_text=True))["messages"]["password"]
        self.assertIn("Shorter than minimum length 6.", err)
        self.assertStatus(reg_resp, 422)

    def test_register_without_password(self):
        """
        Test client cannot register without password.
        """

        reg_resp = self.register_user(username=self.user_info.username,
                                      email=self.user_info.email)

        # assertions.
        err = json.loads(reg_resp.get_data(as_text=True))["messages"]["password"]
        self.assertIn(self.require_field_err, err)
        self.assertStatus(reg_resp, 422)

    @file_data("test_data/valid_userinfo.json")
    def test_register_with_existing_username(self, info):
        """
        Test client cannot register with existing username.
        """

        # register client first.
        self.register_user(
            username=info[0], password=info[1], email=info[2])

        second_reg_resp = self.\
            register_user(username=info[0], password=info[1], email="different@gmail.com")

        self.assertStatus(second_reg_resp, 202)
        self.assertIn(
            'User with that username exists', second_reg_resp.get_data(as_text=True))

    @file_data("test_data/valid_userinfo.json")
    def test_register_with_existing_email(self, info):
        """
        Test client cannot register with existing email.
        """

        # register client first
        self.register_user(
            username=info[0], password=info[1], email=info[2])

        second_resp = self.register_user(
            username="newusername", password=info[1], email=info[2])

        self.assertStatus(second_resp, 202)
        self.assertIn('User with that email exists', second_resp.get_data(as_text=True))

    def test_login_without_username(self):
        """
        Test user should not be able to login without a username.
        """

        # login client.
        first_resp = self.login_user(password=self.user_info.password)
        err = json.loads(first_resp.get_data(as_text=True))["messages"]["username"]

        self.assertStatus(first_resp, 422)
        self.assertIn(self.require_field_err, err)

    def test_login_without_password(self):
        """
        Test user should not be able to login without a password.
        """

        # login client.
        first_resp = self.login_user(username=self.user_info.email)

        err = json.loads(
            first_resp.get_data(as_text=True))["messages"]["password"]

        self.assertStatus(first_resp, 422)
        self.assertIn(self.require_field_err, err)

    def test_invalid_cridentials(self):
        """
        Test client cannot login with cridentials that don't exist in db.
        """

        # login
        resp = self.login_user(username="someuser", password="somepassword")

        self.assert401(resp)
        self.assertIn(incorrect_password_or_username, resp.get_data(as_text=True))

    @file_data("test_data/valid_userinfo.json")
    def test_user_can_login(self, info):
        """
        Test client can login with correct cridentials.
        """

        # register user first
        reg_resp = self.register_user(username=info[0], password=info[1], email=info[2])

        # confirm registration response
        self.assertTrue(reg_resp.status_code == 201)
        self.assertIn(account_created, reg_resp.get_data(as_text=True))

        # login user
        resp = self.login_user(username=info[0], password=info[1])

        # assertions.
        self.assert200(resp)

        # a response should be sent containing access token and refresh_token
        self.assertIn('Logged in', resp.get_data(as_text=True))
        self.assertIn('auth_token', resp.get_data(as_text=True))
        self.assertIn('refresh_token', resp.get_data(as_text=True))

    @file_data("test_data/valid_userinfo.json")
    def test_view_account_details(self, info):
        """
        Test client can view account details.
        """

        # register user first
        reg_resp = self.register_user(username=info[0], password=info[1], email=info[2])

        # confirm registration response
        self.assertTrue(reg_resp.status_code == 201)
        self.assertIn(account_created, reg_resp.get_data(as_text=True))

        # login user
        resp = self.login_user(username=info[0], password=info[1])

        self.assert200(resp)
        self.assertIn('Logged in', resp.get_data(as_text=True))

        token = json.loads(resp.get_data(as_text=True))['auth_token']

        # get client details
        view_resp = self.get_user_details(token)

        # query user from database.
        user = User.query.filter_by(username=info[0]).first()

        # format date_joined to string.
        date_joined = user.date_joined.strftime("%a, %d %b %Y")

        # assert response and data
        self.assert200(view_resp)

        self.assertIn(
            user.username, view_resp.get_data(as_text=True))

        self.assertIn(
            user.email, view_resp.get_data(as_text=True))

        self.assertIn(
            date_joined, view_resp.get_data(as_text=True))

    @file_data("test_data/valid_userinfo.json")
    def test_update_user_details(self, info):
        """
        Test client can update account details.
        """

        # register user first
        reg_resp = self.register_user(
            username=info[0], password=info[1], email=info[2])

        # confirm registration response
        self.assertTrue(
            reg_resp.status_code == 201)

        self.assertIn(
            account_created, reg_resp.get_data(as_text=True))

        # login user
        resp = self.login_user(username=info[0], password=info[1])

        self.assert200(resp)
        self.assertIn('Logged in', resp.get_data(as_text=True))

        new_details = {
            'username': 'new_admin',
            'password': 'newpassword',
            'email': 'new_admin@email.com'
        }

        # make update request
        token = json.loads(
            resp.get_data(as_text=True))['auth_token']

        # make update request.
        update_resp = self.update_user_info(token=token, data=new_details)

        data = json.loads(
            update_resp.get_data(as_text=True))['data']

        self.assert200(update_resp)

        self.assertIn(
            "Account updated", update_resp.get_data(as_text=True))

        self.assertTrue(
            new_details.get('username') == data['username'])

        self.assertTrue(
            new_details.get('email') == data['email'])

    @file_data("test_data/valid_userinfo.json")
    def test_update_with_existing_data(self, info):
        """
        Test client cannot update account with pre-existing data such as
        username that exists.
        """

        # register client.
        registration1_response = self.register_user(
            username=info[0], password=info[1], email=info[2])

        # username and email.
        target_username = 'existingusername'
        target_email = "existingemail@email.com"

        # register second client.
        registration2_response = self.register_user(
            username=target_username, password='password12', email=target_email)

        # confirm first client registration response.
        self.assertStatus(registration1_response, 201)

        self.assertIn(
            account_created, registration2_response.get_data(as_text=True))

        # confirm second client registration response.
        self.assertTrue(
            registration1_response.status_code == 201)

        self.assertIn(
            account_created, registration2_response.get_data(as_text=True))

        # login first client.
        login1_resp = self.login_user(
            username=info[0], password=info[1])

        token = json.loads(
            login1_resp.get_data(as_text=True))['auth_token']

        # assert first client login response.
        self.assert200(login1_resp)

        self.assertIn(
            'Logged in', login1_resp.get_data(as_text=True))

        # details that the first client intends to update.
        new_details2 = {
            'username': target_username,  # used username.
            'email': 'new_user1@email.com'
        }

        new_details3 = {
            'new_username': "new_detailuser",
            'email': target_email  # used email
        }

        # make a PUT request
        update_det2 = self.update_user_info(
            token=token, data=new_details2)

        update_det3 = self.update_user_info(
            token=token, data=new_details3)

        # assertions.
        self.assertStatus(update_det2, 400)
        self.assertStatus(update_det3, 400)

        self.assertIn("User with %(uname)s exists" % dict(uname=target_username),
                      update_det2.get_data(as_text=True))

        self.assertIn("User with %(email)s exists" % dict(email=target_email),
                      update_det3.get_data(as_text=True))

    @file_data("test_data/valid_userinfo.json")
    def test_logout(self, info):
        """
        Test client can logout successfully.
        """

        # register client.
        self.register_user(
            username=info[0], password=info[1], email=info[2])

        # login client.
        resp = self.login_user(username=info[0], password=info[1])

        _response = json.loads(resp.get_data(as_text=True))

        # logout user
        token = _response['auth_token']
        logout_resp = self.logout_user(token)

        # assert response, response will be ok regardless
        response = json.loads(
            logout_resp.get_data(as_text=True))

        self.assertTrue(response['status'] == 'success')

        self.assertTrue(
            response['message'] == 'Successfully logged out')

        self.assert200(logout_resp)

    @file_data("test_data/valid_userinfo.json")
    def test_cannot_use_auth_token_after_logout(self, info):
        """
        Test client cannot use auth_token after successful_logout.
        """

        # register client.
        self.register_user(username=info[0], password=info[1], email=info[2])

        # login client.
        login_response = self.login_user(username=info[0], password=info[1])

        _response = json.loads(
            login_response.get_data(as_text=True))

        # logout client.
        token = _response['auth_token']

        self.logout_user(token)

        login_response = self.get_user_details(token)
        data = json.loads(
            login_response.get_data(as_text=True))

        # assertions.
        self.assertStatus(login_response, 401)
        self.assertTrue(
            data['msg'] == 'Token has been revoked')

    @file_data("test_data/valid_userinfo.json")
    def test_token_refresh(self, info):
        """
        Test new token can be used after refresh.
        """

        # register client.
        self.register_user(username=info[0], password=info[1], email=info[2])

        # login user
        login_resp = self.login_user(username=info[0], password=info[1])
        data = json.loads(login_resp.get_data(as_text=True))
        old_auth_token = data['auth_token']

        self.assertIn('auth_token', data)
        self.assertIn('refresh_token', data)
        refresh_token = data['refresh_token']

        time.sleep(6)

        refresh_resp = self.refresh_user_token(refresh_token)
        _refresh_resp = json.loads(refresh_resp.get_data(as_text=True))
        new_auth_token = _refresh_resp['access_token']

        self.assert200(refresh_resp)

        self.assertIn('access_token', _refresh_resp)
        self.assertNotEqual(old_auth_token, new_auth_token)

        get_user_details_resp = self.get_user_details(new_auth_token)

    @file_data("test_data/valid_userinfo.json")
    def test_update_password(self, info):
        """
        Test client can update password after providing correct old password.
        """

        # register client.
        self.register_user(
            username=info[0], password=info[1], email=info[2])

        # login client.
        login_response = self.login_user(
            username=info[0], password=info[1]
        )

        # old password and new password
        old_password = info[1]
        new_password = 'mynewpassword'

        # make a post request to reset password api.
        reset_response = self.reset_password(
            username=info[0],
            email=info[2],
            old_password=old_password,
            new_password=new_password,
            confirm=new_password
        )

        # get data returned.
        reset_response_data = json.loads(reset_response.get_data(as_text=True))

        # assert reset password response
        self.assert200(reset_response)
        self.assertTrue(reset_response_data['status'] == 'success')
        self.assertTrue(reset_response_data['message'] == password_changed)

        # login client using new password to confirm reset.
        login2_response = self.login_user(
            username=info[0],
            password=new_password
        )

        login2_response_data = json.loads(login2_response.get_data(as_text=True))

        # assert login after reset
        self.assert200(login_response)
        self.assertTrue(login2_response_data['status'] == 'success')
        self.assertIn('auth_token', login2_response_data)
        self.assertIn('refresh_token', login2_response_data)

    @file_data("test_data/valid_userinfo.json")
    def test_cannot_update_password_without_username_or_email(self, info):
        """
        Test client cannot update password without username or password.
        """

        # register client.
        self.register_user(
            username=info[0], password=info[1], email=info[2])

        # login user
        login_response = self.login_user(
            username=info[0], password=info[1]
        )

        # old password and new password
        old_password = info[1]
        new_password = 'mynewpassword'

        # make a post request to reset password api.
        reset_response = self.reset_password(
            old_password=old_password,
            new_password=new_password,
            confirm=new_password
        )

        # get data returned.
        reset_response_data = json.loads(reset_response.get_data(as_text=True))

        # assert reset password response.
        self.assert401(reset_response)
        self.assertTrue(reset_response_data['status'] == 'fail')
        self.assertTrue(reset_response_data['message'] == username_or_email_required)

    @file_data("test_data/valid_userinfo.json")
    def test_can_update_password_with_username_only(self, info):
        """
        Test client can update password with username only.
        """

        # register client.
        self.register_user(
            username=info[0], password=info[1], email=info[2])

        # login client.
        login_response = self.login_user(
            username=info[0], password=info[1]
        )

        # assert status code from login response
        self.assertStatus(login_response, 200)

        # old password and new password
        old_password = info[1]
        new_password = 'mynewpassword'

        # make a post request to reset password api
        reset_response = self.reset_password(
            username=info[0],
            old_password=old_password,
            new_password=new_password,
            confirm=new_password
        )

        # get data returned
        reset_response_data = json.loads(
            reset_response.get_data(as_text=True))

        # assert reset password response
        self.assert200(reset_response)
        self.assertTrue(reset_response_data['status'] == 'success')
        self.assertTrue(reset_response_data['message'] == password_changed)

    @file_data("test_data/valid_userinfo.json")
    def test_can_update_password_with_email_only(self, info):
        """
        Test client can update password with email only.
        """

        # register client.
        self.register_user(
            username=info[0], password=info[1], email=info[2])

        # login client.
        self.login_user(
            username=info[0], password=info[1]
        )

        # old password and new password.
        old_password = info[1]
        new_password = 'mynewpassword'

        # make a post request to reset password api.
        reset_response = self.reset_password(
            email=info[2],
            old_password=old_password,
            new_password=new_password,
            confirm=new_password
        )

        # get data returned
        reset_response_data = json.loads(reset_response.get_data(as_text=True))

        # assert reset password response
        self.assert200(reset_response)
        self.assertTrue(reset_response_data['status'] == 'success')
        self.assertTrue(reset_response_data['message'] == password_changed)

    @file_data("test_data/valid_userinfo.json")
    def test_cannot_update_password_with_incorrect_old_password(self, info):
        """
        Test client cannot update password without correct old_password.
        """

        # register client.
        self.register_user(
            username=info[0], password=info[1], email=info[2])

        # login client.
        self.login_user(
            username=info[0], password=info[1]
        )

        # old password and new password.
        old_password = info[1]
        new_password = 'mynewpassword'

        # make a post request to reset password api.
        reset_response = self.reset_password(
            username=info[0],
            old_password='somerandompassword',
            new_password=new_password,
            confirm=new_password
        )

        # get data returned.
        reset_response_data = json.loads(reset_response.get_data(as_text=True))

        # assert reset password response
        self.assert401(reset_response)
        self.assertTrue(reset_response_data['status'] == 'fail')
        self.assertTrue(reset_response_data['message'] == incorrect_old_password)

    @file_data("test_data/valid_userinfo.json")
    def test_cannot_update_password_with_unmatched_passwords(self, info):
        """
        Test client cannot update password with new_password and confirm password that dont match.
        """

        # register client.
        self.register_user(
            username=info[0], password=info[1], email=info[2])

        # login client.
        self.login_user(
            username=info[0], password=info[1]
        )

        # old password and new password.
        old_password = info[1]
        new_password = 'mynewpassword'

        # make a post request to reset password api.
        reset_response = self.reset_password(
            username=info[0],
            old_password=old_password,
            new_password='somerandompassword',
            confirm=new_password
        )

        # get data returned
        reset_response_data = json.loads(reset_response.get_data(as_text=True))

        # assert reset password response
        self.assert401(reset_response)
        self.assertTrue(reset_response_data['status'] == 'fail')
        self.assertTrue(reset_response_data['message'] == passwords_donot_match)

    @file_data("test_data/valid_userinfo.json")
    def test_delete_account(self, info):
        """
        Test client can delete his/her account permanently.
        """

        # register client.
        self.register_user(username=info[0], password=info[1], email=info[2])

        # login user
        resp = self.login_user(username=info[0], password=info[1])

        data = json.loads(resp.get_data(as_text=True))

        # logout client.
        token = data['auth_token']

        # make delete request.
        delete_response = self.delete_user(token=token)

        self.assertStatus(delete_response, 204)
