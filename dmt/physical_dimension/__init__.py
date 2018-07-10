"""A physical quantity is a physical property of a phenomenon, body,
or substance, that can be quantified by measurement. A physical quantity can be
expressed as the combination of a magnitude expressed by a number and a unit.
A physical quantity will have physical dimensions. For example, measurement of
length will provide a quantity with physical dimensions of [L].
We begin by defining PhysicalDimension. PhysicalDimension will not have state.
These will be singleton classes."""

from abc import ABC, abstractmethod
import numpy as np

class PhysicalDimension(ABC):
    """Physical dimensions compose our universe,
    both the exterior, and the interior.
    They can be modeled as composed of basic physical dimensions."""

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def label(self):
        pass

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

    @abstractmethod
    def __truediv__(self, other):
        """divide this physical dimension by another,
        to return another physical dimension."""
        pass


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
        return {}

    def __mul__(self, other):
        return other

    def __truediv__(self, other):
        return {label: -1 * exponent for label, exponent in other.composition}


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
        return {self.__label: 1}

    def __mul__(self, other):
        compound_name =  self.name + "_times_" + other.name
        composition = other.composition.update({
            self.label: other.composition.get(self.label, 0) + 1
        })
        return CompoundPhysicalDimension(compound_name, composition)

    def __truediv__(self, other):
        if other == self:
            return Dimensionless()
        


class CompoundPhysicalDimension(PhysicalDimension):
    """A compound physical dimension is composed of AtomicPhysicalDimensions."""

    def __init__(self, name, composition):
        self.__name = name
        self.__composition = composition

class PhysicalDimension:
    """Physical dimensions compose our universe,
    both the exterior, and the interior.
    They can be modeled as composed of basic physical dimensions."""

    basic_physical_dimensions = {
        'Length': 'L',
        'Mass': 'M',
        'Time': 'T',
        'ElectricCurrent': 'I',
        'AbsoluteTemperature': 'K',
        'LuminousIntensity': 'J',
        'Count': 'N',
        'Currency': 'C'
    }

    def __init__(self, **kwargs):
        """
        Parameters
        -----------
        kwargs: key word arguments,
        
        dict {L: exponent for length
              M: exponent for mass
              T: exponent for time
              I: exponent for electric current
              K: exponent for absolute temperature
              J: exponent for luminous intensity
              N: exponent for count of stuff
              C: exponent for currency}

        Limitations
        -----------
        kwargs could be garbage, there are no checks.
        but you have to pay the price of duck typing.
        """
        self.__atomic_exponents = kwargs

    def atomic_exponent(self, letter):
        """getter for exponent of physical dimension represented by letter"""
        return self.__atomic_exponents.get(letter, 0)

    @classmethod
    def with_atomic_exponents_dict(cls, aed={}):
        """an alternative constructor.

        Limiations
        ----------
        Will need additional arguments as the list of basic dimensions grows,
        or change them accordingly.
        """
        return PhysicalDimension(L=aed.get('L', 0),
                                 M=aed.get('M', 0),
                                 T=aed.get('T', 0),
                                 I=aed.get('I', 0),
                                 K=aed.get('K', 0),
                                 J=aed.get('J', 0),
                                 N=aed.get('N', 0),
                                 C=aed.get('C', 0))

    def __eq__(self, other):
        """tell if this PhysicalDimension is the same as the other."""
        return all([
            self.atomic_exponent(l) == other.atomic_exponent(l)
            for l in PhysicalDimension.basic_physical_dimensions.values()
        ])

    @property
    def label(self):
        """
        Return
        -----------
        Label for this physical dimension"""
        def contribution(letter):
            """contribution of a basic physical dimension."""
            power = self.atomic_exponent(letter)
            return letter + str(power) if power > 0 else ''

        return ''.join(
            [contribution(l)
             for l in self.__class__.basic_physical_dimensions.values()]
        )


    def __repr__(self):
        """
        Return
        -----------
        Representation  for this physical dimension"""



        positive = [pd for pd in self.__class__.basic_physical_dimensions.values()
                    if self.atomic_exponent(pd) > 0]
        negative = [pd for pd in self.__class__.basic_physical_dimensions.values()
                    if self.atomic_exponent(pd) < 0]

        def contribution(letter):
            """contribution of a basic physical dimension."""
            power = self.atomic_exponent(letter)
            return letter + '^' + str(abs(power)) if power != 0 else ''

        r = (' * '.join([contribution(l) for l in positive])
             if len(positive) > 0 else '1')
        if len(negative) > 0:
            r += ' / ' + ' * '.join([contribution(l) for l in negative])
             
        return '[' + r + ']'


    def __mul__(self, other):
        """You can multiply and divide two physical dimensions,
        (but not add or subtract)
        Parameters
        -------------
        other: another physical dimension."""

        def combined_exponent(letter):
            '''combine weights in self and other.'''
            return self.atomic_exponent(letter) + other.atomic_exponent(letter)

        return PhysicalDimension.with_atomic_exponents_dict({
            l: combined_exponent(l)
            for l in self.__class__.basic_physical_dimensions.values()
        })

    def __truediv__(self, other):
        """You can multiply and divide two physical dimensions,
        (but not add or subtract)
        Parameters
        -------------
        other: another physical dimension."""

        def combined_exponent(letter):
            '''combine weights in self and other.'''
            return self.atomic_exponent(letter) - other.atomic_exponent(letter)

        return PhysicalDimension.with_atomic_exponents_dict({
            l: combined_exponent(l)
            for l in self.__class__.basic_physical_dimensions.values()
        })

    def combined_weight(self, basic_weights):
        """combine the basic physical dimension weights.
        Parameters
        ----------
        basic_weights :: a dict,
        that maps basic physical dimension labels to  floats"""
        
        return np.prod([
            basic_weights.get(l, 0) ** self.__atomic_exponents[l]
            for l in PhysicalDimension.basic_physical_dimensions.values()
        ])



from dmt.utils.utils import Namespace

BasicPhysicalDimension = Namespace(Length=PhysicalDimension(L=1),
                                   Mass=PhysicalDimension(M=1),
                                   Time=PhysicalDimension(T=1),
                                   Ecurrent=PhysicalDimension(I=1),
                                   Temperature=PhysicalDimension(K=1),
                                   Luminosity=PhysicalDimension(J=1),
                                   Count=PhysicalDimension(N=1),
                                   Currency=PhysicalDimension(C=1))


