"""A physical quantity is a physical property of a phenomenon, body, or
substance, that can be quantified by measurement. A physical quantity can be
expressed as the combination of a magnitude expressed by a number and a unit."""

from abc import ABC, abstractmethod, abstractclassmethod
from dmt.measurement.units import Unit
from typing import TypeVar

class Quantity(ABC):
    """behavior of a physical quantity."""

    @property
    @abstractmethod
    def standard_unit(self) -> Unit:
        """standard units for this Quantity"""
        pass

    def __init__(self, magnitude, unit):
        self.magnitude = magnitude
        self.unit = unit

    @property
    @abstractmethod
    def label(self) -> str:
        """label that can be used in report,
        or a pandas data-frame column name."""
        pass

    def convert_unit(self, to):
        """Return a new Quantity with changed units.
        Parameters
        ----------
        to: Unit, measurement units for this quantity.
        """
        conversion_factor = self.unit.scale_factor / to.scale_factor
        return Quantity(self.magnitude * conversion_factor)



#anything Quantifiable must behave like a Quantity
Quantifiable = TypeVar("Quantity", bound=Quantity)
