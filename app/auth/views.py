# -*- coding: utf-8 -*-

"""
Application module implementing functionalities for user authentication and account management.

"""

from flask import jsonify, make_response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_raw_jwt
from flask_restful import Resource
from webargs.flaskparser import use_args
from usernames import is_safe_username

from app.core.validators import PasswordValidator, UsernameValidator
from .security import check_user, generate_token
from .utils import login_args, registration_args, reset_args, update_args, get_password_token_args
from ..messages import *
from ..models import User, BlacklistToken, ResetToken


class UserRegisterApi(Resource):
    @use_args(registration_args)
    def post(self, args):
        """
        Handle post request with user data and create user object.

        :param args: user data: username, email and password.
        :return: Response object.
        """

        username = args.get('username', '').lower()
        email = args.get('email')
        password = str(args.get('password'))
        confirm = str(args.get('confirm'))

        if not is_safe_username(username):
            return make_response(jsonify(dict(
                message=username_not_allowed
            )), 422)

        validator = UsernameValidator(username)
        validator()

        if validator.has_errors:
            return make_response(jsonify(dict(messages=dict(username=validator.errors))), 422)

        # create user instance
        user = User(username=username, password=password, email=email)

        try:
            # check if username exists.
            User.check_username(username)

        except user.UsernameExists:
            return make_response(
                jsonify(dict(
                    message=username_exists,
                )), 409)

        # check if email exists.
        try:
            User.check_email(email)

        except user.EmailExists:
            return make_response(
                jsonify(dict(
                    message=email_exists
                )), 409)

        # validate password.
        pass_validator = PasswordValidator(password)
        pass_validator()

        if pass_validator.has_errors:
            return make_response(
                jsonify(dict(messages=dict(password=pass_validator.errors))), 422)

        # check passwords
        if password != confirm:
            return make_response(
                jsonify(dict(
                    message=passwords_donot_match
                )), 400)

        # if username and email are okay call the save method.
        user.save()

        return make_response(
            jsonify(dict(
                message=account_created
            )), 201)


class UserLoginApi(Resource):
    @use_args(login_args)
    def post(self, args):
        """
        Authenticate users and generate access token for accessing protected endpoints.

        :return: response object.
        """

        username = args.get('username')
        password = args.get('password')

        user = User.get_by_username(username)

        if user is None:
            return make_response(
                jsonify(dict(
                    message=user_does_not_exist
                )), 404)

        if not user.verify_password(password):
            return make_response(
                jsonify(dict(
                    message=incorrect_password
                )), 401)

        # verify client password.
        if user.verify_password(password):
            token = create_access_token(identity=username)

            return make_response(
                jsonify(dict(
                    message=successful_login,
                    data=dict(auth_token=token)
                )), 200)


class UserProfileApi(Resource):
    """
    Provide methods to retrieve, update and delete user account.
    """

    @jwt_required
    def get(self):
        """
        Retrieve and returns user information.

        :return: response object.
        """

        # get current client identity.
        current_user = get_jwt_identity()

        user = check_user(current_user)

        return make_response(
            jsonify(dict(data=dict(
                username=user.username,
                id=user.id,
                email=user.email,
                date_joined=user.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
                updated=user.updated.strftime("%Y-%m-%d %H:%M:%S")))),
            200)

    @use_args(update_args)
    @jwt_required
    def put(self, args):
        """
        Handles PUT request to update user details.
        """

        current_user = get_jwt_identity()
        user = check_user(current_user)

        username = args.get('username', None)

        if user.username == user or not username:

            return make_response(
                jsonify(dict(
                    message=account_not_updated
                )), 200)

        validator = UsernameValidator(username)
        validator()

        if validator.has_errors:
            return make_response(
                jsonify(dict(messages=dict(username=validator.errors))), 422)

        try:
            User.check_username(username)
            user.username = username

        except user.UsernameExists:
            return make_response(
                jsonify(
                    dict(
                        message=new_username_exists % dict(username=username)
                    )),
                409)

        # if everything checks out correctly, we save the new details.
        user.username.strip()
        user.save()
        BlacklistToken(token=get_raw_jwt()['jti']).save()

        return make_response(
            jsonify(dict(
                message=account_updated,
                data=dict(
                    username=user.username,
                    email=user.email,
                    date_joined=user.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
                    updated=user.updated.strftime("%Y-%m-%d %H:%M:%S"))
            )), 200)

    @jwt_required
    def delete(self):
        """
        Handles DELETE request to remove/delete client from database.

        :return: response
        """

        current_user = get_jwt_identity()
        user = check_user(current_user)

        user.delete()

        BlacklistToken(token=get_raw_jwt()['jti']).save()

        return make_response(
            jsonify(dict(
                message=account_deleted
            )), 200
        )


class UserLogoutApi(Resource):
    """
    Resource to logout client and blacklist tokens.
    """

    @jwt_required
    def delete(self):

        jti = get_raw_jwt()['jti']
        BlacklistToken(token=jti).save()

        return make_response(
            jsonify(dict(message=logout_successful)), 200)


class PasswordResetTokenApi(Resource):
    """
    Resource class to handle client password reset.
    """

    @use_args(get_password_token_args)
    def post(self, data):
        email = data.get('email', '')

        user = User.get_by_email(email)

        if user is not None:
            rt = user.reset_tokens.filter_by(
                user_id=user.id, expired=False
            ).first()

            if rt is not None:
                rt.expire_token()

            token = generate_token(user.id)

            return make_response(
                jsonify(dict(
                    message=reset_token_sent,
                    data=dict(
                        password_reset_token=token)
                )), 200)

        return make_response(
            jsonify(dict(message=email_does_not_exist)), 409)


class PasswordResetApi(Resource):
    @use_args(reset_args)
    def post(self, data):
        """
        Handle POST requests.
        """

        errors = {}
        username = data.get('username')

        user = check_user(username)

        if not user:
            return make_response(
                jsonify(dict(message=login_again)), 403)

        new_password = data.get('new_password')
        confirm = data.get('confirm')
        reset_token = data.get('reset_token', None)

        if reset_token is '' or reset_token is None:
            errors.setdefault('reset_token', reset_token_required)
            return make_response(jsonify(dict(message=reset_token_required)), 422)

        rt = ResetToken.get_instance(reset_token, user.id)

        if rt is None:
            errors.setdefault('token', reset_token_does_not_exist)
            return make_response(
                jsonify(dict(message=errors)), 422)

        if rt.is_expired:
            return make_response(
                jsonify(dict(message=reset_token_expired)), 422)

        def change_password():
            if new_password != confirm:
                return make_response(
                    jsonify(dict(message=dict(password=passwords_donot_match))), 409)

            user.password = user.hash_password(new_password)
            rt.expire_token()
            user.save()

            return make_response(
                jsonify(dict(message=password_changed)), 200)

        return change_password()
