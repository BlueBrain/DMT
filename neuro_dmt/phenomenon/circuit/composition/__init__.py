"""Phenomena related to the composition of a brain region"""

from neuro_dmt.phenomenon.circuit import BrainRegionPhenomenon


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

        description = "ratio of inhibitory to excitatory cells in a brain region."
