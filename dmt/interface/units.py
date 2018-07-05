"""Units for physical quantities."""

from abc import ABC, ABCMeta, abstractmethod, abstractclassmethod
from typing import TypeVar

class IUnits(ABC):
    """Behavior of units of a physical quantity."""

    @property
    @abstractmethod
    def name(self) -> str:
        """how are these units called?"""
        pass


