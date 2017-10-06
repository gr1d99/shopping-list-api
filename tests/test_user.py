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

        self.gideon_data = {'username': 'giddy',
                            'pass': 'gideonpassword',
                            'email': 'giddy@gmail.com'}

        self.gideon = self.user(username=self.gideon_data.get('username'),
                                email=self.gideon_data.get('email'),
                                password=self.gideon_data.get('pass'))

    def test_user_username(self):
        """
        assert whether the user created has the same username as `gideon`
        """
        self.db.session.add(self.gideon)  # issue an INSERT statement
        self.db.session.commit()  # commit
        added_user = self.user.query.filter_by(username=self.gideon_data.get('username')).\
            first().username  # retrieve the username itself

        self.assertEqual(added_user, self.gideon_data.get('username'))

    def test_user_email(self):
        """
        Assert if user created has the expected email
        """
        self.db.session.add(self.gideon)
        self.db.session.commit()
        gideon_email = self.user.query.filter_by(
            email=self.gideon_data.get('email')
        ).first().email
        self.assertEqual(gideon_email, self.gideon_data.get('email'))

    def test_user_password(self):
        """
        Assert if the user created has the expected password
        """
        self.db.session.add(self.gideon)
        self.db.session.commit()
        gideon_password = self.user.query.filter_by(
            username=self.gideon_data.get('username')
        ).first().password
        self.assertEqual(gideon_password, self.gideon_data.get('pass'))

    def tearDown(self):
        """
        Called every time a test method is run
        """
        self.db.session.remove()
        self.db.drop_all()
