"""Base class for all tests for the application configuration"""

from flask_testing import TestCase
from app import APP


class TestBaseCase(TestCase):
    def create_app(self):
        return APP
