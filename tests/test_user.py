# -*- coding: utf-8 -*-

"""Contains all Tests for system app user"""

import unittest
import main
from web_app.conf import app_config
from web_app.db.models import User


class TestUser(unittest.TestCase):
    """tests main User model class"""

    def setUp(self):
        """
        Create instances and objects that will be used by the tests
        """
        app = main.app  # use the created app instead of creating a new one
        app.config['SQLALCHEMY_DATABASE_URI'] = app_config.\
            TestingConfig.SQLALCHEMY_DATABASE_URI  # database to use
        app.config['TESTING'] = app_config.TestingConfig.TESTING
        db = main.db
        db.init_app(app)
        # --------------------------------------------#
        db.session.commit()   # ----------------------#
        db.drop_all()         # credits: Mbithe Nzomo #
        db.create_all()       # ----------------------#
        # --------------------------------------------#
        self.app = app
        self.db = db
        self.user = User

    def test_user_creation(self):
        """
        create user named `gideon` and assert whether the user created
        has the same username as `gideon`
        """
        username = 'gideon'  # set username to be used during assertion
        user = self.user(username=username)
        self.db.session.add(user)  # issue an INSERT statement
        self.db.session.commit()  # commit
        added_user = self.user.query.filter_by(username=username).\
            first().username  # retrieve the username itself

        self.assertEqual(added_user, username)

    def tearDown(self):
        """
        Called every time a test method is run
        """
        self.db.session.remove()
        self.db.drop_all()
