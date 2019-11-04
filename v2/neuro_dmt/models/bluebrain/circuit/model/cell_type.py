"""
Abstraction of a cell type.
"""
import functools
from collections import OrderedDict
import pandas as pd
from dmt.tk.field import Field, LambdaField, lazyfield, WithFields

class CellType(WithFields):
    """
    How do we specify the type of a cell.
    """
    value = Field(
        """
        Ordered key-value pairs where the keys are named properties of a cell,
        specified for this `CellType` instance by the values.
        The value may be one of the values assumed by the cell property or
        a list of such values.
        """)
    def __init__(self, value, *args, **kwargs):
        """..."""
        if isinstance(value, OrderedDict):
            super().__init__(value=value, *args, **kwargs)

    def __init__(self, cell_instance=None, *args, **kwargs):
        """
        Arguments
        ----------------
        cell_instance :: Either a pandas.Series with entries for each
        element in `self.specifier`, or an object with an attribute for each
        element in `self.specifier`.
        """
        def alarm(wtf):
            return TypeError(
                """
                {}.
                To initialize a `CellType` provide the cell type specifier:
                1. By either passing a pandas.Series representing a cell
                instance whose properties will become the specifiers.
                2. Or by passing 'specifier' as a keyword argument.
                """.format(wtd))

        if cell_instance is not None:
            if "specifier" in kwargs:
                raise alarm(
                    """
                    __init__ got multiple values for field 'specifier'.
                    One value passed in as the cell instance: {},
                    and another in variable keyword arguments: {}
                    """.format(
                        cell_instance,
                        kwargs["specifier"]))
            specifier = tuple(cell_instance.index.values)
        else:
            if "specifier" not in kwargs:
                raise alarm(
                    """
                    __init__ missing argument to determine `specifier` from.
                    """)
        super().__init__(
            specifier = specifier,
            **kwargs)

    @lazyfield
    def specifier(self):
        """
        List of cell properties that determine this cell's type.
        """
        return self.value.index.values

    def sample(self, circuit_model, size=20):
        """
        Sample cells from circuit model.
        """
        circuit_model.cells

    @staticmethod
    def get_specifier(cell_type):
        """
        Get specifiers for a given cell type.

        Arguments
        --------------
        `cell_type`: a Mapping like an OrderedDict, or a pandas.Series
        """
        if isinstance(cell_type, OrderedDict):
            return tuple(cell_type.keys())
        if isinstance(cell_type, pd.Series):
            return tuple(cell_type.index.values)
        raise TypeError(
            """
            Can extract cell type specifiers from an `OrderedDict`
            or a `pandas.Series`, received a {}
            """.format(type(cell_type)))

    @staticmethod
    def pathway(
            pre_synaptic_cell_type,
            post_synaptic_cell_type):
        """
        A `Pathway` like object from a specified cell type on the
        pre-synaptic side and a specified cell type on  the 
        post-synaptic side.
        """
        def _at(pos, cell_type):
            return pd.Series(
                cell_type.values,
                index=pd.MultiIndex.from_tuples([
                    (pos, value)
                    for value in cell_type.index.values]))
        return\
            _at("pre_synaptic", pre_synaptic_cell_type).append(
                _at("post_synaptic", post_synaptic_cell_type))

    @staticmethod
    def memoized(instance_method):
        """
        Memoize the results of a method that takes
        cell type specifiers as arguments.
        """
        instance_method._cache = {}

        @functools.wraps(instance_method)
        def effective(instance, cell_type_specifier):
            """..."""
            if cell_type_specifier not in instance_method._cache:
                instance_method._cache[cell_type_specifier] =\
                    instance_method(instance, cell_type_specifier)
            return instance_method._cache[cell_type_specifier]

        return effective


