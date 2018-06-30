"""Behavior of a validation expressed as an abstract base class.
"""

from abc import ABC, abstractmethod

class ValidationBase(ABC):
    """Behavior of a Validation."""

    @abstractmethod
    def __call__(self, **kwargs):
        """A Validation may be called."""
        self.check_required_arguments, kwargs)

