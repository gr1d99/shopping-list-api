# -*- coding: utf-8 -*-

"""Contains all Tests for system app user"""

import collections
from . import \
    (DB, app_config, EmailExists, TestBase, User, UsernameExists)


class TestUserModel(TestBase):
    """Tests main User model class"""

    def __init__(self, *args, **kwargs):
        super(TestUserModel, self).__init__(*args, **kwargs)
        self.user = None
        self.user_info = None
        self._info = None

    def setUp(self):
        super(TestUserModel, self).setUp()
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

    def test_user_username(self):
        """
        Test username saved is same as used during creation.
        """
        self.user.save()

        # retrieve the username itself
        added_user = User.query.filter_by(username=self.user_info.username).first().username
        self.assertEqual(added_user, self.user_info.username)

    def test_user_email(self):
        """
        Test email created is same as one used during creation.
        """
        self.user.save()
        added_user = User.query.filter_by(email=self.user_info.email).first()

        self.assertEqual(added_user.email, self.user_info.email)

    def test_user_password(self):
        """
        Test verify password method.
        """
        user_raw_password = 'gideonpassword'
        self.user.save()
        adder_user = User.query.filter_by(username=self.user_info.username).first()

        self.assertTrue(adder_user.verify_password(user_raw_password))

    def test_update(self):
        """
        Test update columns.

        Updated values should be reflected back.
        """
        self.user.save()
        _new_data = self._info('gideon', 'gideon@yahoo.com', 'gideonpassword')
        self.user.username = _new_data.username
        self.user.email = _new_data.email
        self.user.save()

        saved_user = User.query.filter_by(username=_new_data.username).first()

        self.assertTrue((saved_user.username == _new_data.username and
                         saved_user.email == _new_data.email))

    def test_can_authenticate(self):
        """
        Test is_authenticated().

        authenticate() method should return True when called against the created
        user instance.
        """
        self.user.save()  # save user instance
        self.user.authenticate()  # call authenticate method
        saved_user = User.query.filter_by(username=self.user_info.username).first()
        self.assertTrue(saved_user.is_authenticated)  # test

    def test_can_deauthenticate(self):
        """
        Test deauthentication.
        :return:
        """
        self.user.save()
        saved_user = User.query.filter_by(username=self.user_info.username).first()

        # test if authenticated is set to False initially
        self.assertFalse(saved_user.is_authenticated)

        # call authenticate method and test it
        self.user.authenticate()
        self.assertTrue(self.user.authenticate())
        self.assertTrue(saved_user.is_authenticated)

        # finally deauthenticate and test it
        self.user.deauthenticate()
        self.assertFalse(saved_user.is_authenticated)

    def test_unique_username(self):
        """
        Test unique usernames only.

        An exception should be raised if there exists the same username.
        """
        with self.assertRaises(UsernameExists):
            self.user.save()  # save the user for the first time
            User.check_username(self.user_info.username)

    def test_unique_email(self):
        """
        Test unique email per user id.

        An exception should be raised if there exists the same email.
        """
        with self.assertRaises(EmailExists):
            # save the first user
            User(username='anotheruser', email=self.user_info.email, password='anotheruserpass').save()

            # call check method
            User.check_email(self.user_info.email)

    def test_required_colums(self):
        """
        Test required columns(username, email, password).
        """
        # start with null username
        expected_username_error = 'username is required'
        expected_email_error = 'email is required'
        empty_username = User('', 'password', 'user@email.com')
        empty_email = User('username', 'password', '')

        # None is always returned if data is saved successfully,
        # we will also counter check it with querying with the
        # model.

        self.assertIn(expected_username_error, empty_username.save().values())
        self.assertIn(expected_email_error, empty_email.save().values())

        # counter check by querying the database
        self.assertIsNone(User.query.filter_by(email=empty_username.email).first())
        self.assertIsNone(User.query.filter_by(username=empty_email.username).first())

    def test_delete_user(self):
        """Test user instance is deleted successfully."""
        self.user.save()
        # query user
        saved_user = User.query.filter_by(username=self.user_info.username).first()

        # check if saved user is not none
        self.assertIsNotNone(saved_user)

        # call delete method
        self.user.delete()
        # run the query again
        saved_user = User.query.filter_by(username=self.user_info.username).first()

        # check if the returned value is None
        self.assertIsNone(saved_user)
