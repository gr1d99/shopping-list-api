from flask import jsonify, make_response, request
from flask_jwt_extended import \
    (create_access_token, jwt_required, get_jwt_identity,
     create_refresh_token, jwt_refresh_token_required, get_raw_jwt)
from flask_restful import Resource
from webargs.flaskparser import use_args

from ..messages \
    import (username_exists, email_exists, account_created, incorrect_password_or_username,
            incorrect_old_password, passwords_donot_match, password_changed,
            username_or_email_required)
from ..models import User, BlacklistToken
from .utils import login_args, registration_args, reset_password_args


class UserRegisterApi(Resource):
    """
    A resource to handle user registration.

    Only accepts POST request.
    """
    @use_args(registration_args)
    def post(self, data):
        """
        Handle post request.
        :param data: username, email, password
        """

        username = data.get('username')
        email = data.get('email')
        password = str(data.get('password'))

        try:

            # create user instance
            user = User(username=username, password=password, email=email)

            try:
                # check if username exists.
                User.check_username(username)

            except user.UsernameExists:
                return make_response(
                    jsonify(dict(
                        message=username_exists,
                        status='fail'
                    )), 202)

            try:
                # check if email exists.
                User.check_email(email)

            except user.EmailExists:
                return make_response(
                    jsonify(dict(
                        message=email_exists,
                        status='fail'
                    )), 202)

            # if username and email are okey call the save method.
            user.save()

            return make_response(
                jsonify(dict(
                    message=account_created,
                    status='success'
                )), 201)

        except Exception as e:
            return make_response(
                jsonify(dict(status='fail', message=e)), 500
            )


class UserLoginApi(Resource):
    """
    A resource to handle user login.

    Only accepts post requests
    """

    @use_args(login_args)
    def post(self, data):
        """
        Handle POST request.
        :param data: username and password
        """
        username = data.get('username')
        password = str(data.get('password'))

        try:
            user = User.query.filter_by(username=username).first()

            if user is None or not user.verify_password(password):
                return make_response(
                    jsonify(dict(
                        message=incorrect_password_or_username,
                        status='fail'
                    )), 401
                )

            if user.verify_password(password):
                token = create_access_token(identity=username)
                refresh_token = create_refresh_token(identity=username)

                return make_response(
                    jsonify(dict(
                        message='Logged in',
                        status='success',
                        auth_token=token,
                        refresh_token=refresh_token
                    )), 200)

        except Exception as e:
            return make_response(
                jsonify(dict(status='fail', message=e)), 500
            )


class UserProfileApi(Resource):
    """
    A resource to handle retrieval and updating of user account.
    """
    @jwt_required
    def get(self):
        """
        A method to handle get request.
        """

        # get current user identity
        current_user = get_jwt_identity()

        # if current user exists query details and send response back
        # to client.
        if current_user:
            user = User.query.filter_by(username=current_user).first()

            return make_response(
                jsonify(dict(status='success',
                             data=dict(username=user.username,
                                       email=user.email,
                                       date_joined=user.date_joined)
                             )), 200
            )

    @jwt_required
    def put(self):
        """
        Handles PUT request to update user details.
        """
        try:
            current_user = get_jwt_identity()
            if current_user:
                # query user
                user = User.query.filter_by(username=current_user).first()

                if user:
                    new_username = request.json.get('username', None)
                    email = request.json.get('email', None)
                    password = request.json.get('password', None)

                    # use if else statement to check if user
                    # has provided any data. if not we will
                    # not return any errors, instead we will
                    # not make any update.
                    if not new_username:
                        new_username = user.username

                    if not email:
                        email = user.email

                    # check if username is not equal to the current one used
                    # by the user.
                    if user.username != new_username:

                        try:
                            # check if there exists a user with the username
                            # provided by the user.
                            User.check_username(new_username)

                        except user.UsernameExists:
                            # return a response informing the user of the conflict.
                            return make_response(
                                jsonify(
                                    dict(
                                        message="User with %(uname)s exists" % dict(uname=new_username),
                                        status='fail'
                                    )),
                                400)

                    # check if supplied email is not equal to current email
                    # used by the user.
                    if user.email != email:

                        try:
                            User.check_email(email)

                        except user.EmailExists:
                            return make_response(
                                jsonify(
                                    dict(
                                        message="User with %(email)s exists" % dict(email=email),
                                        status='fail'
                                    )),
                                400)

                    if new_username != user.username:
                        user.username = new_username

                    if email != user.email:
                        user.email = email

                    # if everything checks out correctly, we save the new details.
                    user.save()

                    BlacklistToken(token=get_raw_jwt()['jti']).save()

                    return make_response(
                        jsonify(dict(
                            message="Account updated",
                            data=dict(
                                username=user.username,
                                email=user.email,
                                date_joined=user.date_joined),
                            status='success'
                        )), 200)

                return make_response(
                    jsonify(dict(
                        message='login again',
                        status='fail'
                    )), 400
                )

        except Exception as e:
            print(e)
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=e
                )), 500
            )


class UserLogoutApi(Resource):
    """
    Resource to logout users and blacklist tokens.
    """
    @jwt_required
    def delete(self):
        """
        Make delete request.
        """
        jti = get_raw_jwt()['jti']
        BlacklistToken(token=jti).save()

        return make_response(
            jsonify(
                dict(status='success',
                     message="Successfully logged out"
                     )), 200)


class ResetPasswordApi(Resource):
    """
    Resource class to handle client password reset.
    """

    @use_args(reset_password_args)
    def post(self, data):
        """
        Handle POST requests.
        """

        username = data.get('username', None)
        email = data.get('email', None)
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        confirm = data.get('confirm')

        # set user instance to None initially because the user
        # will provide either a username or email used to get
        # user instance if it exists.
        user = None

        if username and email:
            user = User.query.filter_by(username=username).first()

        elif username and not email:
            user = User.query.filter_by(username=username).first()

        elif not username and email:
            user = User.query.filter_by(email=email).first()

        else:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=username_or_email_required
                )), 401
            )

        if not user.verify_password(old_password):
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=incorrect_old_password
                )), 401
            )

        if new_password != confirm:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=passwords_donot_match
                )), 401
            )

        user.password = user.hash_password(new_password)
        user.save()

        return make_response(
            jsonify(dict(
                status='success',
                message=password_changed
            )), 200
        )


class RefreshTokenApi(Resource):
    """
    Used to refresh user authentication tokens.
    """
    @jwt_refresh_token_required
    def post(self):
        """
        Handle post requests to refresh authentication tokens.
        :return: new_token
        """

        # gets identity of the user identified by the token.
        current_user = get_jwt_identity()
        return make_response(
            jsonify(dict(
                access_token=create_refresh_token(identity=current_user)
            )), 200
        )
