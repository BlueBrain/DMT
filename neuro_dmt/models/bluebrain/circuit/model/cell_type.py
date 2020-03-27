# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Abstraction of a cell type.
"""
import functools
from collections.abc import Mapping
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
        if value is None:
            raise TypeError(
                """
                __init__ called with argument `value` {}
                """.format(value))
        try:
            value_as_series = pd.Series(value)
            super().__init__(value=value_as_series, *args, **kwargs)
        except ValueError as error:
            raise TypeError(
                """
                __init__called with {} instance that could not be case to a
                pandas Series.
                Original error:
                \t{}
                """.format(
                    type(value),
                    error))

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
        raise NotImplementedError

    @staticmethod
    def get_specifier(cell_type):
        """
        Get specifiers for a given cell type.

        Arguments
        --------------
        `cell_type`: a Mapping like an OrderedDict, or a pandas.Series
        """
        if isinstance(cell_type, Mapping):
            return frozenset(cell_type.keys())
        if isinstance(cell_type, pd.Series):
            return frozenset(cell_type.index.values)
        raise TypeError(
            """
            Can extract cell type specifiers from an `Mapping`
            or a `pandas.Series`, received a {}
            """.format(type(cell_type)))

    @staticmethod
    def pathway(
            pre_synaptic_cell_type,
            post_synaptic_cell_type,
            multi_indexed=True):
        """
        A `Pathway` like object from a specified cell type on the
        pre-synaptic side and a specified cell type on  the 
        post-synaptic side.
        """
        def _at(pos, cell_type):
            if multi_indexed:
                return pd.Series(
                    cell_type.value.values,
                    index=pd.MultiIndex.from_tuples([
                        (pos, variable)
                        for variable in cell_type.value.index]))
            return pd.Series(
                cell_type.value.values,
                index=pd.Index(
                    "{}_{}".format(pos, variable)
                    for variable in cell_type.value.index))

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
        def effective(instance,
            cell_type_specifier=None,
            cell_types=None):
            """..."""
            if (cell_type_specifier is not None
                and cell_type_specifier not in instance_method._cache):
                instance_method._cache[cell_type_specifier] =\
                    instance_method(instance, cell_type_specifier, cell_types)
            return instance_method._cache[cell_type_specifier]

        return effective


