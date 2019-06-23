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

    def get_efferent_degree(self, mtype, *args):
        """
        Number of out-going connections of a neuron of given 'mtype'.
        """
        return np.random.poisson(
            self.efferent_degree_mtype[mtype])
