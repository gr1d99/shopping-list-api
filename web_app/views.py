from flask import jsonify, make_response, request
from flask_restful import Resource
from main import auth
from web_app.db.models import User
from web_app.db.utils.messages \
    import (username_not_provided, email_not_provided, password_not_provided,
            username_exists, email_exists, account_created)


@auth.verify_password
def verify(username, password):
    if not username or not password:
        return False

    user = User.query.filter_by(username=username).first()

    if user is None:
        return False

    return user.verify_password(password)


class UserRegisterApi(Resource):
    def post(self):
        username = request.json.get('username')
        email = request.json.get('email')
        password = request.json.get('password')

        if not username:
            return make_response(
                jsonify(dict(message=username_not_provided)), 400)

        if not email:
            return make_response(
                jsonify(dict(message=email_not_provided)), 400)

        if not password:
            return make_response(
                jsonify(dict(message=password_not_provided)), 400)

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
    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')

        if not username:
            return make_response(
                jsonify(dict(message=username_not_provided)), 400)

        if not password:
            return make_response(
                jsonify(dict(message=password_not_provided)), 400)

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
    @auth.login_required
    def get(self, username_id):
        if not username_id:
            return make_response(
                jsonify(dict(message='Provide a username')), 400
            )

        user = User.query.filter_by(username=username_id).first()

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

    @auth.login_required
    def put(self, username_id):
        user = User.query.filter_by(username=username_id).first()

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

            if not user.verify_password(str(password)):
                user.password = str(password)

            user.save()
            return make_response(
                jsonify(
                    dict(message="Account updated")),
                200)
