class CallableBool(object):
    def __init__(self, value):
        self.value = value

    def __bool__(self):
        return self.value

    def __nonzero__(self):
        return self.value

    def __call__(self):
        return self.value


CallableTrue = CallableBool(True)
CallableFalse = CallableBool(False)
