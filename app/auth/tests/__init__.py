from app.conf import app_config
from app.messages import (account_created, password_changed, incorrect_old_password, passwords_donot_match,
                          incorrect_password_or_username, username_or_email_required)
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
