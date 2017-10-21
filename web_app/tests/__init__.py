from main import API, APP, DB
from web_app.conf import app_config
from web_app.db.utils.messages import account_created
from web_app.db.models import User

CONTENT_TYPE = 'application/json'
BASE_PREFIX = API.prefix

LOGIN_PREFIX = "auth/login"
LOGOUT_PREFIX = "auth/logout"
REGISTER_PREFIX = "auth/register"
USER_DETAILS_PREFIX = "auth"
UPDATE_USER_DETAILS_PREFIX = "auth"

LOGIN_URL = "%(prefix)s%(next)s" % dict(prefix=BASE_PREFIX, next=LOGIN_PREFIX)
LOGOUT_URL = "%(prefix)s%(next)s" % dict(prefix=BASE_PREFIX, next=LOGOUT_PREFIX)
REGISTER_URL = "%(prefix)s%(next)s" % dict(prefix=BASE_PREFIX, next=REGISTER_PREFIX)
USER_DETAILS_URL = "%(prefix)s%(next)s" % dict(prefix=BASE_PREFIX, next=USER_DETAILS_PREFIX)
UPDATE_USER_DETAILS_URL = "%(prefix)s%(next)s" % dict(prefix=BASE_PREFIX, next=UPDATE_USER_DETAILS_PREFIX)

INVALID_EMAIL_ERR = "Not a valid email address."
REQUIRED_FIELDS_ERR = "Missing data for required field."


__all__ = [
    APP, account_created, app_config,
    CONTENT_TYPE, DB, INVALID_EMAIL_ERR, LOGIN_URL, LOGOUT_URL, REGISTER_URL,
    REQUIRED_FIELDS_ERR, User, UPDATE_USER_DETAILS_URL, USER_DETAILS_URL,
]