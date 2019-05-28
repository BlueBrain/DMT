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
        self.__class__.__doc__ = __doc__.strip()
        self.__type__ = __type__
        self.__validation__ = __validation__
        self.__required__ = required
        self.__attr_name__ = None

    def __get_instance_attribute_name(self, instance):
        """
        The attribute name that an instance of a class with
        this Field instance will store its value with.
        """
        if self.__attr_name__ is None:
            raise ValueError(
                """Cannot provide instance attribute's name if
                this Field's '__attr_name__' attribute has not been set.""")
        return "${}_{}".format(self.__type__.__name__, self.__attr_name__)

    def assert_validity(self, value):
        """Is 'value' valid value of this Field?"""
        if not isinstance(value, self.__type__):
            raise TypeError(
                "Cannot set field '{}' of type '{}' to value '{}' of type '{}'"\
                .format(
                    self.__attr_name__,
                    self.__type__.__name__,
                    value,
                    str(type(value))))
        if not self.__validation__(value):
            raise ValueError(
                "Field '{}' of type '{}' cannot be an invalid value."\
                .format(
                    self.__attr_name__,
                    self.__type__.__name__,
                    value))
        return True

    @property
    def description(self):
        """Describe this ClassAttribute"""
        return "Field<{}>".format(self.__doc__)

    def __set__(self, instance, value):
        """
        Set the value of this Field in an class instance.
        """
        self.assert_validity(value)
        setattr(instance, self.__get_instance_attribute_name(instance), value)

    def __get__(self, instance, owner):
        """
        Get the value of this Field stored in an instance of the class that
        has this Field.
        """
        if instance:
            return getattr(
                instance,
                self.__get_instance_attribute_name(instance))
        #assuming owner is the class in which this Field was defined...
        return self
