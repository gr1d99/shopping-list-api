from collections import OrderedDict

from flask import jsonify, make_response, request
from flask_restful import Resource
from webargs import fields, validate
from webargs.flaskparser import use_args

from app.messages \
    import (username_exists, email_exists, account_created)
from app.models import User

auth_args = {
    'user_id': fields.Str(required=True)
}

registration_args = OrderedDict(
    [
        ('username', fields.Str(required=True)),
        ('email', fields.Str(message='Email required', required=True, validate=validate.Email())),
        ('password', fields.Str(required=True, validate=validate.Length(min=6)))
    ]
)

login_args = OrderedDict(
    [
        ('username', fields.Str(required=True)),
        ('password', fields.Str(required=True))
    ]
)


# TODO comp 220 OS MISSING, Interchanged INTE 223 and Comp 326, INTE 226 MISSING SAD, INTE 314

class UserRegisterApi(Resource):
    @use_args(registration_args)
    def post(self, data):
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        user = User(username=username, password=password, email=email)

        try:
            user.check_username()

        except user.UsernameExists:
            return make_response(
                jsonify(dict(message=username_exists)), 400)

        try:
            user.check_email()

        except user.EmailExists:
            return make_response(
                jsonify(dict(message=email_exists)), 400)

        user.save()

        return make_response(
            jsonify(dict(message=account_created)), 201)


class UserLoginApi(Resource):
    @use_args(login_args)
    def post(self, data):
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if user is None:
            return make_response(
                jsonify(dict(message='Incorrect username or password!!')), 401
            )

        if user.is_authenticated:
            return make_response(
                jsonify(dict(message='Already logged in')), 200)

        if user.verify_password(password):
            user.authenticate()
            return make_response(
                jsonify(dict(message='Logged in')), 200
            )


class AuthApi(Resource):
    @use_args(auth_args)
    def post(self, data):
        user_id = data.get('user_id')

        user = User.query.filter_by(username=user_id).first()

        if not user:
            return make_response(
                jsonify(dict(message='Please login or sign up first')), 401
            )

        if user and not user.is_authenticated:
            return make_response(
                jsonify(dict(message='Please login')), 401
            )

        return make_response(
            jsonify(dict(
                username=user.username,
                email=user.email,
                date_joined=user.date_joined
            )), 200
        )

    @use_args(auth_args)
    def put(self, user_id):
        user_id = user_id.get('user_id')
        user = User.query.filter_by(username=user_id).first()

        if not user:
            return make_response(
                jsonify(dict(message="Create account or login")), 401)

        if user and not user.is_authenticated:
            return make_response(
                jsonify(dict(
                    message='Login first'
                )), 401)

        if user and user.is_authenticated:
            username = request.json.get('username')
            email = request.json.get('email')
            password = request.json.get('password')

            if User.query.filter_by(username=username).first():
                return make_response(
                    jsonify(
                        dict(message="User with %(uname)s exists" % dict(uname=username))),
                    400)

            if User.query.filter_by(email=email).first():
                return make_response(
                    jsonify(
                        dict(message="User with %(email)s exists" % dict(email=email))),
                    400)

            if username != user.username:
                user.username = username

            if email != user.email:
                user.email = email

            if not user.verify_password(password):
                user.password = bytes(password.encode('utf-8'))  # to bytes

            user.save()
            return make_response(
                jsonify(dict(message="Account updated")), 200)


class UserLogoutApi(Resource):
    @use_args(auth_args)
    def post(self, data):
        user_id = data.get('user_id')
        if user_id:
            user = User.query.filter_by(username=user_id).first()
            if user and user.is_authenticated:
                user.deauthenticate()
                user.save()

        return make_response(
            jsonify(dict(message="Logged out")), 200)
