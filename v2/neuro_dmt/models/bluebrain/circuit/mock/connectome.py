"""
The connectome of a circuit.
"""

import numpy as np
import pandas as pd
from bluepy.v2.enums import Direction
from bluepy.exceptions import BluePyError
from dmt.tk.field import Field, WithFields, lazyfield
from dmt.tk.journal import Logger
from .synapse import Synapse

log = Logger(client=__file__)

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
    cells = Field(
        """
        `pandas.DataFrame` of cells for the circuit containing this
        `Connectome`.
        """)
    connections = Field(
        """
        `pandas.DataFrame<pre_synaptic_cell_gid,
                          post_synaptic_cell_gid,
                          synapse_count>`
        """)
    cache_synapses = Field(
        """
        An object that can cache synapses as they are read.
        If not provided, synapses will not be cached.
        """,
        __required__=False)

    @lazyfield
    def afferent_connections(self):
        """
        List of 2-tuples giving afferent cell gid and synapse count,
        for each  cell in a circuit.  We can build other connectome properties
        from this list.
        """
        return self.connections.set_index("post_synaptic_cell_gid")

    @lazyfield
    def efferent_connections(self):
        """
        dict mapping gids to 2-tuples giving efferent cell gid and synapse count,
        for each cell in a circuit. We will set this field to an empty dict, and
        fill it lazily.
        """
        return self.connections.set_index("pre_synaptic_cell_gid")

    @classmethod
    def _get_properties(cls, dataframe, properties):
        """
        Get only columns in list 'properties' from pandas DataFrame.
        """
        return dataframe[properties] if properties else dataframe.index.values

    @classmethod
    def empty_synapse_holder(cls):
        """
         A pandas data-frame containing the synapses defining this Connectome.
         Connectome.synapses will be set lazily.
        """
        return\
            pd.DataFrame(dict(
                pre_gid=np.array([], dtype=np.int32),
                post_gid=np.array([], dtype=np.int32),
                synapse_index=np.array([], dtype=np.int32)))\
              .set_index(
                  ["pre_gid", "post_gid", "synapse_index"],
                  drop=False)

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

    @lazyfield
    def gids(self):
        """
        All the gids, loaded lazily
        """
        return\
            np.sorted(np.concatenate([
                self.connections.pre_synaptic_cell_gids.unique(),
                self.connections.post_synaptic_cell_gids.unique()]))

    # @lazyfield
    # def connections(self):
    #     """
    #     An array of (pre_gid, post_gid, number_synapses) tuples
    #     """
    #     return\
    #         pd.DataFrame(
    #             np.array([
    #                 (pre_gid, post_gid, strength)
    #                 for post_gid, adjacency in enumerate(self.afferent_adjacency)
    #                 for pre_gid, strength in adjacency]),
    #             columns=["pre_synaptic_cell_gid",
    #                      "post_synaptic_cell_gid",
    #                      "strength"])

    @lazyfield
    def synapse_count(self):
        """..."""
        return\
            pd.Series(
                self.connections.synapse_count.values,
                name="synapse_count",
                index=pd.MultiIndex.from_tuples(
                    [(pre, post)
                     for pre, post) in zip(
                             self.connections.pre_synaptic_cell_gid,
                             self.connections.post_synaptic_cell_gid)],
                names=["pre_synaptic_cell_gid", "post_synaptic_cell_gid"]))

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
        return self.connections\
                   .query("post_synaptic_cell_gid==@gid")\
                   .pre_synaptic_cell_gid\
                   .values

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
        return\
            self._get_properties(
                self._get_synapses(post_gid=gid),
                properties=properties)

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
        return\
            self.efferent_connections\
                .loc[gid]\
                .post_synaptic_cell_gid

    def efferent_synapses(self, gid, properties=None):
        """
        Get efferent synapses for given 'gid'.

        Arguments:
        ~   gid: pre-synaptic neuron's GID
        ~   properties: None / 'Synapse' property / list of 'Synapse' properties

        Return:
        ~   List of synapse IDs if 'properties' is None;
        ~   pandas.Series indexed by synapse IDs if 'properties' is scalar;
        ~   pandas.DataFrame indexed by synapse IDs if 'properties' is list.
        """
        return\
            self._get_properties(
                self._get_synapses(pre_gid=gid),
                properties=properties)

    def _get_pair_synapse_count(self, pre_gid, post_gid):
        """
        Get number of synapses pre_gid to post_gid.
        """
        return\
            self.synapse_count.loc[(pre_gid, post_gid)]

    def _read_synapses(self, pre_gid=None, post_gid=None):
        """
        Read synapses connecting pre_gid to post_gid.
        The mock-circuit knows only the pre_gid and post_gid of synapses.
        We will read other properties when we have implemented them.
        """
        assert not (pre_gid is None and post_gid is None)

        if post_gid is None:
            return\
                pd.concat([
                    self._read_synapses(pre_gid, _post_gid)
                    for _post_gid in self.efferent_gids(pre_gid)])
        if pre_gid is None:
            return\
                pd.concat([
                    self._read_synapses(_pre_gid, post_gid)
                    for _pre_gid in self.afferent_gids(post_gid)])
        return\
            pd.DataFrame({
                "pre_gid": pre_gid,
                "post_gid": post_gid,
                "synapse_index": np.arange(
                    self._get_pair_synapse_count(pre_gid, post_gid))})\
              .set_index(
                  ["pre_gid", "post_gid", "synapse_index"],
                  drop=False)

    def _get_cached(self, pre_gid=None, post_gid=None):
        """
        Get cached synapses pre_gid --> post_gid
        """
        try:
            synapse_cache = self.cache_synapses
        except AttributeError as error:
            log.info(
                "{} instance does not cache synapses: {}."\
                .format(self.__class__, error))
            raise KeyError(
                "Synapses {}-->{} not found in cache."\
                .format(pre_gid, post_gid))
        return synapse_cache.get(pre_gid=pre_gid, post_gid=post_gid)

    def _cache(self, synapses, pre_gid=None, post_gid=None):
        """
        Save some synapses
        """
        try:
            synapses_cache = self.cache_synapses
        except AttributeError as error:
            log.info(
                "{} instance does not cache synapses: {}."\
                .format(self.__class__, error))
            return None
        return synapses_cache.append(synapses, pre_gid, post_gid)

    def _get_synapses(self, pre_gid=None, post_gid=None):
        """
        Get synapses pre_gid --> post_gid.
        """
        try:
            return self._get_cached(pre_gid, post_gid)
        except KeyError:
            log.info(
                log.get_source_info(),
                "No cached synapses {}==>{}".format(
                    pre_gid if pre_gid is not None else "",
                    post_gid if post_gid is not None else ""))
            pass
        synapses_pre_post =\
            self._read_synapses(pre_gid=pre_gid, post_gid=post_gid)
        self._cache(synapses_pre_post, pre_gid=pre_gid, post_gid=post_gid)
        return synapses_pre_post

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
        return\
            self._get_properties(
                self._get_synapses(pre_gid, post_gid),
                properties=properties)

    def _filter_connected(self,
            gid,
            candidate_gids,
            direction=Direction.AFFERENT):
        """
        Filter gids from  list of 'possible_pre_gids' that make a synapse
        onto the post-synaptic neuron with given 'gid'.
        """
        connected_gids =\
            self.afferent_gids(gid)\
            if direction == Direction.AFFERENT else\
               self.efferent_gids(gid)
        return\
            candidate_gids[
                np.in1d(candidate_gids, connected_gids)]
                
    def pathway_synapses(self,
            pre_gids=np.array([]),
            post_gids=np.array([]),
            properties=None):
        """
        Synapses in the pathway {pre_gids} -> {post_gids}.
        """
        if len(pre_gids) == 0 and len(post_gids) == 0:
            raise NotImplementedError(
                "There may be too many synapses to handle.")
        def __stacked(datas):
            """
            Stack either a list of arrays, or dataframes
            """
            if len(datas) == 0:
                return\
                    self.empty_synapse_holder() if properties\
                    else np.array([], np.integer)
            return (pd.concat if properties else np.hstack)(datas)

        if len(pre_gids) == 0:
            return __stacked([
                self.afferent_synapses(gid)
                for gid in post_gids])
        if len(post_gids) == 0:
            return __stacked([
                self.efferent_synapses(gid)
                for gid in pre_gids])
        return\
            __stacked([
                self.pair_synapses(_pre_gid, _post_gid, properties=properties)
                for _post_gid in post_gids
                for _pre_gid in self._filter_connected(_post_gid, pre_gids)])
    
    def iter_connections(self,
            pre=None, post=None,
            unique_gids=False,
            shuffle=False,
            return_synapse_ids=False,
            return_synapse_count=False):
        """
        Iterate through `pre` -> `post` connections.

        Args:
            pre: presynaptic cell group
            post: postsynaptic cell group
            unique_gids: if True, no gid would be used more than once
            shuffle: if True, result order would be (somewhat) randomised
            return_synapse_count: ifTrue, synapse count is added to yield result
            return_synapse_ids: if True, synapse ID list is added to yield result

        `return_synapse_count` and `return_synapse_ids` are mutually exclusive.

        Yields:
            (pre_gid, post_gids, synapse_ids) if return_synapse_ids == True;
            (pre_gid, post_gid, synapse_count) if return_synapse_count == True;
            (pre_gid, post_gid) otherwise.
        """
        if return_synapse_ids and return_synapse_count:
            raise BluePyError(
                """
                `{}_count` and `{}_ids` are mutually exclusive
                """.format("count", "ids"))
        pre_synaptic_cells = self.cells.get(pre)
        post_synaptic_cells = self.cells.get(post)

        

        for pre_synaptic_gid in pre_synaptic_cells.index:
            efferent_connections =\
                self.connections\
                    .xs(pre_synaptic_gid,
                        level="pre_synaptic_cell_gid")
            connections =\
                self.connections\
                    .xs(pre_synaptic_gid, level="pre_synaptic_cell_gid")\
                    .reindex(post_synaptic_cells.index)\
                    .dropna()
            for post_synaptic_gid, connection, in connections.iterrows():
                yield (pre_synaptic_gid, post_synaptic_gid, connection.strength)

        for pre_gid in pre_synaptic_cells.index:
            for post_gid, cnxn in self.connections\
                                      .xs(pre_gid, level="pre_synaptic_cell_gid")\
                                      .reindex(post_synaptic_cells.index)\
                                      .dropna()\
                                      .iterrows():
                yield (pre_gid, post_gid, cnxn.strength)
        def efferent_connections(pre_gid):
            return\
                self.connections\
                    .xs(pre_gid, level="pre_synaptic_cell_gid")
        return(
            (pre_gid, post_gid, cnxn.strength)
            for pre_gid in pre_synaptic_cells.index
            for post_gid, cnxn in efferent_connections(pre_gid).iterrows())


        raise NotImplementedError

