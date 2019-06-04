"""
Classes that are Python Descriptors.

Descriptor: An object attribute whose access has been overriden by methods in
the descriptor protocol. The descriptor protocol requires implementation of at
least one of __get__, __set__, and __delete__ methods.

Further reading: https://docs.python.org/3/howto/descriptor.html

"""

from sys import stdout
from .field import Field
from .class_attribute import ClassAttribute


class WithFields:
    """
        A base class that will add declared Fields.
        A mixin class' '__init__' should set attributes that provide the
        mixin's features. A mixin may declare abstractmethods, assuming that
        those will be provided by some another mixed in class. A good mixin
        will mix in very specific features.
        WithFields extracts attribute values from kwargs and adds them to 
        class attributes.
    """

    __description__ = {} #description of Fields and ClassAttributes

    def __init__(self,
            *args, **kwargs):
        """
        Initialize Me
        """

        def __check_validity(field, value):
            """..."""
            try:
                field.assert_validity(value)
            except TypeError as error:
                raise TypeError(
                    """{}\n\t{} field {} value {} type {} is inadmissible.
                    Expected type is {}."""\
                    .format(
                        error,
                        self.__class__.__name__,
                        value,
                        field.__attr_name__,
                        type(value),
                        field.__type__))
            except ValueError as error:
                raise ValueError(
                    "{}\n\t{}instance field {} value {} is invalid."\
                    .format(
                        error,
                        self.__class__.__name__,
                        field.__attr_name__,
                        value))
            pass

        def __get_value(field):
            """..."""
            if not hasattr(self.__class__, field):
                raise TypeError(
                    "{} is not a field of class {}".format(
                        field,
                        self.__class__.__name__))
            class_field = getattr(self.__class__, field, None)
            if hasattr(self, field):
                instance_field = getattr(self, field)
                if not isinstance(instance_field, Field):
                    #Field value already assigned
                    #before initialization chain hits WithFields.__init__
                    __check_validity(field, instance_field)
                    return instance_field
                else:
                    #instance's Field has not been set
                    pass
            else:
                #unassigned Field, read its value from kwargs
                pass

            if field in kwargs:
                return kwargs[field]
            else:
                #did not find Field in kwargs
                return None

            if hasattr(class_field, "__default_value__"):
                return class_field.__default_value__

            return None

        for field in self.get_fields():
            class_field = getattr(self.__class__, field, None)
            setattr(class_field, "__attr_name__", field)
            self.__description__[field] = class_field.description
            if isinstance(class_field, ClassAttribute):
                continue
            value = __get_value(field)

            if value:
                __check_validity(class_field, value)

            if class_field.__required__:
                if value is None:
                    print(
                        """Please provide Field '{}':
                        {}""".format(
                            field,
                            class_field.__doc__.replace('\n', "\n\t\t")),
                        file=stdout)
                    raise ValueError(
                    """Cannot create '{}' instance without required Field '{}'.
                    Please provide a value as a keyword argument in your 
                    instance initialization.
                    Missing Field '{}':
                    \t{}
                    """.format(
                        self.__class__.__name__,
                        field,
                        field,
                        class_field.__doc__.replace('\n', "\n\t\t")))
                setattr(self, field, value)
            elif value is None:
                #Value is not required
                pass
            else:
                setattr(self, field, value)

        try:
            super().__init__(
                *args, **kwargs)
        except TypeError as error:
            pass

    @classmethod
    def get_fields(cls):
        """..."""
        return [
            attr for attr in dir(cls)
            if isinstance(getattr(cls, attr), Field)]

    @classmethod
    def get_class_attributes(cls):
        """..."""
        return [
            attr for attr in dir(cls)
            if isinstance(getattr(cls, attr), ClassAttribute)]

