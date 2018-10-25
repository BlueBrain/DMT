"""Brain Circuit Analysis"""

from abc import ABC, abstractmethod
import os
from dmt.analysis import Analysis
from dmt.vtk.phenomenon import Phenomenon
from dmt.vtk.utils.descriptor import Field, WithFCA
from neuro_dmt.utils import brain_regions
from neuro_dmt.utils.brain_regions import BrainRegion

class BrainCircuitAnalysis(Analysis):
    """Base class for a brain circuit analysis."""

    brain_region = Field(
        __name__="brain_region",
        __type__=BrainRegion,
        __default__=brain_regions.whole_brain,
        __doc__="Provides a model independent tag for the brain region.")

    animal = Field(
        __name__="animal",
        __type__=str,
        __doc__="""Animal for which the circuit was built. This will help
        organize reporting.""")

    def __init__(self,
            *args, **kwargs):
        """..."""
        #self.brain_region = kwargs["brain_region"]
        super().__init__(*args, **kwargs)

    def _get_output_dir(self):
        """..."""
        animal_region_path\
            = os.path.join(
                self.animal,
                self.brain_region.label)

        return os.path.join(
            super()._get_output_dir(),
            animal_region_path)
