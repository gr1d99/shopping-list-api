"""
Application module defining configuration settings for various environments.
"""


import os
import datetime


class Config(object):
    """
    Default application configuration values.
    """

    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(seconds=360000)
    JWT_HEADER_NAME = 'x-access-token'
    JWT_HEADER_TYPE = None
    HOST = '0.0.0.0'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    JSON_SORT_KEYS = False


class ProductionConfig(Config):
    """
    Production environment configurations.
    """


class DevelopmentConfig(Config):
    """
    Development environment configuration.
    """

    DEBUG = True


class TestingConfig(Config):
    """
    Testing environment configuration.
    """

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DB_URL')
    TESTING = True
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(seconds=5)
