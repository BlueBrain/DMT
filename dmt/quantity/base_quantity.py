"""A base quantity is a physical quantity in a subset of a given system of
quantities that is chosen by convention, where no quantity in the set can be
expressed in terms of the others. (from Wikipedia)
https://en.wikipedia.org/wiki/International_System_of_Quantities#Base_quantities
"""

from dmt.quantity import Quantity
from dmt.measurement.units import Unit

class BaseQuantity(Quantity):
    """Behavior of a base quantity."""

    @property
    @abstractmethod
    def standard_unit(self) -> Unit:

class Length()
