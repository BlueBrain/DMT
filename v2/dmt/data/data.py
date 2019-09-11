"""
Prototype for Data.
"""
import pandas as pd
from dmt.tk.journal import Logger
from dmt.tk.field import\
    Field,\
    ClassAttribute,\
    WithFields,\
    ClassAttributeMetaBase

def is_data_base_class(cls):
    """???"""
    return getattr(cls, "__data_base_class__", False)


class DataClassMeta(ClassAttributeMetaBase):
    """
    A metaclass to construct Data classes
    """
    index = ClassAttribute(
        """
        A dict mapping the name of an index variable to its description.
        The names will be used to name the dataframe index,
        and the description to provide documentation.
        """,
        __type__=dict)
    measurements = ClassAttribute(
        """
        A dict mapping the name of measurement variable to its description.
        The names will be used to name the dataframe columns, 
        and the description to provide documentation.
        """,
        __type__=dict)
        

class DataClassConstructor(type):
    """
    A meta class to construct Data classes
    """

    def __new__(mcs, name, bases, namespace):
        """..."""
        logger = Logger(
            client="DataClassConstructor",
            level="STUDY")
        logger.study(
            """Construct new class with
            mcs {},
            name {},
            bases {}"""\
            .format(
                mcs, name, bases))
        logger.study(
            """namespace has data_base_class__? {}""".format(
                namespace.get("__data_base_class__", False)))
        if not namespace.get("__data_base_class__", False):
            if "index" not in namespace:
                logger.alert("""
                Provide class attribute 'index':
                A dict mapping the name of an index variable to its description.
                The names will be used to name the dataframe index,
                and the description to provide documentation.
                """)
                raise TypeError(
                    "Missing class attribute 'index' in class definition of '{}'"\
                    .format(name))
            if "measurements" not in namespace:
                logger.alert("""
                Provide class attribute 'measurements':
                A dict mapping the name of measurement variable to its description.
                The names will be used to name the dataframe columns, 
                and the description to provide documentation.
                """)
                raise TypeError(
                    "Missing class attribute 'measurements' in class definition of '{}'"\
                    .format(name))

        return super().__new__(
            mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace):
        """..."""
        super().__init__(
            name, bases, namespace)


class Data(
        WithFields,
        metaclass=DataClassMeta):
    """A base class to define DataClasses."""

    __metaclass_base__ = True

    data = Field("""
    A list of dicts that can be used to construct a pandas.DataFrame.
    Each dict should have keys for all the index and measurement columns of
    the dataframe. An exception will be raised if any columns are missing.
    """,
        __type__=list,
        __required__=True)
    label = Field(
        """
        A string to name a Data instance. 
        """,
        __type__=str,
        __required__=True)
    provenance = Field(
        """
        Description of the origin of this data.
        """,
        __type__=object,
        __default_value__="Unknown")

    def __init__(self,
            data,
            *args, **kwargs):
        """..."""
        for d in data:
            for i in self.index.keys():
                if i not in d.keys():
                    raise ValueError(
                        """Missing data index '{}' in dict {}""".format(i, d))
            for m in self.measurements.keys():
                if m not in d.keys():
                    raise ValueError(
                        """Missing measurement '{}' in dict {}""".format(m, d))

        kwargs["data"] = data

        super().__init__(
            *args, **kwargs)

    @property
    def dataframe(self):
        """
        Data as a dataframe.
        """
        return pd.DataFrame(self.data)\
                 .set_index(list(self.index))

    @property
    def loc(self):
        """..."""
        return self.dataframe.loc

    @property
    def iloc(self):
        """..."""
        return self.dataframe.iloc

    @property
    def what(self):
        """Needs improvement"""
        return "{}\n Provided by {}"\
            .format(
                self.__class__.__doc__.strip(),
                self.provenance)
