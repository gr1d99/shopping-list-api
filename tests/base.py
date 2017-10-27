"""Base class for all tests for the application configuration"""

from flask_testing import TestCase

from . import APP


class TestBase(TestCase):
    def create_app(self):
        return APP
