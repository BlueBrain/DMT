"""
Classes that are Python Descriptors.

Descriptor: An object attribute whose access has been overriden by methods in
the descriptor protocol. The descriptor protocol requires implementation of at
least one of __get__, __set__, and __delete__ methods.

Further reading: https://docs.python.org/3/howto/descriptor.html

"""

from sys import stdout
from abc import ABC
from .field import Field
from .prop import Property
from .class_attribute import ClassAttribute, UndefinedClassAttribute
from ..journal import Logger

def set_name(
        field_or_class_attribute,
        name):
    """
    Set name of a field or class attribute.
    """
    setattr(
        field_or_class_attribute,
        "__attr_name__",
        name)


def get_value(
        key_values,
        field_or_class_attribute):
    """
    Get value of a field or class attribute from a dictionary.
    """
    return\
        key_values.get(
            field_or_class_attribute.__attr_name__,
            field_or_class_attribute.__default_value__)


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
            return True

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

            return getattr(class_field, "__default_value__", None)

        for field in self.get_fields():
            class_field =\
                getattr(
                    self.__class__,
                    field,
                    None)
            class_field\
                .set_defining_class(
                    self.__class__)
            set_name(
                class_field,
                field)
            self.__description__[field] = class_field.description
            if isinstance(class_field, ClassAttribute):
                self._check_class_attribute(class_field)
            value = __get_value(field)

            if value is not None:
                __check_validity(class_field, value)

            if class_field.__required__:
                if value is None:
                    documentation = class_field\
                        .documentation\
                        .replace('\n', "\n\t\t")
                    print(
                        """Please provide Field '{}':
                        {}""".format(
                            field,
                            documentation),
                        file=stdout)
                    raise ValueError(
                    """
                    Cannot create '{}' instance without required Field '{}'.
                    Please provide a value as a keyword argument in your 
                    instance initialization.
                    Missing Field '{}':
                    \t{}
                    """.format(
                        self.__class__.__name__,
                        field,
                        field,
                        documentation))
                setattr(self, field, value)
            elif value is None:
                #Value is not required
                pass
            else:
                setattr(self, field, value)

        if not hasattr(self, "_logger"):
            self._logger = Logger(
                client=self.__class__.__name__,
                level=kwargs.get("log_level", None))

        try:
            super().__init__(
                *args, **kwargs)
        except TypeError as error:
            pass

    def _check_class_attribute(self, field):
        """
        Complain that class attribute has not been defined.
        """
        if isinstance(field, ClassAttribute):
            raise UndefinedClassAttribute(
                """
                Attempt to instantiate class {} with undefined ClassAttribute.
                You can instantiate a subclass that defines {}.
                Please take a look at ClassAttribute {}'s documentation:
                \t{}
                """.format(
                    self.__class__.__name__,
                    field.__attr_name__,
                    field.__attr_name__,
                    field.__doc__))

    def describe(self, field):
        """
        Describe a Field
        """
        self._logger.info(
            """{}: {}""".format(
                field,
                self.__description__.get(
                    field,
                    "Description not available")))

    @classmethod
    def is_required(cls, field):
        """
        Check if Field attribute 'field' is required.
        """
        field_attr = getattr(cls, field)
        return field_attr.__required__

    @classmethod
    def get_fields(cls, only_required=False):
        """..."""
        fields =[
            attr for attr in dir(cls)
            if isinstance(getattr(cls, attr), (Field, ClassAttribute))]
        if not only_required:
            return fields
        return [
            field for field in fields
            if cls.is_required(field)]


    @property
    def as_dict(self):
        """
        Convert the Fields of this instance into a dict.
        We assume that no one will ever define a Field whose
        value type is also a Field.
        """
        field_values =(
            (field, getattr(self, field))
            for field in self.get_fields()
            if hasattr(self, field))
        return {
            field: value
            for field, value in field_values
            if not isinstance(field, Field)}

ABCWithFields = type("ABCWithFields", (WithFields, ABC), {})


class ClassAttributeMetaBase(type):
    """
    A meta class to construct classes that must provide class attributes
    described as Fields.
    """

    def __new__(mcs, name, bases, namespace):
        """
        Arguments
        ---------
        mcs :: Metaclass based on FieldMetaBase, that we expect to have Fields.
        name :: Name of the class to be created by mcs
        bases :: tuple of bases of class to be created
        namespace :: dict of class attributes of class to be created
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
                        mcs.__name__,
                        value,
                        field.__attr_name__,
                        type(value),
                        field.__type__))
            except ValueError as error:
                raise ValueError(
                    """{}\n\t{}instance field {} value {} is invalid."""\
                    .format(
                        error,
                        mcs.__name__,
                        field.__attr_name__,
                        value))
            return True

        description_field = {}

        if not namespace.pop("__metaclass_base__", False):
            for field in [
                    attr for attr in dir(mcs)
                    if isinstance(getattr(mcs, attr, None), ClassAttribute)]:

                metaclass_field = getattr(mcs, field)

                set_name(metaclass_field, field)
                description_field[field] = metaclass_field.description
                value = get_value(namespace, metaclass_field)
                        
                if value is not None:
                    __check_validity(metaclass_field, value)

                if metaclass_field.__required__:
                    if value is None:
                        print("""
                        Please provide Field '{}':
                        {}""".format(
                            field,
                            metaclass_field.__doc__.replace('\n', "\n\t\t")),
                              file=stdout)
                        raise ValueError(
                            """Cannot create '{}' instance without required Field '{}'.
                            Please provide a value as a keyword argument in your 
                            instance initialization.
                            Missing Field '{}':
                            \t{}
                            """.format(
                                mcs.__name__,
                                field,
                                field,
                                metaclass_field.__doc__.replace('\n', "\n\t\t")))
                    else:
                        #value is valid and will be set as class attribute
                        pass
                elif value is None:#and is not required
                    pass
                else:#value is not required and valid, but will be set
                    pass


        namespace["__description__"] = description_field
        return super().__new__(
            mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace):
        """..."""
        super().__init__(
            name, bases, namespace)



def lazyfield(instance_field):
    """
    Make an 'instance_field' lazy.

    Arguments
    -----------
    instance_field:
    ~   a method attribute of a class decorated @lazyfield
    """
    field_name_for_storage = "_{}".format(instance_field.__name__)

    @property
    def effective(instance):
        """
        The effective method, resulting from the decoration `@lazyfield`.
        """
        if not hasattr(
                instance,
                field_name_for_storage):
            setattr(
                instance,
                field_name_for_storage,
                instance_field(instance))
        return\
            getattr(
                instance,
                field_name_for_storage)

    return effective

lazy = lazyfield

lazyproperty = lazyfield
