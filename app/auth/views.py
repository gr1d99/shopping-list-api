# -*- coding: utf-8 -*-

"""
Application module implementing functionalities for user authentication and account management.

"""

from flask import jsonify, make_response, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_raw_jwt
from email_validator import validate_email, EmailNotValidError
from flask_restful import Resource
from webargs.flaskparser import use_args
from usernames import is_safe_username

from app.core.validators import validate
from .security import check_user, generate_token
from .utils import delete_args, registration_args, reset_args, update_args
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

        # validate username and password for bad characters and formatting.
        try:
            validate(username)

        except Exception as e:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message="username value %(err)s" % dict(err=e.args[0])
                )), 422
            )

        if not is_safe_username(username):
            return make_response(jsonify(dict(
                status='fail',
                message=username_not_allowed
            )), 422)

        # validate password.
        try:
            validate(password, special=True, allow_digits=True)

        except Exception as e:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message='password value %(err)s' % dict(err=e.args[0])
                )), 422)

        # check passwords
        if password != confirm:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=passwords_donot_match
                )), 400)

        # create user instance
        user = User(username=username, password=password, email=email)

        try:
            # check if username exists.
            User.check_username(username)

        except user.UsernameExists:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=username_exists,
                )), 409)

        # check if email exists.
        try:
            User.check_email(email)

        except user.EmailExists:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=email_exists
                )), 409)

        # if username and email are okay call the save method.
        user.save()

        return make_response(
            jsonify(dict(
                status='success',
                message=account_created
            )), 201)


class UserLoginApi(Resource):
    def post(self):
        """
        Authenticate users and generate access token for accessing protected endpoints.

        :return: response object.
        """
        if not request.authorization:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=credentials_required
                )), 401)

        credentials = request.authorization

        username = credentials.get('username')
        password = credentials.get('password')

        user = User.get_by_username(username)

        if user is None:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=user_does_not_exist
                )), 401)

        if not user.verify_password(password):
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=incorrect_password
                )), 401)

        # verify client password.
        if user.verify_password(password):
            token = create_access_token(identity=username)

            return make_response(
                jsonify(dict(
                    status='success',
                    message=successful_login,
                    data=dict(auth_token=token)
                )), 200)


class UserProfileApi(Resource):
    """
    Provide methods to retrieve, update and delete user accounts.
    """

    @jwt_required
    def get(self):
        """
        Retrieve and returns user information to client.

        :return: response object.
        """

        # get current client identity.
        current_user = get_jwt_identity()

        user = check_user(current_user)

        if not user:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=login_again
                )), 401)

        return make_response(
            jsonify(dict(status='success',
                         data=dict(
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

        if not user:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=login_again
                )), 401)

        email = args.get('email', None)

        if user.email == email or not email:

            return make_response(
                jsonify(dict(
                    status='success',
                    message=account_not_updated
                )), 200)

        try:
            validate_email(email)

        except EmailNotValidError as e:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=e.args
                )), 422
            )

        try:
            User.check_email(email)
            user.email = email

        except user.EmailExists:
            return make_response(
                jsonify(
                    dict(
                        status='fail',
                        message=new_email_exists % dict(email=email)
                    )),
                409)

        # if everything checks out correctly, we save the new details.
        user.save()

        return make_response(
            jsonify(dict(
                status='success',
                message=account_updated,
                data=dict(
                    username=user.username,
                    email=user.email,
                    date_joined=user.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
                    updated=user.updated.strftime("%Y-%m-%d %H:%M:%S"))
            )), 200)

    @use_args(delete_args)
    @jwt_required
    def delete(self, data):
        """
        Handles DELETE request to remove/delete client from database.

        :return: response
        """

        current_user = get_jwt_identity()
        user = check_user(current_user)
        password = data.get('password')

        if not user:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=login_again
                )), 401)

        if not user.verify_password(password):
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=incomplete_delete
                )), 409
            )

        user.delete()

        BlacklistToken(token=get_raw_jwt()['jti']).save()

        return make_response(
            jsonify(dict(
                status='success',
                message=account_deleted
            )), 200
        )


class UserLogoutApi(Resource):
    """
    Resource to logout client and blacklist tokens.
    """

    @jwt_required
    def delete(self):
        current_user = get_jwt_identity()
        user = check_user(current_user)

        if not user:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=login_again
                )), 401)

        jti = get_raw_jwt()['jti']
        BlacklistToken(token=jti).save()

        return make_response(
            jsonify(
                dict(status='success',
                     message=logout_successful)),
            200)


class PasswordResetTokenApi(Resource):
    """
    Resource class to handle client password reset.
    """

    @use_args(update_args)
    def post(self, data):
        email = data.get('email', '')

        try:
            validate_email(email)

        except EmailNotValidError as e:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=e.args
                )), 422)

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
                    status='success',
                    message=reset_token_sent,
                    data=dict(
                        password_reset_token=token)
                )), 200)

        return make_response(
            jsonify(dict(
                status='fail',
                message=email_does_not_exist
            )), 409)


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
                jsonify(dict(
                    status='fail',
                    message=login_again
                )), 401)

        new_password = data.get('new_password')
        confirm = data.get('confirm')
        reset_token = data.get('reset_token', None)

        if reset_token is '' or reset_token is None:
            errors.setdefault('reset_token', reset_token_required)
            return make_response(jsonify(dict(
                status='fail',
                message=reset_token_required
            )), 422)

        rt = ResetToken.get_instance(reset_token, user.id)

        if rt is None:
            errors.setdefault('token', reset_token_does_not_exist)
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=errors
                )), 422
            )

        if rt.is_expired:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=reset_token_expired
                )), 422
            )

        def change_password():
            if new_password != confirm:
                return make_response(
                    jsonify(dict(
                        status='fail',
                        message=dict(password=passwords_donot_match)
                    )), 401)

            user.password = user.hash_password(new_password)
            rt.expire_token()
            user.save()

            return make_response(
                jsonify(dict(
                    status='success',
                    message=password_changed
                )), 200
            )

        return change_password()
