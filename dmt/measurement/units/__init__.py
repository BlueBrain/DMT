"""A definite magnitude of a quantity, adopted by convention of by law,
used as a standard for measurement of the same kind of quantity."""

from abc import ABC, abstractmethod

class Unit(ABC):
    """Behavior of a unit of measurement."""
    
    @property
    @abstractmethod
    def scale_factor(self) -> float:
        pass



class AtomicUnit(Unit):
    """An atomic unit is a building brick for compound units.
    In physics units for length, mass, and time are atomic.
    To this list we may add units of money, or count of things."""

    pass


class CompoundUnit(Unit):
    """"A compound unit is non-trivial transform of one or more
    AtomicUnits."""

    @property
    @abstractmethod
    def unit_composition(self):
        """A list of (AtomicUnit, int) that compose this CompoundUnit.
        For example CubicMeter will be, [(Meter, 3)]"""
        pass

    @classmethod
    def simplified(cls):
        """Simplify """
