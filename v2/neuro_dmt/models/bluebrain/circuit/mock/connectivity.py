"""
Connectivity of a circuit
"""
from abc import ABC, abstractmethod
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
            mtype,
            *args, **kwargs):
        """
        Number of out-going connections of a neuron of given 'mtype'.
        """
        return np.random.poisson(
            self.afferent_degree_mtype[mtype])

    def get_synapse_count(self,
            pre_synaptic_cell,
            post_synaptic_cell,
            *args, **kwargs):
        """
        How many synapses connecting cells in pathway pre_mtype --> post_mtype?
        """
        return 1 +\
            np.random.poisson(
                self.synapse_count_pathway[
                    pre_synaptic_cell.mtype][
                        post_synaptic_cell.mtype])

    def get_connections(self, cells):
        """
        Afferent connections for a post-synaptic cell
        """
        def _afferent_connections(post_synaptic_cell):
            pre_gids =\
                np.sort(np.random.choice(
                    cells.index,
                    self.get_afferent_degree(**post_synaptic_cell),
                    replace=False))
            return\
                pd.DataFrame([
                    {"pre_synaptic_cell_gid": pre_synaptic_cell.gid,
                     "post_synaptic_cell_gid": post_synaptic_cell.gid,
                     "synapse_count": self.get_synapse_count(pre_synaptic_cell,
                                                             post_synaptic_cell)}
                    for pre_synaptic_cell in cells.loc[pre_gids]])

        return\
            pd.concat([
                _afferent_connections(post_synaptic_cell)
                for _, post_synaptic_cell in cells.iterrows()])
