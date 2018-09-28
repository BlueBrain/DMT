"""An attempt at creating Fields out of a class."""
from abc import ABCMeta, ABC, abstractmethod
import collections
from dmt.vtk.utils.exceptions import \
    RequiredKeywordArgumentError, RequiredArgumentError
from dmt.vtk.utils.logging import Logger, with_logging
from dmt.vtk.utils.logging.message import Validation

@with_logging(Logger.level.STUDY)
class Field:
    """Creates a field from a provided class."""

    __is_field__ = True

    def __init__(self, __name__, __type__,
                 __is_valid_value__=None,
                 __is_valid__=lambda instance, x: True,
                 __doc__ = "A field.",
                 __examples__=[],
                 *args, **kwargs):
        """"
        Parameters
        -----------------------------------------------------------------------
        cls :: a type, not an instance
        validation :: a predicate function to validate values to set
        """
        self.__field_name__ = __name__
        self.__type__ = __type__

        if __is_valid_value__ is not None:
            self.__is_valid_value = __is_valid_value__
        else:
            self.__is_valid_value = __is_valid__

        __doc__ = __doc__.strip()
        self.__doc__ = __doc__
        if __examples__:
            self.__doc__ += "{}You may check {}.examples for further guidance."\
                            .format('. ' if __doc__[-1] != '.' else ' ',
                                    self.__field_name__)
        self.__examples__=__examples__
        self.instance_storage_name\
            = "${}_{}".format(__type__.__name__, __name__)

        super(Field, self).__init__(*args, **kwargs)

    @property
    def examples(self):
        """..."""
        return self.__examples__

    def __is_minimally_valid(self, value):
        """Minimum requirement on value to pass as a valid instance."""
        return isinstance(value, self.__type__)

    def is_valid(self, instance, value):
        """..."""
        return self.validation(instance, value).passed

    def validation(self, instance, value):
        """is valid value?"""
        try: 
            self.assert_validity(value, *args)
        except TypeError as exception:
            message = """Value {} has incorrect type. Expected {}, received {}"""\
                      .format(value, self.__type__, type(value))
            return Validation(message, exception)
        except ValueError as exception:
            message = """{} is correct type but has invalid value. Look up
            this Field's doc""".format(value)
            return Validation(message, exception)
        return Validation("{} is a valid value of {} field {}."\
                         .format(value,
                                 instance.__class__.__name__,
                                 self.__name__))

    def assert_validity(self, instance, value):
        """..."""
        if not isinstance(value, self.__type__):
            raise TypeError(
                "Cannot set field '{}' of type '{}' to value '{}' of type '{}'"\
                .format(self.__field_name__,
                        self.__type__.__name__,
                        value, str(type(value)))
            )
        error = ValueError(
            "Field '{}' of type '{}' cannot be set to an invalid value, '{}'"\
            .format(self.__field_name__,
                    self.__type__.__name__,
                    value)
        )
        if not self.__is_valid_value(instance, value):
            raise error
        return

    def __set__(self, instance, value):
        """set the value of the field in an instance
        where a field has been declared."""
        self.assert_validity(instance, value)
        setattr(instance, self.instance_storage_name, value)

    def __get__(self, instance, owner):
        """get the value of the field, from the instance
        it was created in."""
        if not instance is None:
            return getattr(instance, self.instance_storage_name)
        if not self.__field_name__ in dir(owner):
            self.logger.info("{} is not a Field member of {}"\
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

    class typecheck:
        """Typecheck attributes of an instance containing a Field.
        This has only 'staticmethod' --- so acts as a module under 'Field'.
        """
        @staticmethod
        def get_type(instance, type_arg):
            if isinstance(type_arg, type):
                return type_arg
            try:
                return getattr(instance, type_arg)
            except TypeError as e:
                raise TypeError(
                    "{}.\nIf not a type, 'type_arg' must be a string".format(e)
                )

        @staticmethod
        def collection(elem_type_arg):
            """
            Arguments
            --------------------------------------------------------------------
            elem_type_arg :: Either[type, str]# either type to check against, or
            ~                                 # instance attribute that provides it
            """

            def check(instance, candidate_attr_value):
                """..."""
                elem_type = Field.typecheck.get_type(instance, elem_type_arg)

                for element in candidate_attr_value:
                    if not isinstance(element, elem_type):
                        raise TypeError(
                            """element {} of a collection field of {} instance
                            does not type-check {}"""\
                            .format(element,
                                    instance.__class__.__name__,
                                    elem_type.__name__)
                        )
                return True
            return check

        @staticmethod
        def mapping(key_type_arg, val_type_arg):
            """
            Arguments
            ----------------------------------------------------------------
            key_type_arg :: Either[type, str],# either key type to check, or
            ~                                 # instance attribute that provides it
            val_type_arg :: Either[type, str],# either value type to check, or
            ~                                 # instance attribute that provides it
            """
            def check(instance, candidate_attr_value):
                """..."""
                key_type = Field.typecheck.get_type(instance, key_type_arg)
                val_type = Field.typecheck.get_type(instance, val_type_arg)
                for key, val in candidate_attr_value.items():
                    if not isinstance(key, key_type):
                        raise TypeError(
                            """key '{}' of a mapping field of '{}' instance
                            does not type-check '{}"""
                            .format(key, 
                                    instance.__class__.__name__,
                                    key_type.__name__)
                        )
                    if not isinstance(val, val_type):
                        raise TypeError(
                            """value '{}' of mapping field  of
                            {} instance does not type-check {}"""
                            .format(val,
                                    instance.__class__.__name__,
                                    val_type.__name__)
                        )
                return True
            return check



def field(__name__, #name of the field, 
          __type__, #type of the field value
          __is_valid_value__ = lambda instance, x: True,
          __doc__ = None): #document string
    """A factory function to define a Field.
    It is unfortunate that we have to require a __name__ argument."""
    F = Field(__name__, __type__, __is_valid_value__, __doc__)
    return F

def is_field(x):
    """Is x a field?"""
    return getattr(x, '__is_field__', False)

def __get_field_attrs(cls):
    """get fields of class cls"""
    return [attr for attr, value in cls.__dict__.items() if is_field(value)]

def initialize_fields(cls):
    """A class decorator that will extract fields from a class' attributes,
    and add their doc strings to that of the class."""
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


#now Field at the class level
class ClassAttribute:
    """An non-method attribute that should be defined by a deriving class
    as a class attribute."""

    def __init__(self, __name__, __type__,
                 __is_valid_value__=lambda x: True,
                 __doc__ = "A field."):
        """"
        Parameters
        -----------------------------------------------------------------------
        cls :: a type, not an instance
        validation :: a predicate function to validate values to set
        """
        self.__field_name__ = __name__
        self.__type__ = __type__
        self.__is_valid = __is_valid_value__
        self.__doc__ = __doc__

    def check_validity(self, value):
        """Check if value is valid"""
        return isinstance(value, self.__type__) and self.__is_valid(value)

    def __repr__(self):
        """represent this ClassAttribute as a string."""
        return "ClassAttribute {}".format(str(self.__type__))


class ClassAttributeMeta(type):
   """Checks if a sub class definition contains the required fields.""" 

   def __init__(cls, name, bases, namespace):
       for b in cls.__bases__:
           for m, v in b.__dict__.items():
               if isinstance(v, ClassAttribute):
                   cls_v = getattr(cls, m)
                   if not isinstance(cls_v, ClassAttribute):
                       assert v.check_validity(cls_v),\
                           """Invalid class field value {}.
                           Try help({}).""".format(cls_v,  b)
       super(ClassAttributeMeta, cls).__init__(name, bases, namespace)
        

@with_logging(Logger.level.STUDY)
class WithFCA:
    """Check if a the class definition has 'Field's or 'ClassAttribute's,
    and adapt '__init__' accordingly. This will be useful for
    documenting / typing abstract attributes, in association with 'ABC'."""

    def __init__(self, *args, **kwargs):
        """
        A mixin class' '__init__' should provide attributes that are
        required for providing the mixin's features. A mixin may declare
        abstractmethods, assuming those are provided by the mixing class.
        The mixing class may use yet another mixin for providing the missing
        attributes.
        So a good mixin will be one that mixes in very specific features.
        """
        cls = self.__class__
        fields = self.get_fields()
        for field in fields:
            cls_field = getattr(cls, field)
            if hasattr(self, field) and not isinstance(getattr(self, field), Field):
                self_field = getattr(self, field)
                try:
                    cls_field.assert_validity(self, self_field)
                except TypeError as e:
                    raise TypeError(
                        "{} instance field {} has inadmissible type: {}"\
                        .format(cls._name__, field, type(self_field).__name__)
                    )
                except ValueError as e:
                    raise ValueError(
                        "{} instance field {} has inadmissible value: {}"\
                        .format(cls._name__, field, self_field)
                    )
            else:
                if field in kwargs:
                    setattr(self, field, kwargs[field])
                else:
                    raise TypeError(
                        "Can't instantiate abstract class {} "
                        "with undefined Field {}"
                        .format(self.__class__.__name__, field)
                    )
        try:
            super(WithFCA, self).__init__(*args, **kwargs)
        except TypeError as te:
            pass

    @classmethod
    def get_fields(cls):
        """..."""
        return [
            attr for attr in dir(cls) if isinstance(getattr(cls, attr), Field)
        ]

    @classmethod
    def get_class_attributes(cls):
        """..."""
        return [attribute for attribute, value in dir(cls)
                if isinstance(value, ClassAttribute)]

def document_fields(cls):
    """Document any Fields that may appear in class cls.
    Can be used as class decorator."""
    doc_included = {}
    field_docs = ""
    for mcls in cls.__mro__:
        field_attrs = [a for a, v in mcls.__dict__.items()
                       if isinstance(v, Field)]
        if len(field_attrs) == 0:
            continue
        if mcls != cls:
            field_docs += "\nFields inherited from {}.\n".format(mcls.__name__)
            field_docs += 70 * "-" + "\n"
        for attr, value in mcls.__dict__.items():
            if not doc_included.get(attr, False) and is_field(value):
                field_docs += attr + "\n"
                field_docs += "    type {}\n".format(value.__type__.__name__)
                field_docs += "    {}\n".format(value.__doc__)
                field_docs += 70 * "-" + "\n"
                doc_included[attr] = True
    if len(field_docs) > 0:
        cls.__doc__ = "\n\nFields\n"
        cls.__doc__ += 70 * "-" + "\n"
        cls.__doc__ += field_docs

    cattr_docs = ""
    for attr, value in cls.__dict__.items():
        if isinstance(value, ClassAttribute):
            cattr_docs += attr + "\n"
            cattr_docs += "    type {}\n".format(value.__type__.__name__)
            cattr_docs += "    {}\n".format(value.__doc__)
            cattr_docs += 70 * "-" + "\n"
    if len(cattr_docs) > 0:
        cls.__doc__ = "\n\nClass Attributes\n"
        cls.__doc__ += 70 * "-" + "\n"
        cls.__doc__ += cattr_docs

    return cls

