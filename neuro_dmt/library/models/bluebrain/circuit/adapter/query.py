# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
A `BlueBrainCircuitAdapter` will need to handle spatial queries on a
`BlueBrainCircuitModel`. Here we implement helpers towards that endeavor.
"""

from dmt.tk.collections.data import make_hashable
from dmt.tk.field import Field, lazyfield, WithFields

class QueryDB(WithFields):
    """
    Cache of data associated with a circuit query, that the adapter will use.
    """
    method_to_memoize = Field(
        """
        A callable to get values to cache.
        """)
    def __init__(self, method_to_memoize):
        """..."""
        super().__init__(
            method_to_memoize=method_to_memoize)

    @lazyfield
    def store(self): return {}

    @staticmethod
    def _hashable(query_dict):
        """..."""
        return tuple(sorted(
           [(key, make_hashable(value))
            for key, value in query_dict.items()
            if value is not None],
            key=lambda key_value: key_value[0]))

    @staticmethod
    def _hashed(query_dict):
        """..."""
        return\
            hash(QueryDB._hashable(query_dict))

    def __call__(self,
            circuit_model,
            query_dict):
        """
        Call Me.
        """
        if circuit_model not in self.store:
            self.store[circuit_model] = {}

        cache_circuit_model = self.store[circuit_model]
        hash_query = self._hashable(query_dict)
        if hash_query not in cache_circuit_model:
            cache_circuit_model[hash_query] =\
                self.method_to_memoize(circuit_model, query_dict)

        return cache_circuit_model[hash_query]


class SpatialQueryData(WithFields):
    """
    Define data critical to answer spatial queries.
    """
    ids = Field(
        """
        Ids of voxels that passed the spatial query filter.
        """)
    positions = Field(
        """
        Physical space positions for the voxel with ids in self.ids.
        """)
    cell_gids = Field(
        """
        pandas.Series that provides the gids of all the cells in voxels
        that passed the spatial query filter, indexed by the corresponding
        voxel ids.
        """)
