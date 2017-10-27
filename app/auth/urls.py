import collections

from .views import RefreshTokenApi, UserRegisterApi, UserLoginApi, UserLogoutApi, UserProfileApi

url = collections.namedtuple('url', ['route', 'resource'])

urls = [
    url('auth/users', UserProfileApi),
    url('auth/register', UserRegisterApi),
    url('auth/login', UserLoginApi),
    url('auth/logout', UserLogoutApi),
    url('auth/refresh-token', RefreshTokenApi),
]