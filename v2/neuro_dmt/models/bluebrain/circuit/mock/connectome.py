"""
The connectome of a circuit.
"""

import numpy as np
from dmt.tk.field import Field, WithFields, lazy

class Connection(WithFields):
    """
    A connection between two cells.
    A Connection instance will make sense only when defined for a circuit, as
    cells are tracked by their gid.
    """
    pre_gid = Field(
        """
        gid of the pre-synaptic cell.
        """)
    post_gid = Field(
        """
        gid of the post-synaptic cell.
        """)
    synapse_count = Field(
        """
        number of synapses in this Connection.
        """)

class Connectome(WithFields):
    """
    The connectome of a circuit.
    """
    afferent_adjacency = Field(
        """
        List of 2-tuples giving afferent cell gid and synapse count,
        for each  cell in a circuit.  We can build other connectome properties
        from this list.
        """)
    efferent_adjacency = Field(
        """
        dict mapping gids to 2-tuples giving efferent cell gid and synapse count,
        for each cell in a circuit. We will set this field to an empty dict, and
        fill it lazily.
        """,
        __default_value__={})

    @lazy
    def gids(self):
        """
        All the gids, loaded lazily
        """
        return np.array(range(len(self.afferent_adjacency)), dtype=int)

    def afferent_gids(self, gid):
        """
        All the incoming connected cell gids of the cell with 'gid'.
        """
        return self.afferent_adjacency[gid][:, 0]

    def efferent_gids(self, gid):
        """
        All the outcoming connected cell gids of the cell with 'gid'.
        """

        def __contains(xs, y):
            """
            Is 'y' in 'xs', given xs is sorted?
            """
            i = np.searchsorted(xs, y)
            return i < len(xs) and xs[i] == y

        if gid not in self.efferent_adjacency:
            self.efferent_adjacency[gid] = np.array([
                post_gid for post_gid in self.gids
                if __contains(self.afferent_gids(post_gid), gid)])
        return self.efferent_adjacency[gid]

    def pathway_synapses(self, pre_gids, post_gids, properties=None):
        """
        Synapses in the pathway {pre_gids} -> {post_gids}.
        """
        raise NotImplementedError

    def iter_connections(self, pre_gids, post_gids, unique_gids, shuffle):
        """
        Iterate through {pre_gids} -> {post_gids} connections.
        """
        raise NotImplementedError
