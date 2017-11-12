"""Base class for all tests"""

import collections

from flask_testing import TestCase
from . import APP, DB, User, app_config


class TestBase(TestCase):
    def create_app(self):
        return APP

    def __init__(self, *args, **kwargs):
        super(TestBase, self).__init__(*args, **kwargs)
        self.user = None
        self.user_info = None
        self._info = None

    def setUp(self):
        self.app.config.from_object(app_config.TestingConfig)
        DB.init_app(self.app)

        DB.session.commit()
        DB.drop_all()
        DB.create_all()

        _info = collections.namedtuple('User', ['username', 'email', 'password'])
        user_info = _info('giddy', 'giddy@email.com', 'gideonpassword')

        self.user = User(username=user_info.username,
                         email=user_info.email,
                         password=user_info.password)
        self.user_info = user_info
        self._info = _info

    def tearDown(self):
        DB.session.remove()
        DB.drop_all()
