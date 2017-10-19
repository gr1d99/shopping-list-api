"""Base class for all tests"""

from flask_testing import TestCase

from main import app


class TestBase(TestCase):
    def create_app(self):
        return app
