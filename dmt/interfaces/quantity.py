"""Behavior of a quantity."""

from abc import ABC, ABCMeta, abstractmethod, abstractclassmethod
from typing import TypeVar

class _Quantifiable(ABC):
    """Behavior of a quantity"""

    @property
    @abstractmethod
    def name(self) -> str:
        """how is this quantity called?"""
        pass

    @property
    @abstractmethod
    def units(self) -> [Unit]

Quantifiable = TypeVar('Quantifiable', bound=_Quantifiable)
