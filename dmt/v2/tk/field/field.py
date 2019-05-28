"""
Field with description
"""
import sys
import collections

class Field:
    """
    Field of a class, with description
    """

    __is_field__ = True

    def __init__(self,
            __doc__: str,#documentation for this Field is required
            __type__=object,
            __validation__=lambda x: True,
            required=True):
        """Initialize Me"""
        self.__doc__ = __doc__.strip()
        self.__type__ = __type__
        self.__validation__ = __validation__
        self.__required__ = required
        self.__field_name__ = None

    def get_instance_attribute_name(self, instance):
        """
        The attribute name that an instance of a class with
        this Field instance will store its value with.
        """
        if self.__field_name__ is None:
            raise ValueError(
                """Cannot provide instance attribute's name if
                this Field's '__field_name__' attribute has not been set.""")
        return "${}_{}".format(self.__type__.__name__, self.__field_name__)

    def assert_validity(self, value):
        """Is 'value' valid value of this Field?"""
        if not isinstance(value, self.__type__):
            raise TypeError(
                "Cannot set field '{}' of type '{}' to value '{}' of type '{}'"\
                .format(
                    self.__field_name__,
                    self.__type__.__name__,
                    value,
                    str(type(value))))
        if not self.__validation__(value):
            raise ValueError(
                "Field '{}' of type '{}' cannot be an invalid value."\
                .format(
                    self.__field_name__,
                    self.__type__.__name__,
                    value))
        return True

    def __set__(self, instance, value):
        """
        Set the value of this Field in an class instance.
        """
        self.assert_validity(value)
        setattr(instance, self.get_instance_attribute_name(instance), value)

    def __get__(self, instance, owner):
        """
        Get the value of this Field stored in an instance of the class that
        has this Field.
        """
        if instance:
            return getattr(
                instance,
                self.get_instance_attribute_name(instance))
        #assuming owner is the class in which this Field was defined...
        return self

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
                        field.__field_name__,
                        type(value),
                        field.__type__))
            except ValueError as error:
                raise ValueError(
                    "{}\n\t{}instance field {} value {} is invalid."\
                    .format(
                        error,
                        self.__class__.__name__,
                        field.__field_name__,
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

            if hasattr(class_field, "default_value"):
                return class_field.default_value

            return None


        for field in self.get_fields():
            class_field = getattr(self.__class__, field, None)
            setattr(class_field, "__field_name__", field)
            value = __get_value(field)

            if value:
                __check_validity(class_field, value)

            if class_field.__required__:
                if value is None:
                    print(
                        "Please provide Field {}: {}".format(
                            field,
                            class_field.__doc__),
                        file=sys.stdout)
                    raise ValueError(
                        """Cannot create an instance of {} without field {}.
                        Please proivde Field {}: {} """.format(
                            self.__class__.__name__,
                            field,
                            field, class_field.__doc__))
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
