"""Compare cell densities of two MeasruableSystems"""

from dmt.validation.comparison import Comparison
from dmt.measruable_system import MeasurableSystem

class CellDensityComparison(Comparison):
    """Comparison of cell density between two measurable systems."""

    def __init__(self, ref: MeasurableSystem, alt: MeasurableSystem) -> None :
        """
        Parameters
        -----------
        ref: reference MearuableSystem
        alt: alternative MeasruableSystems
        """
        self._ref = ref
        self._alt = alt

    @property
    def alternative_system(self) -> MeasurableSystem :
        return self._alt

    @property
    def reference_system(self) -> MeasruableSystem :
        return self._ref


    def make(self):
        ref_measurement = self._ref.get_cell_density()
        alt_measurement = self._alt.get_cell_density()


