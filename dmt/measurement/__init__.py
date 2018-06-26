"""Measurement of a physical phenomenon of a system,
composed of a physical quantity that consists of a number and units"""

from abc import ABC, abstractmethod
from dmt import MeasurableSystem

class Measurement(ABC):
    """Behavior of a measurement."""

    @property
    @abstractmethod
    def measured_system(self) -> MeasurableSystem:
        """The system that this measurement was made on."""
        pass

    @property
    @abstractmethod
    def measurement_label(self) -> str:
        """A label of this measurement to be used as a column in a data-frame.
        For example, cell density should be cell_density --- no spaces."""
        pass

    @property
    @abstractmethod
    def units(self) -> Units

