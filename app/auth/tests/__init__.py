from app.conf import app_config
from app.messages import account_created, password_changed
from app.models import User
from app import API, APP, DB

CONTENT_TYPE = 'application/json'
BASE_PREFIX = API.prefix

LOGIN_PREFIX = "auth/login"
LOGOUT_PREFIX = "auth/logout"
REGISTER_PREFIX = "auth/register"
RESET_PASSWORD_PREFIX = "auth/reset-password"
USER_DETAILS_PREFIX = "auth/users"
UPDATE_USER_DETAILS_PREFIX = "auth/users"
REFRESH_TOKEN_PREFIX = "auth/refresh-token"

LOGIN_URL = "%(prefix)s%(next)s" % dict(prefix=BASE_PREFIX, next=LOGIN_PREFIX)
LOGOUT_URL = "%(prefix)s%(next)s" % dict(prefix=BASE_PREFIX, next=LOGOUT_PREFIX)
REGISTER_URL = "%(prefix)s%(next)s" % dict(prefix=BASE_PREFIX, next=REGISTER_PREFIX)
RESET_PASSWORD_URL = "%(prefix)s%(next)s" % dict(prefix=BASE_PREFIX, next=RESET_PASSWORD_PREFIX)
USER_DETAILS_URL = "%(prefix)s%(next)s" % dict(prefix=BASE_PREFIX, next=USER_DETAILS_PREFIX)
UPDATE_USER_DETAILS_URL = "%(prefix)s%(next)s" % dict(prefix=BASE_PREFIX, next=UPDATE_USER_DETAILS_PREFIX)
REFRESH_USER_TOKEN_URL = "%(prefix)s%(next)s" % dict(prefix=BASE_PREFIX, next=REFRESH_TOKEN_PREFIX)

INVALID_EMAIL_ERR = "Not a valid email address."
REQUIRED_FIELDS_ERR = "Missing data for required field."


__all__ = [
    APP, account_created, app_config, password_changed,
    CONTENT_TYPE, DB, INVALID_EMAIL_ERR, LOGIN_URL, LOGOUT_URL,
    REFRESH_USER_TOKEN_URL, REGISTER_URL, RESET_PASSWORD_URL, REQUIRED_FIELDS_ERR,
    User, UPDATE_USER_DETAILS_URL, USER_DETAILS_URL,
]
