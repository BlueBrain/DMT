"""
A physical dimension can be defined for a physical quantity.

"""

from ..field import Field, WithFields

class PhysicalDimension(WithFields):
    """
    A physical dimension is a property we associate with physical quantities.
    Length, mass, time are primitive or base physical dimensions that can be
    composed to define composite physical dimensions such as force and
    velocity.

    A physical dimension can be expressed as a set of exponents, one for each
    fundamental physical dimension.
    """

    L = Field(
        """
        Exponent of Length.
        """,
        __type__=int,
        __default_value__=0)
    M = Field(
        """
        Exponent of Mass.
        """,
        __type__=int,
        __default_value__=0)
    T = Field(
        """
        Exponent of Time.
        """,
        __type__=int,
        __default_value__=0)
    I = Field(
        """
        Exponent of electric current.
        """,
        __type__=int,
        __default_value__=0)
    K = Field(
        """
        Exponent of Temperature.
        """,
        __type__=int,
        __default_value__=0)
    J = Field(
        """
        Exponent of Luminous Intensity.
        """,
        __type__=int,
        __default_value__=0)
    N = Field(
        """
        Exponent of Count.
        """,
        __type__=int,
        __default_value__=0)
    C = Field(
        """
        Exponent of Currency.
        """,
        __type__=int,
        __default_value__=0)

    basic_dimensions = "LMTIKJNC"

    def __eq__(self, other):
        """
        Is this PhysicalDimension the same as the other.
        """
        return (
            self.L == other.L and
            self.M == other.M and
            self.T == other.T and
            self.I == other.I and
            self.K == other.K and
            self.J == other.J and
            self.N == other.N and
            self.C == other.C)

    def __repr__(self):
        """
        Represent this PhysicalDimension as a string.
        """
        positive_dimensions =[
            d for d in self.basic_dimensions
            if getattr(self, d) > 0]
        negative_dimensions = [
            d fo d in self.basic_dimensions
            if getattr(self, d) < 0]

       def _contribution(basic_dimension):
           """
           How much does a basic dimension contribute ?
           """
           power = getattr(self, basic_dimension, 0)
           return "{}^{}".format(basic_dimension, power)\
               if power != 0 else ""

       numerator =\
           " * ".join([_contribution(d) for d in positive_dimensions])\
           if len(positive_dimensions) > 0 else "1"
       denominator =\
           " * ".join([contribution(d) for d in negative_dimensions])
       return\
           "[{}/{}]".format(numerator, denominator)\
           if denominator else "[{}]".format(numerator)
