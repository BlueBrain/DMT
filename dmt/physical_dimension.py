"""A physical quantity is a physical property of a phenomenon, body,
or substance, that can be quantified by measurement. A physical quantity can be
expressed as the combination of a magnitude expressed by a number and a unit.
A physical quantity will have physical dimensions. For example, measurement of
length will provide a quantity with physical dimensions of [L].
We begin by defining PhysicalDimension. PhysicalDimension will not have state.
These will be singleton classes."""

from typing import NamedTuple

class PhysicalDimension:
    """Physical dimensions compose our universe,
    both the exterior, and the interior.
    They can be modeled as composed of basic physical dimensions."""

    __basic_physical_dimensions__ = {
        'Length': 'L',
        'Mass': 'M',
        'Time': 'T',
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
              C: exponent for currency}

        Limitations
        -----------
        kwargs could be garbage, there are no checks.
        but you have to pay the price of duck typing.
        """
        self.__atomic_exponents = kwargs

    def atomic_exponent(self, letter):
        """getter for exponent of physical dimension represented by letter"""
        return self.__atomic_exponent.get(letter, 0)

    @classmethod
    def with_atomic_exponents_dict(cls, aed={}):
        """an alternative constructor.

        Limiations
        ----------
        Will need additional arguments as the list of basic dimensions grows,
        or change them accordingly.
        """
        return PhysicalDimension(L=aed.get('L': 0),
                                 M=aed.get('M': 0),
                                 T=aed.get('T':0),
                                 C=aed.get('C':0))

    @property
    def label(self):
        """
        Return
        -----------
        Label for this physical dimension"""
        def contribution(letter):
            """contribution of a basic physical dimension."""
            power = self.atomic_weights(letter)
            return letter + '^' + power if power > 0 else ''

        return ''.join(
            [contribution(l)
             for l in self.__class__.__basic_physical_dimensions__.values()]
        )


    def repr(self):
        return "[" + self.label + "]"

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
            for l in self.__class__.__basic_physical_dimensions__.values()
        })



length = PhysicalDimension(L=1)
mass = PhysicalDimesion(M=1)
time = PhysicalDimesion(T=1)
currency = PhysicalDimension(C=1)


