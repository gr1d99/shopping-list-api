# -*- coding: utf-8 -*-

"""
App module containing client authentication and account management resources.
"""

from flask import jsonify, make_response, request
from flask_jwt_extended import \
    (create_access_token, jwt_required, get_jwt_identity, get_raw_jwt)
from flask_restful import Resource
from webargs.flaskparser import use_args
from usernames import is_safe_username

from app.core.validators import CustomValidator
from .security import check_user
from .utils import (delete_account_args, registration_args, reset_password_args,
                    update_account_args, send_reset_token)
from ..messages import *
from ..models import User, BlacklistToken, ResetToken


class UserRegisterApi(Resource):
    """
    A resource to handle client registration.

    Only accepts POST request.
    """
    @use_args(registration_args)
    def post(self, data):
        """
        Handle post request.
        :param data: username, email, password
        """

        username = data.get('username').lower()
        email = data.get('email')
        password = str(data.get('password'))
        confirm = str(data.get('confirm'))

        # validate username and password for bad characters and formatting.
        try:
            CustomValidator(username).validate()

        except Exception as e:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message="username value %(err)s" % dict(err=e.args[0])
                )), 422
            )

        try:
            CustomValidator(password).validate()

        except Exception as e:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message='password value %(err)s' % dict(err=e.args[0])
                )), 422
            )

        if not is_safe_username(username):
            return make_response(jsonify(dict(
                status='fail',
                message=username_not_allowed
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

        try:
            # check if email exists.
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
    """
    A resource to handle client login.

    Only accepts post requests.
    """

    def post(self):
        """
        Handle POST request.
        :param data: username and password.
        """
        if not request.authorization:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=cridentials_required
                )), 401)

        cridentials = request.authorization

        username = cridentials.get('username')
        password = cridentials.get('password')

        user = User.get_user(username)

        if user is None:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=user_does_not_exist
                )), 401
            )

        if not user.verify_password(password):
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=incorrect_password
                )), 401
            )

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
    A resource to handle retrieval and updating of client account.
    """

    @jwt_required
    def get(self):
        """
        A method to handle get request.
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
                             updated=user.updated.strftime("%Y-%m-%d %H:%M:%S"))
                         )), 200)

    @use_args(update_account_args)
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

        new_username = args.get('username')
        email = args.get('email')

        if any([new_username, email]):

            # use if else statement to check if client
            # has provided any data. if not we will
            # not return any errors, instead we will
            # not make any update.
            if new_username:

                # check if username is not equal to the current one used
                # by the user.
                if user.username != new_username:

                    try:
                        # check if there exists a user with the username
                        # provided by the user.
                        User.check_username(new_username)
                        user.username = new_username

                    except user.UsernameExists:
                        # return a response informing the user of the conflict.
                        return make_response(
                            jsonify(
                                dict(
                                    status='fail',
                                    message=new_username_exists % dict(username=new_username)
                                )),
                            409)

            if email:
                # check if supplied email is not equal to current email
                # used by the user.
                if user.email != email:

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

            BlacklistToken(token=get_raw_jwt()['jti']).save()

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

        else:
            return make_response(
                jsonify(dict(
                    status='success',
                    message=account_not_updated
                )), 200)

    @use_args(delete_account_args)
    @jwt_required
    def delete(self, data):
        """
        Handles DELETE request to remove/delete client from database.
        :return: response
        """

        current_user = get_jwt_identity()
        user = check_user(current_user)
        confirm = data.get('confirm')

        if not user:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=login_again
                )), 401)

        if not confirm:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=incomplete_delete
                )), 422
            )
        user.delete()

        BlacklistToken(token=get_raw_jwt()['jti']).save()

        # return 204 response with nothing
        return {}, 204


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
                     message=logout_successful
                     )), 200)


class ResetPasswordApi(Resource):
    """
    Resource class to handle client password reset.
    """

    @jwt_required
    def get(self):
        current_user = get_jwt_identity()
        user = check_user(current_user)

        if not user:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=login_again
                )), 401)

        if user is not None:
            user = User.get_user(current_user)
            rt = user.reset_tokens.filter_by(
                user_id=user.id, expired=False
            ).first()

            if rt is not None:
                rt.expire_token()

            token = send_reset_token(user.id)
            return make_response(
                jsonify(dict(
                    status='success',
                    message=reset_token_sent,
                    data=dict(
                        password_reset_token=token
                    )
                )), 200
            )

    @use_args(reset_password_args)
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

        rt = user.reset_tokens.filter_by(
            user_id=user.id, token=reset_token
        ).first()

        # check if token is expired.
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
                    message=dict(token=reset_token_expired)
                )), 422
            )

        def change_password():
            if new_password != confirm:
                return make_response(
                    jsonify(dict(
                        status='fail',
                        message=dict(password=passwords_donot_match)
                    )), 401
                )

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
