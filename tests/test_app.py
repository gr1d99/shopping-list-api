"""
    Contain tests for various app configuration environments such as

    1. Testing
    2. Development
    3. Production

"""

from .base import TestBase
from web_app.conf import app_config


class TestEnviroments(TestBase):
    """Test various app environment configurations"""
    def test_testing(self):
        """
        Test app is set to testing.
        """
        self.app.config.from_object(app_config.TestingConfig)
        self.assertTrue(self.app.testing)

    def test_development(self):
        """
        Test app is set to development.
        """
        self.app.config.from_object(app_config.DevelopmentConfig)
        self.assertTrue(self.app.debug)

    def test_production(self):
        """Test app is set to production."""
        self.app.config.from_object(app_config.ProductionConfig)
        self.assertFalse(self.app.debug)
