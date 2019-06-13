"""
A quantity is a hypothetically measurable amount of something.
Quantity combines a number with a Unit.
A Quantity has a unique physical-dimension.
"""

from ..field import Field, WithFields
from .unit import Unit

class Quantity(WithFields):
    """
    Quantity combines a number with a Unit.
    """
    amount = Field(
        """
        A number that tells about the amount of this quantity with respect
        to it's associated unit of measurement.
        """,
        __type__=(int, float))
    unit_of_measurement = Field(
        """
        Unit used to measure this quantity.
        """,
        __type__=Unit)
