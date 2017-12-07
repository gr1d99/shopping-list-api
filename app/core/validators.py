"""
Application module with custom validator classes for username and password inputs.
"""

import string


class BaseValidator(object):
    """
    Defines constants and initialize default values for other validator classes.
    """

    PUNCTUATIONS = list(string.punctuation)
    DIGITS = list(string.digits)
    PREFIX = 'validate_'

    def __init__(self, value, special=True, allow_digits=False, allow_spaces=False):
        self.value = str(value)
        self.special = special
        self.allow_digits = allow_digits
        self.allow_spaces = allow_spaces


class CustomBaseValidator(BaseValidator):
    def __init__(self, *args, **kwargs):
        super(CustomBaseValidator, self).__init__(*args, **kwargs)
        self.whitespace = " "

    def validate_does_not_startswith_special_chars(self):
        if not self.special:
            try:
                if self.value[0] in CustomBaseValidator.PUNCTUATIONS:
                    raise ValueError('cannot start with %(c)s' % dict(c=self.value[0]))

            except IndexError:
                pass

    def validate_does_not_contain_special_chars(self):
        if not self.special:
            val = list(self.value)
            for c in val:
                if c in CustomBaseValidator.PUNCTUATIONS:
                    raise ValueError('should not contain any punctuation marks.')

    def validate_does_not_startswith_space(self):
        if self.value.startswith(self.whitespace):
            raise ValueError('cannot start with whitespace')

    def validate_does_not_contain_whitespaces(self):
        if not self.allow_spaces:
            if self.value.__contains__(self.whitespace):
                raise ValueError("cannot contain whitespaces")

    def validate_does_not_startswith_digits(self):
            if not self.allow_digits:
                try:
                    if self.value[0] in CustomBaseValidator.DIGITS:
                        raise ValueError('cannot start with digits')

                except IndexError:
                    pass

    def validate_does_not_contain_digits(self):
        if not self.allow_digits:
            val = list(self.value)
            for c in val:
                if c in CustomBaseValidator.DIGITS:
                    raise ValueError('should not contain any digits.')


def validate(value, special=False, allow_digits=False, allow_spaces=False):
    """
    Runs the available validation methods to check input value.

    :param value: input.
    :param special: bool to allow special characters.
    :param allow_digits: bool to allow integers.
    :param allow_spaces: bool to allow spaces.
    :return: None
    """
    for method in dir(CustomBaseValidator):
        if method.startswith(CustomBaseValidator.PREFIX):
            getattr(CustomBaseValidator(value, special, allow_digits, allow_spaces), method)()