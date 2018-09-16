"""Utilities to create some randomness."""
from abc import ABC, abstractmethod


class RandomGenerator(ABC):
    """Describes the behavior required from a generator of random values.
    """
    @property
    @abstractmethod
    def value_type(self):
        """Type of value generated."""
        pass

    @abstractmethod
    def __call__(self, *args, **kwargs):
        """Create a random generator of value_type for given
        parameters in args and kwargs. """
        pass



