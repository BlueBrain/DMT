"""Measurements of the circuit's connectome."""
import numpy as np
from dmt.vtk import measurement
from dmt.vtk.phenomenon import Phenomenon
from neuro_dmt.models.bluebrain.circuit import BlueBrainModelHelper


class SynapseCount(measurement.Method):
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
