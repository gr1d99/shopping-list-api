from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import \
    (create_access_token, fresh_jwt_required, jwt_required, get_jwt_claims, get_jwt_identity,
     create_refresh_token, jwt_refresh_token_required, get_raw_jwt)
from flask_restful import Resource
from webargs.flaskparser import use_args

from ..messages \
    import (username_exists, email_exists, account_created)
from ..models import User, BlacklistToken
from .utils import login_args, registration_args


class UserRegisterApi(Resource):
    @use_args(registration_args)
    def post(self, data):
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        try:

            user = User(username=username, password=password, email=email)

            try:
                User.check_username(username)

            except user.UsernameExists:
                return make_response(
                    jsonify(dict(
                        message=username_exists,
                        status='fail'
                    )), 202)

            try:
                User.check_email(email)

            except user.EmailExists:
                return make_response(
                    jsonify(dict(
                        message=email_exists,
                        status='fail'
                    )), 202)

            user.save()
            token = create_access_token(identity=user.username)
            refresh_token = create_refresh_token(identity=user.username)

            return make_response(
                jsonify(dict(
                    message=account_created,
                    auth_token=token,
                    refresh_token=refresh_token,
                    status='success'
                )), 201)

        except Exception as e:
            return make_response(
                jsonify(dict(status='fail', message=e)), 500
            )


class UserLoginApi(Resource):
    @use_args(login_args)
    def post(self, data):
        username = data.get('username')
        password = data.get('password')

        try:
            user = User.query.filter_by(username=username).first()

            if user is None:
                return make_response(
                    jsonify(dict(
                        message='Incorrect username or password!!',
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


class RefreshTokenApi(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        return make_response(
            jsonify(dict(
                auth_token=create_refresh_token(identity=current_user)
            )), 200
        )


class UserProfileApi(Resource):
    @jwt_required
    def get(self):
        current_user = get_jwt_identity()
        if current_user:
            user = User.query.filter_by(username=current_user).first()
            claims = get_jwt_claims()
            return make_response(
                jsonify(dict(
                    status='success',
                    data=dict(
                        username=user.username,
                        email=user.email,
                        date_joined=user.date_joined
                    )
                ))
            )

    @jwt_required
    def put(self):
        try:
            current_user = get_jwt_identity()
            if current_user:
                user = User.query.filter_by(username=current_user).first()

                if user:
                    new_username = request.json.get('username')
                    email = request.json.get('email')
                    password = request.json.get('password')

                    if not new_username:
                        new_username = user.username

                    if not email:
                        email = user.email

                    if not password:
                        password = user.password

                    if user.username != new_username:

                        try:
                            User.check_username(new_username)

                        except user.UsernameExists:
                            return make_response(
                                jsonify(
                                    dict(
                                        message="User with %(uname)s exists" % dict(uname=new_username),
                                        status='fail'
                                    )),
                                400)

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

                    print(user.verify_password(password))
                    if not user.verify_password(password):
                        user.password = password.encode('utf-8')  # to bytes

                    user.save()
                    return make_response(
                        jsonify(dict(
                            message="Account updated",
                            data=dict(
                                username=user.username,
                                email=user.email,
                                date_joined=user.date_joined),
                            status='success'
                        )), 200)

        except Exception as e:
            return make_response(
                jsonify(dict(
                    status='fail',
                    message=e
                )), 500
            )


class UserLogoutApi(Resource):
    @jwt_required
    def delete(self):
        jti = get_raw_jwt()['jti']
        BlacklistToken(token=jti).save()

        return make_response(
            jsonify(
                dict(status='success',
                     message="Successfully logged out"
                     )), 200)
