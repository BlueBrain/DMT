"""Base class for all brain region circuit validations."""
from abc import ABC, abstractmethod
from dmt.analysis import Analysis
from dmt.vtk.utils.descriptor import Field, WithFCA
from neuro_dmt.utils.brain_regions import BrainRegion


class BrainCircuitAnalysis(Analysis):
    """Base class for a brain circuit analysis."""

    brain_region = Field(
        __name__="brain_region",
        __type__=BrainRegion,
        __doc__="Provides a model independent tag for the brain region.")

    def __init__(self, *args, **kwargs):
        """..."""
        self.brain_region = kwargs["brain_region"]
        super().__init__(*args, **kwargs)
