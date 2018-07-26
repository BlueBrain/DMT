"""Comparison of two MeasurableSystems."""

from abc import ABC, abstractmethod
from dmt.measurable_system import MeasurableSystem
from dmt.phenomenon import Phenomenon


class Comparison(ABC):
    """Compare two MeasurableSystems"""

    @property
    @abstractmethod
    def reference_system(self) -> MeasruableSystem :
        """The model/data MeasurableSystem this Comparison compares against"""
        pass

    @property
    @abstractmethod
    def alternative_system(self) -> MeasruableSystem :
        """The model/data MeasruableSystem this Comparison compares."""
        pass

    @abstractmethod
    def __call__(self) :
        """read up AP's circuit-analysis code.
        We may conclude that this hook is not required!"""
        pass

    @classmethod
    @abstractmethod
    def compared_phenomena(cls) -> List[Phenomenon] :
        """A list of phenomena that this Comparison compared."""
        pass

    @abstractmethod
    def make(self):
        """Make comparison.
        Example: get p-values comparing each of the columns in a data-frame"""
        pass
