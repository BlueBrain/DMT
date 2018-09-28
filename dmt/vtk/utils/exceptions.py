"""Custom exceptions"""
class RequiredKeywordArgumentError(TypeError):
    def __init__(self, key, *args):
        self.message = key
        super(RequiredKeywordArgumentError, self).__init__(key, *args)


class RequiredArgumentError(TypeError):
    def __init__(self, pos, argname, *args):
        self.message = argname + " at pos " + str(pos)
        super(RequiredArgumentError, self).__init__(self.message, *args)


class InvalidArgumentError(Exception):
    pass


class InvalidArgumentTypeError(Exception):
    def __init__(self, expected=None, received=None):
        self.message = ("Expecting " + str(expected) +
                        ", received " + str(received))
        super(InvalidArgumentTypeError, self).__init__(self.message)


class InvaldTraitDefinitionError(Exception):
    pass


class ValueNotSetError(Exception):
    def __init__(self, attribute, obj, *args):
        self.message = "Attribute {} of {} was not set.".format(attribute, obj)
