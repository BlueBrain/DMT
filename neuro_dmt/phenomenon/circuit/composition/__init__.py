"""Phenomena related to the composition of a brain region"""

from dmt.vtk.phenomenon import Phenomenon
from neuro_dmt.phenomenon.circuit import BrainRegionPhenomenon

cell_density = Phenomenon(name = "cell density",
                          description = """Number of cells in a unit volume
                          of a brain region""")

inhibitory_cell_ratio = Phenomenon(name = "inhibitory cell ratio",
                                   description = """Ratio of inhibitory to
                                   excitatory cells in a brain region""")


class Composition(BrainRegionPhenomenon):
    """Composition is a class of phenomena that concern
    what a brain region is made of."""

    pass


class CellDensity(Composition):
    """Number of cells in a unit volume of a brain region."""

    name = "cell density"

    description = """Number of cells in a unit volume of a brain region"""


class InhibitoryCellRatio(Composition):
    """Ratio of inhibitory to excitatory cells in a brain region."""

    name = "inhibitory cell ratio"

    description = "Ratio of inhibitory to excitatory cells in a brain region"
