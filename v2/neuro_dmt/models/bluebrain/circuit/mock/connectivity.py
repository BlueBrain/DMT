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
    def get_efferent_degree(self, mtype):
        """
        Out-degree of a cell of given 'mtype'.
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
    efferent_degree_mtype = Field(
        """
        A dict mapping mtype to  expected efferent degree for neurons of
        that mtype.
        """)
    synapse_count_pathway = Field(
        """
        A double dict mapping pre_mtype -> post_mtype -> number of synapses
        expected to connect cells in the pathway pre_mtype --> post_mtype.
        """)

    def get_efferent_degree(self, mtype,
            *args, **kwargs):
        """
        Number of out-going connections of a neuron of given 'mtype'.
        """
        return np.random.poisson(
            self.efferent_degree_mtype[mtype])

    def get_synapse_count(self,
            pre_mtype, post_mtype,
            *args, **kwargs):
        """
        How many synapses connecting cells in pathway pre_mtype --> post_mtype?
        """
        return 1 + np.random.poisson(
            self.synapse_count_pathway[pre_mtype][post_mtype])

