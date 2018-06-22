"""A definite magnitude of a quantity, adopted by convention of by lay,
used as a standard for measurement of the same kind of quantity."""

from abc import ABC, abstractmethod

class Unit(ABC):
    """Behavior of a unit of measurement."""
    
    @property
    @abstractmethod
    def scale_factor(self) -> float:
        pass
