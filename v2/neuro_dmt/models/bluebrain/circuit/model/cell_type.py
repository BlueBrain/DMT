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
        """
        Arguments
        -----------
        value : Mapping or pandas.Series
        """
        super().__init__(value=pd.Series(value), *args, **kwargs)

    @lazyfield
    def specifier(self):
        """
        List of cell properties that determine this cell's type.
        """
        return self.get_specifier(self.value)

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
            return frozenset(cell_type.keys())
        if isinstance(cell_type, pd.Series):
            return frozenset(cell_type.index.values)
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
                cell_type.value.values,
                index=pd.MultiIndex.from_tuples([
                    (pos, variable)
                    for variable in cell_type.value.index]))
        return\
            _at("pre_synaptic", CellType(pre_synaptic_cell_type)).append(
                _at("post_synaptic", CellType(post_synaptic_cell_type)))


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


