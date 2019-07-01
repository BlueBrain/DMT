"""
The connectome of a circuit.
"""

import numpy as np
import pandas as pd
from dmt.tk.field import Field, WithFields, lazy
from .synapse import Synapse


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


MAXNEURONSYNS = 10000#maximum number of efferent synapses of a (pre-) neuron
MAXCONNSYNS = 100#max number of synapses in pre --> post connection.

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

    @classmethod
    def empty_synapse_holder(cls):
        """
         A pandas data-frame containing the synapses defining this Connectome.
         Connectome.synapses will be set lazily.
        """
        dataframe =\
            pd.DataFrame(dict(
                pre_gid=np.array([], dtype=np.int32),
                post_gid=np.array([], dtype=np.int32)))
        return dataframe

    def __init__(self,
            *args, **kwargs):
        """
        Initialize
        1. A pandas data-frame containing the synapses defining this Connectome.
        ~  Connectome.synapses will be set lazily.
        2. Pass on to WithFields for everything else.
        """
        self._synapses =\
            self.empty_synapse_holder()
        self._pre_post_index = {}#to track where pre_gid-->post_gid synapses are
        super().__init__(
            *args, **kwargs)

    @lazy
    def gids(self):
        """
        All the gids, loaded lazily
        """
        return np.array(range(len(self.afferent_adjacency)), dtype=int)

    @lazy
    def connections(self):
        """
        An array of (pre_gid, post_gid, number_synapses) tuples
        """
        return np.array(
            [(pre_gid, post_gid, strength)
             for post_gid in self.gids
             for pre_gid, strength in self.afferent_adjacency])

    def synapse_properties(self,
            synapse_ids,
            properties):
        """
        Synapse properties as pandas DataFrame.

        Arguments:
        ~   synapse_ids: array-like of synapse IDs.
        ~   properties: 'Synapse' property or list of 'Synapse' properties.

        Return:
        ~   pandas.Series indexed by synapse IDs if 'properties' is scalar.
        ~   pandas.DataFrame indexed by synapse IDs if 'properties' is list.
        """
        raise NotImplementedError

    def synapse_positions(self,
            synapse_ids,
            side,
            kind):
        """
        Synapse positions as pandas.DataFrame

        Arguments:
        ~   synapse_ids: array-like of synapse IDs
        ~   side: 'pre' or 'post'
        ~   kind: 'center' or 'contour'

        Return:
        ~   pandas.DataFrame with ('x', 'y', 'z') columns indexed by synapse IDs.
        """
        raise NotImplementedError

    def afferent_gids(self, gid):
        """
        All the incoming connected cell gids of the cell with 'gid'.
        """
        return self.afferent_adjacency[gid][:, 0]

    def afferent_synapses(self, gid, properties=None):
        """
        Get afferent synapses for given 'gid'.

        Arguments:
        ~   gid: post-synaptic neuron's GID
        ~   properties: None / 'Synapse' property / list of 'Synapse' properties

        Return:
        ~   List of synapse IDs if 'properties' is None;
        ~   pandas.Series indexed by synapse IDs if 'properties' is scalar;
        ~   pandas.DataFrame indexed by synapse IDs if 'properties' is list.
        """
        return self.pathway_synapses([], [gid], properties)

    @staticmethod

    def __in_sorted(xs, y):
        """
        Is 'y' in sorted array xs?
        """
        i = np.searchsorted(xs, y)
        return i < len(xs) and xs[i] == y

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
                if self.__in_sorted(self.afferent_gids(post_gid), gid)])
        return self.efferent_adjacency[gid]

    def efferent_synapses(self, gid, properties=None):
        """
        Get efferent synapses for given 'gid'.

        Arguments:
        ~   gid: post-synaptic neuron's GID
        ~   properties: None / 'Synapse' property / list of 'Synapse' properties

        Return:
        ~   List of synapse IDs if 'properties' is None;
        ~   pandas.Series indexed by synapse IDs if 'properties' is scalar;
        ~   pandas.DataFrame indexed by synapse IDs if 'properties' is list.
        """
        return self.pathway_synapses([gid], [], properties)

    def _get_pair_synapse_count(self, pre_gid, post_gid):
        """
        Get number of synapses pre_gid to post_gid.
        """
        pre_gids = self.afferent_gids(post_gid)
        i = np.searchsorted(pre_gids, pre_gid)
        return 0 if i >= len(pre_gids) or pre_gids[i] != pre_gid\
            else self.afferent_adjacency[post_gid][i, 1]

    def _append_synapses(self, pre_gid, post_gid):
        """
        Append synapses to the synapse holder, self._synapses.
        """
        if pre_gid not in self._pre_post_index:
            self._pre_post_index[pre_gid] = {}

        if post_gid not in self._pre_post_index[pre_gid]:
            n_synapses =\
                self._synapses.shape[0]
            count =\
                self._get_pair_synapse_count(pre_gid, post_gid)
            pre_post_synapses =\
                pd.DataFrame({
                    "pre_gid": np.repeat(pre_gid, count),
                    "post_gid": np.repeat(post_gid, count)})
            self._synapses =\
                self._synapses.append(
                    pre_post_synapses,
                    sort=True)
            self._pre_post_index[pre_gid][post_gid] =\
                slice(
                    n_synapses,
                    n_synapses + pre_post_synapses.shape[0])

        return self._pre_post_index[pre_gid][post_gid]

    def _append_afferent_synapses(self, gid):
        """
        Append all the afferent synapses of 'gid' to the synapse holder.
        DEPRECATED, REMOVE IT
        """
        if gid not in self._pre_post_index:
            pre_post_synapses =\
                    pd.DataFrame(
                        {"pre_gid": np.hstack([
                            np.repeat(pre_gid, count)
                            for pre_gid,count in self.afferent_adjacency[gid]]),
                         "post_gid": gid})
            n_synapses =\
                self._synapses.shape[0]
            self._pre_post_index[gid] =\
                slice(
                    n_synapses,
                    n_synapses + pre_post_synapses.shape[0])
            self._synapses =\
                self._synapses.append(
                    pre_post_synapses,
                    sort=True)
        return self._synapses

    def pair_synapses(self, pre_gid, post_gid, properties=None):
        """
        Get synapses corresponding to 'pre_gid' --> 'post_gid' connection.

        Arguments:
        pre_gid: presynaptic GID
        post_gid: postsynaprtic GID
        properties: None / 'Synapse' property / list of 'Synapse' properties

        Return:
        ~   List of synapse IDs if 'properties' is None;
        ~   pandas.Series indexed by synapse IDs if 'properties' is scalar;
        ~   pandas.DataFrame indexed by synapse IDs if 'properties' is list.
        """
        pre_post_slice =\
            self._append_synapses(pre_gid, post_gid)
        return\
            self._synapses.iloc[pre_post_slice]

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
