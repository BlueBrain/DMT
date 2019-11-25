"""
A `BlueBrainCircuitAdapter` will need to handle spatial queries on a
`BlueBrainCircuitModel`. Here we implement helpers towards that endeavor.
"""

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
    def _hashed(query_dict):
        """..."""
        def _hashable(xs):
            """
            Get hash for a query.
            """
            try:
                _ = hash(xs)
                return xs
            except TypeError:
                return ';'.join(str(x) for x in xs)
            raise RuntimeError(
                "Execution of _hashed(...) should not reach here.")

        key_values =(
            (key, _hashable(value))
            for key, value in query_dict.items()
            if value is not None)
        return\
            hash(tuple(sorted(
                key_values,
                key=lambda key_value: key_value[0])))

    def __call__(self,
            circuit_model,
            query_dict):
        """
        Call Me.
        """
        if circuit_model not in self.store:
            self.store[circuit_model] = {}

        cache_circuit_model = self.store[circuit_model]
        hash_query = self._hashed(query_dict)
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
