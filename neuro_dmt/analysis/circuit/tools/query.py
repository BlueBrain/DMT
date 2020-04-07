# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published 
# by the Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT 
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for 
# more details.

# You should have received a copy of the GNU Lesser General Public License 
# along with DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Query to analyze circuits.
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


class PathwayQuery(WithFields):
    """
    Defines a pathway query.
    """
    post_synaptic_cell_group = Field(
        """
        Either a cell type described by a `Mapping` or `pandas.Series`,
        or a collection of cells as a `pandas.DataFrame`,
        or a collection of gids as a `np.ndarray, list, Iterable`,
        or a named target
        """)
    pre_synaptic_cell_group = Field(
        """
        Either a cell type described by a `Mapping` or `pandas.Series`,
        or a collection of cells as a `pandas.DataFrame`,
        or a collection of gids as a `np.ndarray, list, Iterable`,
        or a named target
        """)
    direction = Field(
        """
        `afferent` or `efferent`
        """)

    def __repr__(self):
        return "{}".format(self.field_dict)

    @lazyfield
    def cell_group(self):
        """
        Determine the primary and secondary synaptic cell types in the query.
        Cell type of the primary, with respect to the direction of measurement,
        synaptic side sides.
        If the measurement will be made in the afferent direction, the primary
        cell type will be that of the post-synaptic cells, and the secondary
        that of the pre-synatic cells.
        If the measurement will be made in the efferent direction, the primary
        cell type will be that of the pre-synaptic cells, and the secondary
        that of the post-synaptic cells.s
        """
        if self.direction == terminology.direction.afferent:
            return Record(
                primary=self.post_synaptic_cell_group,
                secondary=self.pre_synaptic_cell_group)
        if self.direction == terminology.direction.efferent:
            return Record(
                primary=self.pre_synaptic_cell_group,
                secondary=self.post_synaptic_cell_group)
        raise ValueError(
            "Unknown measurement direction {}.".format(self.direction))

    @lazyfield
    def secondary_synaptic_side(self):
        if self.direction == terminology.direction.afferent:
            return "pre_synaptic_cell"
        if self.direction == terminology.direction.efferent:
            return "post_synaptic_cell"
        raise ValueError(
            "Unknown measurement direction {}.".format(self.direction))

    @lazyfield
    def primary_synaptic_side(self):
        if self.direction == terminology.direction.afferent:
            return "post_synaptic_cell"
        if self.direction == terminology.direction.efferent:
            return "pre_synaptic_cell"
        raise ValueError(
            "Unknown measurement direction {}.".format(self.direction))


