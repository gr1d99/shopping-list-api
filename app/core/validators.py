"""
Application module with custom validator classes for username and password inputs.
"""

import re


class PasswordValidator(object):
    """
    Validates password inputs and stores appropriate
    error message for each error found.
    """
    PREFIX = 'inspect_'

    def __init__(self, password):
        self.password = password
        self.errors = []
        self.has_errors = False

    def __call__(self, *args, **kwargs):
        for method in dir(self):
            if method.startswith(PasswordValidator.PREFIX):
                getattr(self, method)()

    def add_error(self, error):
        self.errors.append(error)
        self.has_errors = True

    def inspect_lower(self):
        regex = re.compile('[a-z ]+')
        res = re.search(regex, self.password)
        if not res:
            self.add_error('should contain at least one character in lowercase')

    def inspect_upper(self):
        regex = re.compile('[A-Z ]+')
        res = re.search(regex, self.password)
        if not res:
            self.add_error('should contain at least one letter in uppercase')

    def inspect_punctuations(self):
        regex = re.compile('[!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ ]+')
        res = re.search(regex, self.password)
        if not res:
            self.add_error('should contain at least one special character')

    def inspect_integers(self):
        regex = re.compile('[0-9 ]+')
        res = re.search(regex, self.password)
        if not res:
            self.add_error('should contain at least on digit')

    def inspect_length(self):
        regex = re.compile('[a-zA-Z0-9!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ ]{8,}')
        res = re.search(regex, self.password)
        if not res:
            self.add_error('password length should not be minimum than eight characters long')

    def inspect_continuous_characters(self):
        res = re.findall(r'(.)\1{3,}', self.password)
        if not bool(res == []):
            self.add_error('should not have more than three '
                           'characters following each other')


class UsernameValidator(object):
    """
    Validates username input value and store appropriate error
    encountered during validation process.
    """
    PREFIX = 'validate_'

    def __init__(self, username):
        self.username = username
        self.errors = []
        self.has_errors = False

    def __call__(self, *args, **kwargs):
        for method in dir(self):
            if method.startswith(UsernameValidator.PREFIX):
                getattr(self, method)()

    def add_error(self, error):
        self.errors.append(error)
        self.has_errors = True

    def validate_username(self):
        regex = re.compile('^[a-zA-Z0-9_@]+$')

        res = re.match(regex, self.username)
        if not res:
            self.add_error('should only contain alpha-numeric characters, optional special characters are @ and _')

    def validate_continuous(self):
        last = self.username[-1:]
        regex = re.compile('^[%(char)s]+$' % dict(char=last))
        res = re.match(regex, self.username)
        if res:
            self.add_error('cannot be all `%(last)s`' % dict(last=last))


class NameValidator(UsernameValidator):
    """
    Validates normal names that restricts the number of special characters in the sentence.
    """
    def validate_username(self):
        regex = re.compile('^[a-zA-Z0-9_@ ]+$')

        res = re.match(regex, self.username)
        if not res:
            self.add_error('should only contain alpha-numeric characters, '
                           'optional special characters are @ and _')