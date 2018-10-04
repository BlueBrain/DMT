"""Circuit composition data for the Somatosensory cortex.
"""
from abc import abstractmethod
import numpy as np
import pandas as pd
from dmt.vtk.utils.collections import Record
from dmt.vtk.measurement.parameter.group import ParameterGroup
from neuro_dmt.utils import brain_regions
from neuro_dmt.measurement.parameter import CorticalLayer
from neuro_dmt.data.bluebrain.circuit.cortex import CortexCompositionData
    

class SomatosensoryCortexCompositionData(CortexCompositionData):
    """Base class for Blue Brain Project Circuit Composition Data"""

    spatial_parameters = {CorticalLayer()}

    brain_region = brain_regions.sscx

    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(*args, **kwargs)

    @abstractmethod
    def get_reference_datasets(self, data_location):
        """..."""
        pass
                 
    @classmethod
    def with_metadata(cls, reference_dataset, reference_dataframe):
        return Record(
            label = reference_dataset.get('short_name', 'unknown'),
            region_label = ParameterGroup(cls.spatial_parameters).label,
            uri = reference_dataset.get('url', 'unknown'),
            citation = reference_dataset.get('citation', 'unknown'),
            what = reference_dataset.get('what', 'dunno'),
            data=reference_dataframe)

    @classmethod
    def summarized(cls, means, stdevs, scale_factor=1.0):
        means = np.array(means)
        stdevs = np.array(stdevs)
        label = ParameterGroup(cls.spatial_parameters).label
        return pd.DataFrame(
            {label:  range(1, 7),
             'mean': scale_factor * means,
             'std': scale_factor * stdevs})\
                 .set_index(label)
                     
    
