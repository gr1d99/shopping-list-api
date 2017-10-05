import os
from shopping_list.settings import BASE_DIR


class Config(object):
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')


class ProductionConfig(Config):
    DATABASE_URI = "sqlite://:memory:"


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, 'test.db')
    TESTING = True
