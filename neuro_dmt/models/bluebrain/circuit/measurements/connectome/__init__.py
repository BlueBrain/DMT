"""Measurements of the circuit's connectome."""
import numpy as np
import neurom as nm
from dmt.vtk import measurement
from dmt.vtk.phenomenon import Phenomenon
from neuro_dmt.models.bluebrain.circuit import BlueBrainModelHelper

class ConnectomeMeasurementMethod(
        measurement.Method):
    """Measurement Methods that will invoke circuit connectome"""

    def __init__(self,
            circuit,
            *args, **kwargs):
        """..."""
        self._circuit=\
            circuit
        super().__init__(
            *args, **kwargs)

    @property
    def cells(self):
        """..."""
        return self._circuit.cells

    @property
    def conn(self):
        """..."""
        return self._circuit.connectome

class AfferentConnectionCount(
        ConnectomeMeasurementMethod):
    """Number of connections coming into a cell,
    i.e. number of connections onto a post-synaptic cell."""

    label= "in-silico"
    phenomenon=\
        Phenomenon(
            "Afferent connections count.",
            "Number of connections onto a post-synaptic cell.")
    units= "Count"
    
    def __call__(self, gid):
        """...Call Me...

        Parameters
        ------------------------------------------------------------------------
        gid :: int #postsynaptic GID

        Returns
        ------------------------------------------------------------------------
        int
        """
        return len(self.conn.afferent_gids(gid))


class EfferentConnectionCount(
        ConnectomeMeasurementMethod):
    """Number of connections going out of a cell,
    i.e. number of connections out of a pre-synaptic cell."""

    label= "in-silico"
    phenomenon=\
        Phenomenon(
            "Efferent connections count.",
            "Number of connections out of a post-synaptic cell.")
    units= "Count"
    
    def __call__(self, gid):
        """...Call Me...

        Parameters
        ------------------------------------------------------------------------
        gid :: int #postsynaptic GID

        Returns
        ------------------------------------------------------------------------
        int
        """
        return len(self.conn.efferent_gids(gid))


class PairConnection(
        ConnectomeMeasurementMethod):
    """Are two cells connected? (i.e do they have any synapses between?)"""
    label= "in-silico"
    phenomenon=\
        Phenomenon(
            "Pair connection",
            "Existence of a connection between a pair of cells.")
    units= "Count"
    
    def __init__(self,
            circuit,
            *args, **kwargs):
        """..."""
        self.__efferent_gids__=\
            {}
        super().__init__(
            circuit,
            *args, **kwargs)

    def __call__(self, pre_gid, post_gid):
        """...Call Me...

        We use caching...

        Parameters
        ------------------------------------------------------------------------
        pre_gid :: int #pre-synaptic cell GID
        post_gid :: int #post-synaptic cell GID

        Returns
        ------------------------------------------------------------------------
        bool #indicating if their is a connection
        """
        if pre_gid not in self.__efferent_gids__:
            self.__efferent_gids__[pre_gid]=\
                self.conn.efferent_gids(pre_gid)
        return\
            post_gid in self.__efferent_gids__[pre_gid]


class AfferentSynapseCount(
        ConnectomeMeasurementMethod):
    """Number of synapses coming into a cell,
    i.e. number of synapses onto a post-synaptic cell."""

    label= "in-silico"
    phenomenon=\
        Phenomenon(
            "Afferent synapse count.",
            "Number of synapses onto a post-synaptic cell.")
    units= "Count"
    
    def __call__(self, gid):
        """...Call Me...

        Parameters
        ------------------------------------------------------------------------
        gid :: int #postsynaptic GID

        Returns
        ------------------------------------------------------------------------
        int
        """
        return\
            len(self.conn.afferent_synapses(gid))


class EfferentSynapseCount(
        ConnectomeMeasurementMethod):
    """Number of synapses going out of a cell,
    i.e. number of synapses out of a pre-synaptic cell."""

    label= "in-silico"
    phenomenon=\
        Phenomenon(
            "Efferent synapse count.",
            "Number of synapses out of a post-synaptic cell.")
    units= "Count"
    
    def __call__(self, gid):
        """...Call Me...

        Parameters
        ------------------------------------------------------------------------
        gid :: int #postsynaptic GID

        Returns
        ------------------------------------------------------------------------
        int
        """
        return\
            len(self.conn.efferent_synapses(gid))


class PairSynapseCount(
        ConnectomeMeasurementMethod):
    """Number of synapses between a pair of cells (gids)."""
    label= "in-silico"
    phenomenon=\
        Phenomenon(
            "Pair Synapse Count",
            "Number of synapses between two cells.")
    units= "Count"
    
    def __call__(self,
            pre_gid, post_gid):
        """...Call Me..."""
        return\
            len(
                self.conn.pair_synapses(
                    pre_gid=pre_gid,
                    post_gid=post_gid))


class SomaDistance(
        ConnectomeMeasurementMethod):
    """Distance between the soma bodies."""
    label= "in-silico"
    phenomenon=\
        Phenomenon(
            "Soma distance",
            "Distance between soma bodies of a connection.")
    units= "um^3"

    def __call__(self, pre_gid, post_gid):
        """...Call Me..."""
        positions=\
            self.cells\
                .positions([
                    pre_gid,
                    post_gid])
        return\
            np.linalg.norm(
                positions.loc[pre_gid] - positions.loc[post_gid])


class InterboutonInterval(
        ConnectomeMeasurementMethod):
    """InterboutonInterval of a cell."""
    label= "in-silico"
    phenomenon=\
        Phenomenon(
            "Interbouton Interval",
            "Mean Distance between boutons on a cell body.")
    units= "um"
        
    def __call__(self, gid):
        """...Call Me..."""
        return\
            1. / self._circuit.stats.bouton_density(gid)


class BoutonDensity(
        ConnectomeMeasurementMethod):
    """Bouton density of a cell."""
    label = "in-silico"
    phenomenon=\
        Phenomenon(
            "Bouton Density",
            "Number of boutons per unit length of axonic arbor of a cell.",
            group="connectome")
    units = "Count/um"

    def __call__(self, gid):
        """...Call Me...."""
        return self._circuit.stats.bouton_density(gid)


class ConnectionStrength(
        PairSynapseCount):
    """Number of synapses in a cell --> cell connection."""

    label= "in-silico"
    phenomenon=\
        Phenomenon(
            "Connection strength",
            "Number of synapses between cells in a connection.")
    units= "Count"

    def __call__(self,
            pre_gid, post_gid):
        """...Call Me..."""
        return\
            len(
                self.conn.pair_synapses(
                    pre_gid=pre_gid,
                    post_gid=post_gid))


class AxonLength(
        ConnectomeMeasurementMethod):
    """Total length of the axons of a cell.
    We do not filter on the region."""
    label = "in-silico"
    phenomenon=\
        Phenomenon(
            "Axon Length",
            "Total length of the axons of a neuron.",
            group="Connectome")
    units= "um"

    def __call__(self,
            cell_gid):
        """...Call Me..."""
        return\
            nm.get(
                "neurite_lengths",
                self._circuit.morph.get(cell_gid, False),
                neurite_type=nm.AXON
            )[0]

