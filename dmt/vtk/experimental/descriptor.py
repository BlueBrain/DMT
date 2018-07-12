"""An attempt at creating Fields out of a class."""


class Field:
    """Creates a field from a provided class."""

    def __init__(self, cls):
        self.__field_cls = cls
        self.storage_name = "${}".format(cls.__name__)

    def __set__(self, instance, value):
        """set the value of the field in an instance
        where a field has been declared."""
        if not self.__field_cls.__accepts__(value):
            raise ValueError(
                self.__field_cls.__name__ + " does not accept " + str(value)
            )
        instance.__dict__[self.storage_name] = self.__field_cls(value)

    def __get__(self, instance, owner):
        """get the value of the field, from the instance
        it was created in."""
        return instance.__dict__[self.storage_name].__value__()
