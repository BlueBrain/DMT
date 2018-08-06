"""An attempt at creating Fields out of a class."""


class Field:
    """Creates a field from a provided class."""
    __isfield__ = True
    __isabstractmethod__ = True

    def __init__(self, cls):
        self.__field_cls = cls
        self.storage_name = "${}".format(cls.__name__)

    def __set__(self, instance, value):
        """set the value of the field in an instance
        where a field has been declared."""
        if not isinstance(value, self.__field_cls):
            raise ValueError("{} cannot be set to {}"\
                             .format(self.__field_cls.__name__, value))
        setattr(instance, self.storage_name, value)

    def __get__(self, instance, owner):
        """get the value of the field, from the instance
        it was created in."""
        return getattr(instance, self.storage_name)
