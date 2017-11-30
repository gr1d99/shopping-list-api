import string


class Validator(object):
    PUNCTUATIONS = list(string.punctuation)
    DIGITS = list(string.digits)
    PREFIX = 'validate_'

    def __init__(self, value, special=True, allow_digits=False, allow_spaces=False):
        self.value = str(value)
        self.special = special
        self.allow_digits = allow_digits
        self.allow_spaces = allow_spaces


class CustomValidator(Validator):
    def __init__(self, *args, **kwargs):
        super(CustomValidator, self).__init__(*args, **kwargs)
        self.whitespace = " "

    def validate_does_not_startswith_special_chars(self):
        if not self.special:
            try:
                if self.value[0] in CustomValidator.PUNCTUATIONS:
                    raise ValueError('cannot start with %(c)s' % dict(c=self.value[0]))

            except IndexError:
                pass

    def validate_does_not_contain_special_chars(self):
        if not self.special:
            val = list(self.value)
            for c in val:
                if c in CustomValidator.PUNCTUATIONS:
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
                    if self.value[0] in CustomValidator.DIGITS:
                        raise ValueError('cannot start with digits')

                except IndexError:
                    pass

    def validate_does_not_contain_digits(self):
        if not self.allow_digits:
            val = list(self.value)
            for c in val:
                if c in CustomValidator.DIGITS:
                    raise ValueError('should not contain any digits.')


def validate(value, special=False, allow_digits=False, allow_spaces=False):
    for method in dir(CustomValidator):
        if method.startswith(CustomValidator.PREFIX):
            getattr(CustomValidator(value, special, allow_digits, allow_spaces), method)()