"""A definite magnitude of a quantity, adopted by convention of by law,
used as a standard for measurement of the same kind of quantity."""

from abc import ABC, abstractmethod
from dmt.physical_dimension import PhysicalDimension
from dmt.utils.utils import Namespace

class Unit(ABC):
    """Behavior of a unit of measurement."""
    
    registered_instances = {} #to store all the instances of units

    @property
    @abstractmethod
    def physical_dimensions(self):
        """The PhysicalDimension that this is a measurement unit of."""
        pass

    @property
    @abstractmethod
    def scale_to_standard(self):
        """Scale factor of this unit with respect to a (unnamed) standard.
        All units with the same physical dimensions should have a scale_factor
        with respect to the same (implicit) standard.
        Return
        ------
        float"""
        pass

    def weight_per(self, alt_unit):
        """Convert this unit to an alternate unit.
        Parameters
        ----------
        @alt_unit :: Unit # the alternate unit to convert to."""
        if self.physical_dimensions != alt_unit.physical_unit:
            raise Exception(
                "Incompatible Units " +
                self.physical_dimensions.__repr__() + " and " +
                alt_unit.physical_dimensions.__repr__()
            )

        return self.scale_to_standard / alt_unit.scale_to_standard

    @property
    @abstractmethod
    def label(self):
        pass

    def __repr__(self):
        """A label to use to print this Unit"""
        return self.label



class AtomicUnit(Unit):
    """An atomic unit is a building brick for compound units.
    In physics units for length, mass, and time are atomic.
    To this list we may add units of money, or count of things."""

    def __init__(self, name, label, physical_dimension, scale_to_standard):
        self.__name = name
        self.__label = label
        self.__physical_dimension = physical_dimension
        self.__scale_to_standard = scale_to_standard

    @property
    def physical_dimension(self):
        """The PhysicalDimension that this is a measurement unit of."""
        return self.__physical_dimension

    @property
    def scale_to_standard(self):
        return self.__scale_to_standard

    @abstractmethod
    def standard_unit(self):
        """The accepted standard unit,
        with the same physical dimensions as this unit.
        Return
        ------
        Unit"""
        pass

    @property
    def name(self):
        return self.__name

    @property
    def label(self):
        """label that can be used."""
        return self.__label
    
    def __repr__(self):
        """label for this unit."""
        return self.__label

class CompoundUnit(Unit):
    """"A compound unit is non-trivial transform of one or more
    AtomicUnits."""

    def __init__(self, name, label, physical_dimensions, atomic_units):
        self.__name = name
        self.__label = label
        self.__physical_dimensions = physical_dimensions


    @property
    def name(self):
        return self.__name

    @property
    def label(self):
        return self.__label

    @property
    def physical_dimensions(self):
        return self.__physical_dimensions

    @property
    def scale_to_standard(self):
        pd = self.__physical_dimensions
        au = self.__atomic_units
        [au.__dict__.get(dimname, 1.0).scale_to_standard ** pd.atomic_exponent(dimletter)
         for dimname, dimletter in pd.basic_physical_dimensions.items()]
