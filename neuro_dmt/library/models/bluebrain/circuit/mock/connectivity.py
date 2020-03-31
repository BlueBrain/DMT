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
Connectivity of a circuit
"""
from abc import ABC, abstractmethod
from tqdm import tqdm
import numpy as np
import pandas as pd
from dmt.tk.journal import Logger
from dmt.tk.field import Field, WithFields


class CircuitConnectivity(ABC):
    """
    A data-class to parameterize a (mock) circuit's connectome.
    Because you can choose any method to wire up a circuit,
    we define an interface as abstract methods that must be implemented
    by a class providing circuit connectivity.
    """

    @abstractmethod
    def get_afferent_degree(self, mtype):
        """
        In-degree of a cell of given 'mtype'.
        """
        raise NotImplementedError

    @abstractmethod
    def get_afferent_gids(self, post_synaptic_cell, cells):
        """..."""
        raise NotImplementedError

    @abstractmethod
    def get_synapse_counts(self, pre_mtype, post_mtype):
        """
        How many synapses connecting cells in pathway pre_mtype --> post_mtype?
        """
        raise NotImplementedError


class SimpleUniformRandomConnectivity(
        CircuitConnectivity,
        WithFields):
    """
    A circuit in which a neuron has a prescribed efferent degree,
    and is assigned that many randomly chosen efferent neighbors.
    """
    mean_afferent_degree = Field(
        """
        A post-synaptic cell (irrespecitive of it's mtype) will be given
        a Poisson distributed number of afferent connections with the mean
        equal to this Field's value.
        """)
    mean_synapse_count = Field(
        """
        Mean number of synapses of a connection.
        """,
        __default_value__=5)
    def get_afferent_degree(self,
            post_synaptic_cell,
            *args, **kwargs):
        """
        Number of out-going connections of a neuron of given 'mtype'.
        """
        return\
            np.random.poisson(self.mean_afferent_degree)

    def _synapse_count(self, *args, **kwargs):
        return 1. + np.random.poisson(self.mean_synapse_count)

    def get_synapse_counts(self,
            connections):
        """
        ...
        """
        return\
            1. + np.random.poisson(
                self.mean_synapse_count,
                size=connections.shape[0])

    def get_afferent_gids(self,
            post_synaptic_cell,
            cells):
        """
        GIDs of cells afferent on a post-synaptic cell.
        Arguments
        -------------
        post_gid :: GID of the post_synaptic cell.
        cells :: pandas.DataFrame containing cells in the circuit
        """
        return\
            np.sort(np.random.choice(
                cells.index.values,
                self.get_afferent_degree(post_synaptic_cell),
                replace=False))

    def get_afferent_connections(self,
            post_gid, post_cell,
            cells):
        """...
        """
        return pd.DataFrame({
            "pre_gid": self.get_afferent_gids(post_cell, cells),
            "post_gid": post_gid})


class SimpleUniformRandomConnectivityWithMtypeDependence(
        CircuitConnectivity,
        WithFields):
    """
    A circuit in which a neuron has a prescribed efferent degree,
    and is assigned that many randomly chosen efferent neighbors.
    """
    afferent_degree_mtype = Field(
        """
        A dict mapping mtype to  expected in-degree for neurons of that mtype.
        """)
    synapse_count_pathway = Field(
        """
        A double dict mapping pre_mtype -> post_mtype -> number of synapses
        expected to connect cells in the pathway pre_mtype --> post_mtype.
        """)


    def get_afferent_degree(self,
            post_synaptic_cell,
            *args, **kwargs):
        """
        Number of out-going connections of a neuron of given 'mtype'.
        """
        return\
            np.random.poisson(
                self.afferent_degree_mtype[
                    post_synaptic_cell.mtype])

    def _synapse_count(self, pre_cell, post_cell):
        return 1. + np.random.poisson(
            self.synapse_count_pathway[pre_cell.mtype][post_cell.mtype])

    def get_synapse_counts(self,
            afferent_adjacency,
            cell_collection):
        """
        Arguments
        -------------
        afferent_adjacency :: ...
        cells :: pandas.DataFrame containing cells.
        """
        def _synapse_count(pre_mtype, post_mtype):
            return\
                1 + np.random.poisson(
                    self.synapse_count_pathway[pre_mtype][post_mtype])
        mtype_of =\
            np.array(
                cell_collection.get(properties="mtype"),
                dtype=str)
        # return [
        #     [1. + np.random.poisson(
        #         self.synapse_count_pathway[
        #             mtype_of[pre_gid]][mtype_of[post_gid]])
        #      for pre_gid in afferent_adjacency[post_gid]]
        #     for post_gid in tqdm(cell_collection.gids)]
        return  np.array([
            [_synapse_count(mtype_of[pre_gid], mtype_of[post_gid])
             for pre_gid in afferent_adjacency[post_gid]]
            for post_gid in tqdm(cell_collection.gids)])


    def get_afferent_gids(self,
            post_synaptic_cell,
            cells):
        """
        GIDs of cells afferent on a post-synaptic cell.
        Arguments
        -------------
        post_gid :: GID of the post_synaptic cell.
        cells :: pandas.DataFrame containing cells in the circuit
        """
        return\
            np.sort(np.random.choice(
                cells.index.values,
                self.get_afferent_degree(post_synaptic_cell),
                replace=False))

    def get_afferent_connections(self,
            post_gid, post_cell,
            cells):
        """...
        """
        return pd.DataFrame({
            "pre_gid": self.get_afferent_degree(post_cell, cells),
            "post_gid": post_gid,
            "synapse_count": [self._synapse_count(cells.iloc[pre_gid], post_cell)]})
        # return np.array([
        #     [pre_gid, post_gid, self._synapse_count(cells.iloc[pre_gid], post_cell)]
        #     for pre_gid in self.get_afferent_gids(post_cell, cells)])
