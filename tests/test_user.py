# -*- coding: utf-8 -*-

"""Contains all Tests for system app user"""

import unittest
from main import app
from web_app.conf import app_config
from web_app.db.models import User


class TestUser(unittest.TestCase):
    """tests main User model class"""

    def setUp(self):
        app.config.from_object(app_config.TestingConfig)
        self.user = User

    def test_user_create(self):
        """
        test if a user is created successfully
        """
        self.user(username='gideon',
                  password='gideonpassword',
                  email='gideonkimutai9@gmail.com')
