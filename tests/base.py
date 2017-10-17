"""Base class for all tests"""

import unittest

from main import app


class TestBase(unittest.TestCase):
    def setUp(self):
        self.app = app
