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
            __required__=True,
            __default_value__=None,
            __examples__=[]):
        """Initialize Me"""
        self.__doc__ = __doc__
        self.__type__ = __type__
        self.__validation__ = __validation__
        self.__required__ = __required__
        self.__attr_name__ = None
        self.__default_value__ = __default_value__
        self.__examples__  = __examples__
        self.__defined_in__ = "Unknown"

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

    def set_defining_class(self, cls):
        """
        Where was this `Field` defined.
        """
        self.__defined_in__ = cls.__name__

    @property
    def examples(self):
        """
        Get examples
        """
        return self.__examples__

    @property
    def documentation(self):
        """
        Documentation with examples.
        """
        if not self.__examples__:
            return self.__doc__
        return self.__doc__ + """
        You may look at some examples: `{}.{}.examples`
        """.format(
            self.__defined_in__,
            self.__attr_name__)

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



