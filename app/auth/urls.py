import collections

from flask import Blueprint

from app import API

auth_blueprint = Blueprint('auth', __name__)


from .views import (RefreshTokenApi, ResetPasswordApi, UserRegisterApi,
                    UserLoginApi, UserLogoutApi, UserProfileApi)

url = collections.namedtuple('url', ['route', 'resource'])

auth_urls = [
    url('auth/users', UserProfileApi),
    url('auth/register', UserRegisterApi),
    url('auth/login', UserLoginApi),
    url('auth/logout', UserLogoutApi),
    url('auth/refresh-token', RefreshTokenApi),
    url('auth/reset-password', ResetPasswordApi),
]


for url in auth_urls:
    API.add_resource(url.resource, url.route)