"""A definite magnitude of a quantity, adopted by convention of by law,
used as a standard for measurement of the same kind of quantity."""

from abc import ABC, abstractmethod
from dmt.physical_dimension import PhysicalDimension
from dmt.utils.collections import Namespace
from dmt.utils.utils import ABCwithRegistryMeta

class Unit(metaclass=ABCwithRegistryMeta):
    """Behavior of a unit of measurement."""
    
    __instance_registry__ = {}


    def __init__(self, name, label, physical_dimensions, scale_to_standard):
        """
        Parameters
        ----------
        @name :: A short string, example 'centimeter'
        @label :: A very short string, example 'cm'
        @physical_dimension :: , example 'Length'
        @scale_to_standard :: fraction of the standard unit, example 1e-2
    """
        self.__name = name
        self.__label = label
        self.__physical_dimensions = physical_dimensions
        self.__std_scale = scale_to_standard

        #self.__instance_registry__[self.__class__,__name__] = self
        self.__instance_registry__[name] = self

    def __repr__(self):
        """label for this unit."""
        return self.label

    @property
    def name(self):
        """a somewhat descriptive string"""
        return self.__name

    @property
    def label(self):
        """label that can be used,
        very brief string."""
        return self.__label
    
    @property
    def physical_dimensions(self):
        """The PhysicalDimension that this is a measurement unit of."""
        return self.__physical_dimensions

    @property
    def std_scale(self):
        """Scale factor of this unit with respect to a (unnamed) standard.
        All units with the same physical dimensions should have a scale_factor
        with respect to the same (implicit) standard.
        Return
        ------
        float"""
        return self.__std_scale

    @property
    @abstractmethod
    def standard_unit(self):
        """The accepted standard unit,
        with the same physical dimensions as this unit.
        Return
        ------
        Unit"""
        pass


    @property
    @abstractmethod
    def conversion_factor(self, alt_unit):
        """multiplication factor relating alt_unit to this unit."""
        pass
