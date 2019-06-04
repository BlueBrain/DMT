"""
Prototype for Data.
"""
from abc import ABCMeta
import pandas as pd
from dmt.v2.tk.journal import Logger
from dmt.v2.tk.field import Field, WithFields, FieldMeta


def is_data_base_class(cls):
    """???"""
    return getattr(cls, "__data_base_class__", False)

class DataClassConstructor(type):
    """
    A meta class to construct Data classes
    """

    def __new__(mcs, name, bases, namespace):
        """..."""
        logger = Logger(client="DataClassConstructor", level="STUDY")
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
        metaclass=DataClassConstructor):
    """A base class to define DataClasses."""

    __data_base_class__ = True

    label = Field("""
        A string to name a Data instance
        """,
        __type__=str,
        __required__=False)
    data = Field("""
        A list of dicts that can be used to construct a pandas.DataFrame.
        """,
        __type__=list,
        __required__=True)


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

