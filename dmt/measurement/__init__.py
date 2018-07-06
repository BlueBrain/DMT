"""Measurement is the assignment of a number to a characteristic of an object
or event, which can be compared with other objects or events.
Measurement is the determination or estimation of ratios of quantities.
Measurement is the correlation of numbers with entities that are not numbers.
Statistically speaking, a measurement is a set of observations that reduce
uncertainty where the result is expressed as a quantity. There is not a clear
distinction between estimation and measurement."""

#from abc import ABC. abstractmethod
from dmt.phenomenon import Phenomenon
from dmt.measurement import MeasurableSystem
#from dmt.methods import MeasurementMethod
from dmt.quantity import Quantity

class Measurement:
    """Defines a measurement.
    We define this class to be abstract to distinguish between measurements
    composed of quantities that are scalar, vector, or statistical.

    Not sure if it should be an ABC"""

    def __init__(self, phenomenon, system, quantity):
        self._phenomenon = phenomenon
        self._system = system
        self._quantity = quantity

    @property
    def measured_phenomenon(self) -> Phenomenon :
        """The measured phenomenon."""
        return self._phenomenon

    @property
    def measured_system(self) -> MeasurableSystem :
        """The system that was measured."""
        return self._system

    @property
    def measured_quantity(self) -> Quantity :
        """Quantity that is the result of this measurement."""
        return self._quantity



