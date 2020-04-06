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
The connectome of a circuit.
"""

from tqdm import tqdm
import numpy as np
import pandas as pd
from dmt.tk.field import Field, WithFields, lazyfield
from dmt.tk.journal import Logger
from neuro_dmt import terminology
from .synapse import Synapse

LOGGER = Logger(client=__file__)

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
        Instance of cell collection on which this `Connectome` has been defined.
        """)
    connections = Field(
        """
        A pandas.DataFrame <pre_gid, post_gid, synapse_count>...
        """)
    cache_synapses = Field(
        """
        An object that can cache synapses as they are read.
        If not provided, synapses will not be cached.
        """,
        __required__=False)

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
    def pre_gids(self):
        return\
            np.sort(self.connections.pre_gid.unique())
    @lazyfield
    def post_gids(self):
        return\
            np.sort(self.connections.post_gid.unique())
    @lazyfield
    def gids(self):
        """
        All the gids, loaded lazily
        """
        return\
            np.unique(np.concatenate([self.pre_gids, self.post_gids], axis=0))

    # @lazyfield
    # def connections(self):
    #     """
    #     An array of (pre_gid, post_gid, number_synapses) tuples
    #     """
    #     LOGGER.info(
    #         LOGGER.get_source_info(),
    #         "Loading connections")
    #     cnxns =\
    #         pd.DataFrame(
    #             np.array(
    #                 [(pre_gid_and_strength[0], post_gid, pre_gid_and_strength[1])
    #                  for post_gid in tqdm(self.gids)
    #                  for pre_gid_and_strength in self.afferent_adjacency[post_gid]]),
    #             columns=["pre_synaptic_cell_gid",
    #                      "post_synaptic_cell_gid",
    #                      "strength"])
    #     LOGGER.info(
    #         LOGGER.get_source_info(),
    #         "DONE")
    #     return cnxns


    @lazyfield
    def afferent_connections(self):
        """..."""
        return\
            self.connections\
                .set_index("post_gid")\
                .sort_index()
    @lazyfield
    def afferent_adjacency(self):
        """
        List of 2-tuples giving afferent cell gid and synapse count,
        for each  cell in a circuit.  We can build other connectome properties
        from this list.
        """
        raise NotImplementedError

    @lazyfield
    def efferent_adjacency(self):
        """
        dict mapping gids to 2-tuples giving efferent cell gid and synapse count,
        for each cell in a circuit. We will set this field to an empty dict, and
        fill it lazily.
        """
        raise NotImplementedError


    @lazyfield
    def efferent_connections(self):
        """..."""
        return\
            self.connections\
                .set_index("pre_gid")\
                .sort_index()

    @lazyfield
    def synapse_counts(self):
        """..."""
        LOGGER.info("Loading synapse counts.")
        levels_index =[
            "pre_gid", "post_gid"]
        return\
            self.connections\
                .set_index(levels_index)\
                .synapse_count\
                .sort_index(level=levels_index)

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
        return\
            self.afferent_connections.loc[gid].pre_gid.values

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
            self.efferent_connections.loc[gid].post_gid.values

        # def __contains(xs, y):
        #     """
        #     Is 'y' in 'xs', given xs is sorted?
        #     """
        #     i = np.searchsorted(xs, y)
        #     return i < len(xs) and xs[i] == y

        # if gid not in self.efferent_adjacency:
        #     self.efferent_adjacency[gid] = np.array([
        #         post_gid for post_gid in self.gids
        #         if self.__in_sorted(self.afferent_gids(post_gid), gid)])
        # return self.efferent_adjacency[gid]

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
            self.synapse_counts.loc[(pre_gid, post_gid)]
        # pre_gids = self.afferent_gids(post_gid)
        # i = np.searchsorted(pre_gids, pre_gid)
        # return 0 if i >= len(pre_gids) or pre_gids[i] != pre_gid\
        #     else self.afferent_adjacency[post_gid][i, 1]

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
            LOGGER.info(
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
            LOGGER.info(
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
            LOGGER.info(
                LOGGER.get_source_info(),
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
            direction=terminology.direction.afferent):
        """
        Filter gids from  list of 'possible_pre_gids' that make a synapse
        onto the post-synaptic neuron with given 'gid'.
        """
        connected_gids =\
            self.afferent_gids(gid)\
            if direction == terminology.bluebrain.afferent else\
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

    def _resolve_gids(self, group_cells):
        cells_subset = self.cells.get(group_cells)
        if isinstance(cells_subset, pd.Series):
            return group_cells
        return cells_subset.index.values

    def iter_connections(self,
            pre=None, post=None,
            unique_gids=False,
            shuffle=False,
            return_synapse_ids=False,
            return_synapse_count=False):
        """
        Iterate through pre -> post connections.
        """
        result = lambda xyz: xyz if return_synapse_count else xyz[0:2]
        if pre is None:
            if post is None:
                for _, connection in self.connections.iterrows():
                    yield result((
                        connection.pre_gid,
                        connection.post_gid,
                        connection.synapse_count))
            else:
                for post_gid in self._resolve_gids(post):
                    afferent_connections =\
                        self.afferent_connections.loc[post_gid]
                    for _, connection in afferent_connections.iterrows():
                        yield result((
                            connection.pre_gid,
                            post_gid,
                            connection.synapse_count))
        elif post is None:
            for pre_gid in self._resolve_gids(pre):
                efferent_connections =\
                    self.efferent_connections.loc[pre_gid]
                for _, connection in efferent_connections.iterrows():
                    yield result((
                        pre_gid,
                        connection.post_gid,
                        connection.synapse_count))
        else:
            for pre_gid in tqdm(self._resolve_gids(pre)):
                efferent_synapse_count =\
                    self.synapse_counts\
                        .loc[pre_gid]\
                        .reindex(self._resolve_gids(post))\
                        .dropna()
                for post_gid, synapse_count in efferent_synapse_count.iteritems():
                    yield result((
                        pre_gid,
                        post_gid,
                        synapse_count))

