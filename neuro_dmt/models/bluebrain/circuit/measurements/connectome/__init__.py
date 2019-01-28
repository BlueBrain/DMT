"""Measurements of the circuit's connectome."""
import numpy as np
from dmt.vtk import measurement
from dmt.vtk.phenomenon import Phenomenon
from neuro_dmt.models.bluebrain.circuit import BlueBrainModelHelper

class AfferentConnectionCount(measurement.Method):
    """Number of connections coming into a cell,
    i.e. number of connections onto a post-synaptic cell."""

    label = "in-silico"
    phenomenon = Phenomenon("Afferent connections count.",
                            "Number of connections onto a post-synaptic cell.")
    units = "Count"

    def __init__(self, circuit):
        """..."""
        self._circuit = circuit

    def __call__(self, gid):
        """...Call Me...

        Parameters
        ------------------------------------------------------------------------
        gid :: int #postsynaptic GID

        Returns
        ------------------------------------------------------------------------
        int
        """
        return len(self._circuit.connectome.afferent_gids(gid))


class EfferentConnectionCount(measurement.Method):
    """Number of connections going out of a cell,
    i.e. number of connections out of a pre-synaptic cell."""

    label = "in-silico"
    phenomenon = Phenomenon("Efferent connections count.",
                            "Number of connections out of a post-synaptic cell.")
    units = "Count"

    def __init__(self, circuit):
        """..."""
        self._circuit = circuit

    def __call__(self, gid):
        """...Call Me...

        Parameters
        ------------------------------------------------------------------------
        gid :: int #postsynaptic GID

        Returns
        ------------------------------------------------------------------------
        int
        """
        return len(self._circuit.connectome.efferent_gids(gid))


class PairConnection(measurement.Method):
    """Are two cells connected? (i.e do they have any synapses between?)"""
    label = "in-silico"
    phenomenon = Phenomenon("Pair connection",
                            "Existence of a connection between a pair of cells.")
    units = "Count"

    def __init__(self, circuit):
        """..."""
        self._circuit = circuit

    def __call__(self, pre_gid, post_gid):
        """...Call Me...

        Parameters
        ------------------------------------------------------------------------
        pre_gid :: int #pre-synaptic cell GID
        post_gid :: int #post-synaptic cell GID

        Returns
        ------------------------------------------------------------------------
        bool #indicating if their is a connection
        """
        conn = self._circuit.connectome
        return post_gid in conn.efferent_gids(pre_gid)


class AfferentSynapseCount(measurement.Method):
    """Number of synapses coming into a cell,
    i.e. number of synapses onto a post-synaptic cell."""

    label = "in-silico"
    phenomenon = Phenomenon("Afferent synapse count.",
                            "Number of synapses onto a post-synaptic cell.")
    units = "Count"

    def __init__(self, circuit):
        """..."""
        self._circuit = circuit

    def __call__(self, gid):
        """...Call Me...

        Parameters
        ------------------------------------------------------------------------
        gid :: int #postsynaptic GID

        Returns
        ------------------------------------------------------------------------
        int
        """
        return len(self._circuit.connectome.afferent_synapses(gid))


class EfferentSynapseCount(measurement.Method):
    """Number of synapses going out of a cell,
    i.e. number of synapses out of a pre-synaptic cell."""

    label = "in-silico"
    phenomenon = Phenomenon("Efferent synapse count.",
                            "Number of synapses out of a post-synaptic cell.")
    units = "Count"

    def __init__(self, circuit):
        """..."""
        self._circuit = circuit
        self._helper = BlueBrainModelHelper(circuit=circuit)

    def __call__(self, gid):
        """...Call Me...

        Parameters
        ------------------------------------------------------------------------
        gid :: int #postsynaptic GID

        Returns
        ------------------------------------------------------------------------
        int
        """
        return len(self._circuit.connectome.efferent_synapses(gid))


class PairSynapseCount(measurement.Method):
    """Number of synapses between a pair of cells (gids)."""
    label = "in-silico"
    phenomenon = Phenomenon("Synapse Count",
                            "Number of synapses between two cells.")
    units = "Count"

    def __init__(self, circuit):
        """..."""
        self._circuit = circuit

    def __call__(self, pre_gid, post_gid):
        """...Call Me..."""
        conn = self._circuit.connectome
        return len(conn.pair_synapses(pre_gid=pre_gid, post_gid=post_gid))


class SomaDistance(measurement.Method):
    """Distance between the soma bodies."""
    label = "in-silico"
    phenomenon = Phenomenon("Soma distance",
                            "Distance between soma bodies of a connection.")
    units = "um^3"

    def __init__(self, circuit):
        """..."""
        self._circuit = circuit

    def __call__(self, pre_gid, post_gid):
        """...Call Me..."""
        poses = self._circuit.cells.positions([pre_gid, post_gid])
        return np.linalg.norm(poses.iloc[0] - poses.iloc[1])


class InterboutonInterval(measurement.Method):
    """InterboutonInterval of a cell."""
    label = "in-silico"
    phenomenon = Phenomenon("Interbouton Interval",
                            "Mean Distance between boutons on a cell body.")
    units = "um"

    def __init__(self, circuit):
        """..."""
        self._circuit = circuit

    def __call__(self, gid):
        """...Call Me..."""
        return 1. / self._circuit.stats.bouton_density(gid)


class ConnectionStrength(measurement.Method):
    """Number of synapses in a cell --> cell connection."""

    label = "in-silico"
    phenomenon = Phenomenon("Connection strength",
                            "Number of synapses between cells in a connection.")
    unit = "Count"

    def __init__(self, circuit):
        self._circuit = circuit

    def __call__(self, connection):
        """...Call Me...

        Parameters
        ------------------------------------------------------------------------
        connection :: Tuple[pre_gid :: str, post_gid :: str]

        Returns
        ------------------------------------------------------------------------
        int #number of synapses
        """
        return\
            len(
                self._circuit.connectome.pair_synapses(
                    pre_gid=connection[0],
                    post_gid=connection[1]))

