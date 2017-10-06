# -*- coding: utf-8 -*-

"""Contains all Tests for system app user"""

import unittest
from main import app, db, bcrypt
from web_app.conf import app_config
from web_app.db.models import User


class TestUserBase(unittest.TestCase):
    def setUp(self):
        """Create instances and objects that will be used by the tests"""
        app.config['SQLALCHEMY_DATABASE_URI'] = app_config.\
            TestingConfig.SQLALCHEMY_DATABASE_URI  # database to use
        app.config['TESTING'] = app_config.TestingConfig.TESTING
        app.config['DEBUG'] = False
        db.init_app(app)
        # --------------------------------------------#
        db.session.commit()   # ----------------------#
        db.drop_all()         # credits: Mbithe Nzomo #
        db.create_all()       # ----------------------#
        # --------------------------------------------#

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class TestUserModel(TestUserBase):
    """tests main User model class"""

    def setUp(self):
        super(TestUserModel, self).setUp()  # call the super class setUp method
        self.user_raw_password = 'gideonpassword'
        user_hashed_password = bcrypt. \
            generate_password_hash(self.user_raw_password)  # hash user password
        self.gideon_data = {'username': 'giddy',
                            'pass': user_hashed_password,
                            'email': 'giddy@gmail.com'}

        self.gideon = User(username=self.gideon_data.get('username'),
                           email=self.gideon_data.get('email'),
                           password=self.gideon_data.get('pass'))

    def test_user_username(self):
        """
        assert whether the user created has the same username as `gideon`
        """
        db.session.add(self.gideon)  # issue an INSERT statement
        db.session.commit()  # commit
        added_user = User.query.filter_by(username=self.gideon_data.get('username')).\
            first().username  # retrieve the username itself

        self.assertEqual(added_user, self.gideon_data.get('username'))

    def test_user_email(self):
        """
        Assert if user created has the expected email
        """
        db.session.add(self.gideon)
        db.session.commit()
        gideon_email = User.query.filter_by(
            email=self.gideon_data.get('email')
        ).first().email
        self.assertEqual(gideon_email, self.gideon_data.get('email'))

    def test_user_password(self):
        """
        Assert if the user created has the expected password
        """
        db.session.add(self.gideon)
        db.session.commit()
        gideon_password = User.query.filter_by(
            username=self.gideon_data.get('username')
        ).first().password  # query `gideon` details and get the password
        self.assertTrue(bcrypt.check_password_hash(gideon_password, self.user_raw_password))


class TestUserRegisterAndLogin(TestUserBase):
    """test user registration and login"""
    def setUp(self):
        super(TestUserRegisterAndLogin, self).setUp()
        self.client = app.test_client()
        self.user_register_data = {
            'username': 'gideon',
            'password': 'gideonpassword',
            'email': 'gideon@email.com'
        }
        self.api_register_url = '/shopping-list/api/v1/auth/register/'
        self.api_login_url = '/shopping-list/api/v1/auth/login/'

    def test_user_registration(self):
        """
        test if response code is 404
            `we currently don't have an endpoint to handle registration`
        """
        response = self.client.post(self.api_register_url,
                                    data=self.user_register_data)
        self.assertEqual(response.status_code, 404)

    def test_user_login(self):
        """
        test is response code is 404
            `there is no api endpoint to handle user login as of yet`
        """
        login_data = {
            'username': self.user_register_data.get('username'),
            'password': self.user_register_data.get('password')
        }
        response = self.client.post(self.api_login_url, data=login_data)
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
