"""A definite magnitude of a quantity, adopted by convention of by law,
used as a standard for measurement of the same kind of quantity."""

from abc import ABC, abstractmethod
from dmt.physical_dimension import PhysicalDimension

class Unit(ABC):
    """Behavior of a unit of measurement."""
    
    registered_instances = {} #to store all the instances of units

    @property
    @abstractmethod
    def __repr__(self):
        """A label to use to print this Unit"""
        pass

    @property
    @abstractmethod
    def physical_dimension(self):
        """The PhysicalDimension that this is a measurement unit of."""
        pass

    @property
    @abstractmethod
    def scale(self):
        """Scale of a unit can be measured in terms of another unit
        with the same physical dimensions as this unit, and a number.

        Return
        ------
        Tuple[Unit, Float] #a tuple of another unit and the scaling factor 
        relating this unit to that one."""
        pass

    @abstractmethod
    def weight_per(self, alt_unit):
        """Convert this unit to an alternate unit.
        Parameters
        ----------
        @alt_unit :: Unit # the alternate unit to convert to."""

        pass


class AtomicUnit(Unit):
    """An atomic unit is a building brick for compound units.
    In physics units for length, mass, and time are atomic.
    To this list we may add units of money, or count of things."""

    def __init__(self, physical_dimension):
        self.__physical_dimension = physical_dimension

    @property
    def physical_dimension(self):
        """The PhysicalDimension that this is a measurement unit of."""
        return self.__physical_dimension


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
