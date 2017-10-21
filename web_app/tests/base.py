"""Base class for all tests"""

from flask_testing import TestCase

from . import app


class TestBase(TestCase):
    def create_app(self):
        return app
