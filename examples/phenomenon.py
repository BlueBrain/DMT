"""Example phenomena"""

#not complete example, more of what to do...
#mostly names of classes to write...

from dmt.phenomenon import Phenomenon
from neuro_dmt.circuit.composition import CircuitCompositionPhenomenon


class CellDensity(CircuitCompositionPhenomenon):
    """density of cells in a brain circuit."""

    @property
    def label(self) -> str:
        return "cell_density"

    @property
    def description(self) -> str:
        return """explain how cell density was measured."""


