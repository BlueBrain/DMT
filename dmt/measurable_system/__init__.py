"""A measurable system should define the required measurements."""


from abc import ABC, abstractmethod

class MeasurableSystem(ABC):
    """Basic behavior of a system that can be measured.
    A MeasurableSystem may be a model, or a wrapper around data obtained from
    an experimental system."""

    @property
    @abstractmethod
    def measurable_phenomena(self):
        """
        Return
        ------
        A list of phenomena that this MeasurableSystem provides"""
        
        pass


