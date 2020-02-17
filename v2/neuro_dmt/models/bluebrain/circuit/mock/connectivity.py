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
    def get_synapse_count(self, pre_mtype, post_mtype):
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

    def get_synapse_count(self,
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
        return [
            [_synapse_count(mtype_of[pre_gid], mtype_of[post_gid])
             for pre_gid in afferent_adjacency[post_gid]]
            for post_gid in tqdm(cell_collection.gids)]


    # def get_synapse_count(self,
    #         pre_synaptic_cell,
    #         post_synaptic_cell,
    #         *args, **kwargs):
    #     """
    #     How many synapses connecting cells in pathway pre_mtype --> post_mtype?
    #     """
    #     return\
    #         1 + np.random.poisson(
    #             self.synapse_count_pathway[
    #                 pre_synaptic_cell.mtype][
    #                     post_synaptic_cell.mtype])

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
