"""A measurable system should define the required measurements."""


from abc import ABC, abstractmethod
from typing import Dict, Callable
from dmt.phenomenon import Phenomenon

class MeasurableSystem(ABC):
    """Basic behavior of a system that can be measured.
    A MeasurableSystem may be a model, or a wrapper around data obtained from
    an experimental system."""

    @abstractmethod
    @property
    def measurable_phenomena(self) -> Dict[Phenomenon, MeasruementMethod] :
        """The phenomena that this MeasruableSystem provides
        measurement methods for."""
        pass


