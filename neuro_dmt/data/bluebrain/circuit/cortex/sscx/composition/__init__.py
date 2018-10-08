"""Circuit composition data for the Somatosensory cortex.
"""
from abc import abstractmethod
import numpy as np
import pandas as pd
from dmt.vtk.utils.collections import Record
from dmt.vtk.measurement.parameter.group import ParameterGroup
from dmt.vtk.phenomenon import Phenomenon
from neuro_dmt.utils import brain_regions
from neuro_dmt.measurement.parameter import CorticalLayer
from neuro_dmt.data.bluebrain.circuit.cortex import CortexCompositionData
    

class SomatosensoryCortexCompositionData(
        CortexCompositionData):
    """Base class for Blue Brain Project Circuit Composition Data"""

    def __init__(self, data, *args, **kwargs):
        """..."""
        kwargs["brain_region"] = brain_regions.sscx
        super().__init__(data, *args, **kwargs)
