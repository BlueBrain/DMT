"""An attempt at creating Fields out of a class."""

from dmt.vtk.utils.exceptions import RequiredKeywordArgumentError

class __Field:
    """Creates a field from a provided class."""

    #__isabstractmethod__ = True
    __is_field__ = True

    def __init__(self, field_name, field_type, validation=None):
        """"
        Parameters
        -----------------------------------------------------------------------
        cls :: a type, not an instance
        validation :: a predicate function to validate values to set
        """
        self.__field_name__ = field_name
        self.__type__ = field_type
        self.__is_valid = validation if validation is not None\
                            else lambda value: True
        self.instance_storage_name\
            = "${}_{}".format(field_type.__name__, field_name)

    def __is_minimally_valid(self, value):
        """Minimum requirement on value to pass as a valid instance."""
        return isinstance(value, self.__type__)

    def is_valid(self, value):
        return self.__is_minimally_valid(value) and self.__is_valid(value)

    def __set__(self, instance, value):
        """set the value of the field in an instance
        where a field has been declared."""
        if not self.__is_minimally_valid(value):
            raise TypeError("{} cannot be set to {} of type {}"\
                             .format(self.__type__.__name__,
                                     value, str(type(value))))
        if not self.__is_valid(value):
            raise ValueError(
                "{} of type {} cannot be set to an invalid value, {}"\
                .format(self.instance_storage_name, self.__type__.__name__, value))
        setattr(instance, self.instance_storage_name, value)

    def __get__(self, instance, owner):
        """get the value of the field, from the instance
        it was created in."""
        if not instance is None:
            return getattr(instance, self.instance_storage_name)
        if not self.__field_name__ in dir(owner):
            print("{} is not a field member of {}"\
                  .format(self.__field_name__, owner.__name__))
            return None
        for mo in owner.__mro__:
            if self.__field_name__ in mo.__dict__.keys():
                return mo.__dict__[self.__field_name__]
        raise Exception("field member {} NOT FOUND in class {}"\
                        .format(self.__field_name__, owner.__name__))

    def __repr__(self):
        """represent this field as a string."""
        return "Field {}".format(str(self.__type__))


def Field(__name__, #name of the field, 
          __type__, #type of the field value
          __doc__ = None, #document string
          __is_valid_value__ = lambda x: True):
    """A factory function to define a Field.
    It is unfortunate that we have to require a __name__ argument."""
    F = __Field(__name__, __type__, __is_valid_value__)
    F.__doc__ =  __doc__
    return F

def is_field(x):
    """Is x a field?"""
    return getattr(x, '__is_field__', False)

def __get_field_attrs(cls):
    """get fields of class cls"""
    return [attr for attr, value in cls.__dict__.items() if is_field(value)]

def document_fields(cls):
    """Document any Fields that may appear in class cls.
    Can be used as class decorator."""
    field_docs = "\n\nFields\n"
    field_docs += 70 * "-" + "\n"
    for attr, value in cls.__dict__.items():
        if is_field(value):
            field_docs += attr + "\n"
            field_docs += "    type {}\n".format(value.__type__)
            field_docs += "    {}\n".format(value.__doc__)
    field_docs += 70 * "-" + "\n"
    cls.__doc__ += field_docs
    return cls

def initialize_fields(cls):
    """A class decorator that will extract fields from a class' attributes,
    and add their doc strings to that of the class."""
    cls = document_fields(cls)
    original_init = cls.__init__
    def field_init(self, *args, **kwargs):
        """insert fields into the class dict"""
        try:
            original_init(self, *args, **kwargs)
        except:
            pass
        for attr in __get_field_attrs(self.__class__):
            try:
                value = kwargs[attr]
            except:
                raise RequiredKeywordArgumentError(attr)
            setattr(self, attr, value)
    cls.__init__ = field_init
            
    return cls





