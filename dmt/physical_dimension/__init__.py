"""A physical quantity is a physical property of a phenomenon, body,
or substance, that can be quantified by measurement. A physical quantity can be
expressed as the combination of a magnitude expressed by a number and a unit.
A physical quantity will have physical dimensions. For example, measurement of
length will provide a quantity with physical dimensions of [L].
We begin by defining PhysicalDimension. PhysicalDimension will not have state.
These will be singleton classes."""

from abc import ABC, abstractmethod
import numpy as np
from dmt.utils.collections import FrozenDict

class PhysicalDimension(ABC):
    """Physical dimensions compose our universe,
    both the exterior, and the interior.
    They can be modeled as composed of basic physical dimensions."""

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    def label(self):
        """
        Return
        -----------
        Label for this physical dimension"""
        return ','.join([
            '{}:{}'.format(letter, power)
            for letter, power in self.composition.items() if power != 0
        ])

    def __repr__(self):
        return '[' + self.label + ']'

    @property
    @abstractmethod
    def composition(self):
        """Composition of this physical dimension,
        for example Area is dict(L=2)"""
        pass

    @abstractmethod
    def __mul__(self, other):
        """multiply this physical dimension with another."""
        pass

    def __truediv__(self, other):
        if isinstance(other, Dimensionless):
            return self
        if other == self:
            return Dimensionless()

        compound_name =  self.name + "_by_" + other.name
        composition = FrozenDict({
            k: v for k, v in self.composition.updated(
                {key: self.composition.get(key, 0) - value
                 for key, value in other.composition.items()}
            ).items() if v != 0
        })
        return CompoundPhysicalDimension(compound_name, composition)

    def __eq__(self, other):
        """define equality to another"""
        return self.composition == other.composition

class Dimensionless(PhysicalDimension):
    """Dimensionless, like a number, a count of stuff.
    Improvements
    ------------
    Enforce that this is a singleton class."""

    @property
    def name(self):
        return "number"

    @property
    def label(self):
        return "N"

    @property
    def composition(self):
        return FrozenDict()

    def __mul__(self, other):
        return other

    def __truediv__(self, other):
        return FrozenDict({label: -1 * exponent
                           for label, exponent in other.composition})

    
class AtomicPhysicalDimension(PhysicalDimension):
    """All physical dimension are composed of AtomicPhysicalDimensions."""

    def __init__(self, name, label):
        self.__name = name
        self.__label = label

    @property
    def name(self):
        return self.__name

    @property
    def label(self):
        """a single letter abbreviation."""
        return self.__label

    @property
    def composition(self):
        return FrozenDict({self.__label: 1})

    def __mul__(self, other):
        if isinstance(other, Dimensionless):
            return self
        compound_name =  self.name + "_times_" + other.name
        composition = FrozenDict({
            k: v for k, v in other.composition.updated(
            {self.label: other.composition.get(self.label, 0) + 1}
            ).items() if v != 0
        })
        return CompoundPhysicalDimension(compound_name, composition)
       

class CompoundPhysicalDimension(PhysicalDimension):
    """A compound physical dimension is composed of AtomicPhysicalDimensions."""

    def __init__(self, name, composition):
        self.__name = name
        self.__composition = composition

    @property
    def name(self):
        return self.__name

    @property
    def composition(self):
        return self.__composition

    def __mul__(self, other):
        """multiply with another PhysicalDimension"""
        if isinstance(other, Dimensionless):
            return self

        composition = FrozenDict({
            k: v for k, v in self.composition.updated(
                {key: self.composition.get(key, 0) + value
                 for key, value in other.composition.items()}
            ).items() if v != 0
        })
        if len(composition) == 0:
            return Dimensionless()

        compound_name = self.name + "_times_" + other.name

        return CompoundPhysicalDimension(compound_name,
                                         composition)

