"""
Field with description
"""
import sys
import collections
from ..collections import emuset

class Field:
    """
    Field of a class, with description
    """

    __is_field__ = True

    def __init__(self,
            __doc__: str,#documentation for this Field is required
            __type__=object,
            __validation__=lambda x: True,
            __required__=True,
            __default_value__=None):
        """Initialize Me"""
        self.__doc__ = __doc__
        self.__type__ = __type__
        self.__validation__ = __validation__
        self.__required__ = __required__
        self.__attr_name__ = None
        self.__default_value__ = __default_value__

    def __get_instance_attribute_name(self, instance):
        """
        The attribute name that an instance of a class with
        this Field instance will store its value with.
        """
        self.__check_name()
        type_prefix =\
            self.__type__.__name__ if not isinstance(self.__type__, tuple)\
            else '_'.join(t.__name__ for t in self.__type__)
        return "${}_{}".format(type_prefix, self.__attr_name__)

    def __check_name(self):
        """
        Has this Field instance been given a name?
        The intended use of Field is through the associated
        WithFields baseclass. Fields are initialized, and given a name in the
        initializer method of WithFields. So if a Field instance does not have
        a name, it could mean that the class where this Field has been defined
        does not derive from WithFields.
        """
        if self.__attr_name__ is None:
            raise ValueError("""
              Field instance does not have a name (__attr_name__).
              Check if the containing class was based on WithFields.
              """)

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
        """Describe this Field"""
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



class Property(Field):
    """
    Fully define a property of an object,
    specifying the key to be used to index data-sets containing
    the object, as well as its value type, and the set of values it may assume.
    """
    def __init__(self,
            __label__=None,
            __type__=object,
            __value_set__=set(),#empty means any value
            *args, **kwargs):
        """
        Initialize...
        """
        def __is_valid(instance, value):
            """
            Validate a value.

            Arguments
            -------------
            value :: Either a singleton, or an iterable.
            If 'value' is a singleton, it should be of the accepted type.
            If 'value' is an iterable (for e.g. a set of values), each
            of these values must be of the accepted type.
            """
            value_is_collection =\
                isinstance(value, collections.Iterable) and\
                not isinstance(value, (str, bytes))
            if __value_set__:
                if value_is_collection:
                    return all(
                        isinstance(v, __type__) and v in __value_set__
                        for v in value)
                return isinstance(value, __type__) and value in __value_set__
            if value_is_collection:
                return all(
                    isinstance(v, __type__)
                    for v in value)
            return isinstance(value, __type__)

        if __value_set__:
            self.__value_set__= emuset(*__value_set__)
        super().__init__(
            __validation__=__is_valid,
            *args, **kwargs)
