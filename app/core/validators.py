import string


class Validator(object):
    PUNCTUATIONS = (char for char in string.punctuation)
    DIGITS = (str(dig) for dig in string.digits)

    def __init__(self, value, allow_spaces=False):
        self.prefix = 'validate_'
        self.value = str(value)
        self.allow_spaces = allow_spaces

    def validate(self):
        for method in dir(self):
            if method.startswith(self.prefix):
                getattr(self, method)()


class CustomValidator(Validator):
    def __init__(self, *args, **kwargs):
        super(CustomValidator, self).__init__(*args, **kwargs)
        self.whitespace = " "

    def validate_does_not_startswith_special_chars(self):

        for c in Validator.PUNCTUATIONS:
            if self.value.startswith(c):
                raise ValueError('cannot start with %(c)s' % dict(c=c))

    def validate_does_not_startswith_space(self):
        if self.value.startswith(self.whitespace):
            raise ValueError('cannot start with whitespace')

    def validate_does_not_contain_whitespaces(self):
        if not self.allow_spaces:
            if self.value.__contains__(self.whitespace):
                raise ValueError("cannot contain whitespaces")

    def validate_does_not_startswith_digits(self):
        for dig in Validator.DIGITS:
            if self.value.startswith(dig):
                raise ValueError('cannot start with digits')


