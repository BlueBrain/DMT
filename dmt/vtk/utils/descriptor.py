"""An attempt at creating Fields out of a class."""


class Field:
    """Creates a field from a provided class."""
    __isfield__ = True
    __isabstractmethod__ = True

    def __init__(self, cls, validation=None):
        """"
        Parameters
        -----------------------------------------------------------------------
        cls :: a type, not an instance
        validation :: a predicate function to validate values to set
        """
        self.__field_cls = cls
        self.__validation = validation if validation is not None\
                            else lambda value: True
        self.__is_valid = (validation if validation is not None else
                           lambda value: isinstance(value, self.__field.cls))
        self.storage_name = "${}".format(cls.__name__)

    def minimal_validation(self, value):
        """Minimum requirement on value to pass as a valid instance."""
        return isinstance(value, self.__field.cls)

    def is_valid(self, value):
        return self.minimal_validation(value) and self.__validation(value)

    def __set__(self, instance, value):
        """set the value of the field in an instance
        where a field has been declared."""
        if not self.is_valid(value):
            raise ValueError("{} cannot be set to {}"\
                             .format(self.__field_cls.__name__, value))
        setattr(instance, self.storage_name, value)

    def __get__(self, instance, owner):
        """get the value of the field, from the instance
        it was created in."""
        return getattr(instance, self.storage_name)
