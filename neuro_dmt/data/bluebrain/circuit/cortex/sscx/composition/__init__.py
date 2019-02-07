"""Circuit composition data for the Somatosensory cortex.
"""
from sys import stderr
import os
import numpy as np
import pandas as pd
from dmt.vtk.utils.collections import Record
from dmt.vtk.phenomenon import Phenomenon
from neuro_dmt.utils import brain_regions
from neuro_dmt.measurement.parameter import CorticalLayer
from neuro_dmt.data.bluebrain.circuit.cortex import CortexCompositionData


class SSCxCompositionData(
        CortexCompositionData):
    """Base class for Blue Brain Project Circuit Composition Data.
    """
    _available_data = []

    def __init__(self,
            animal,
            phenomenon,
            *args, **kwargs):
        """..."""
        self.primary_spatial_parameter\
            = CorticalLayer()
        super().__init__(
            phenomenon,
            animal=animal,
            spatial_parameters=[CorticalLayer()],
            brain_region=brain_regions.sscx,
            *args, **kwargs)

    def with_metadata(self,
            reference_dataset,
            reference_dataframe):
        """Add metadata to your data.
        This method is tailored for Rat and Mouse data.
        You can customize it for your data, or not use it!"""
        return Record(
            label=reference_dataset.get('short_name', 'unknown'),
            region_label=self.primary_spatial_parameter.label,
            uri=reference_dataset.get('url', 'unknown'),
            citation=reference_dataset.get('citation', 'unknown'),
            what=reference_dataset.get('what', 'dunno'),
            data=reference_dataframe)

    def summarized(self,
            means,
            stdevs,
            scale_factor=1.0):
        """Summarize your data
        This method is tailored for Rat and Mouse data.
        You can customize it for your data, or not use it!"""
        means = np.array(means)
        stdevs = np.array(stdevs)
        label = self.primary_spatial_parameter.label
        return pd.DataFrame(
            {label:  sorted(self.primary_spatial_parameter.values),
             'mean': scale_factor * means,
             'std': scale_factor * stdevs})\
                 .set_index(label)
                     
    @classmethod
    def get_available_data(cls):
        """Get available data
        Subclasses will provide a concrete version."""
        raise NotImplementedError(
            "Subclass must provide its own version.")

    @classmethod
    def get(cls,
        phenomenon,
        *args, **kwargs):
        """Get reference data by phenomenon.

        Parameters
        --------------------------------------------------------------------
        phenomenon :: Either[str, Phenomenon]"""

        plabel=\
            (phenomenon.label
             if isinstance(phenomenon, Phenomenon) else 
             phenomenon)
        if not cls._available_data:
            cls._available_data=\
                cls.get_available_data()
        try:
            return cls._available_data[plabel](*args, **kwargs)
        except KeyError as e:
            msg = "No data available for {}\n".format(phenomenon)
            msg += "Available data:\n"
            i = 0
            for k in available_data.keys():
                i += 1
                msg += "\t({}) {}\n".format(i, k)
            stderr.write(msg)
        return None
