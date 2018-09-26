"""Base class for all brain region circuit validations."""
from abc import ABC, abstractmethod
from dmt.vtk.utils.descriptor import Field, WithFCA

class BrainCircuitAnalysis(WithFCA):
    """Base class for a brain circuit analysis."""
    def __init__(self, brain_region, *args, **kwargs):
        """..."""

    @property
    @abstractmethod
    def brain_region(self):
        """An object that represents a brain region."""
        pass

    

