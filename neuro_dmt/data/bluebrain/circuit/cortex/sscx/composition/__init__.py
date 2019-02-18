"""Circuit composition data for the Somatosensory cortex.
"""
from sys import stderr
import os
import numpy as np
import pandas as pd
from dmt.vtk.utils.descriptor\
    import Field
from dmt.vtk.utils.collections\
    import Record
from dmt.vtk.phenomenon\
    import Phenomenon
from neuro_dmt.utils\
    import brain_regions
from neuro_dmt.measurement.parameter\
    import BrainCircuitSpatialParameter
from neuro_dmt.measurement.parameter\
    import CorticalLayer
from neuro_dmt.data.bluebrain.circuit.cortex\
    import CortexCompositionData


class SSCxCompositionData(
        CortexCompositionData):
    """Base class for Blue Brain Project Circuit Composition Data.
    """
    _available_data = []
    primary_spatial_parameter=\
        Field(
            __name__="primary_spatial_parameter",
            __type__=BrainCircuitSpatialParameter,
            __doc__="""Which of the possibly many spatial
            parameters is the one that the data is provided against.
            For example, the composition data here may be against
            layers (CorticaLayer) or depth (CorticalDepth)""")

    def __init__(self,
            animal,
            phenomenon,
            spatial_parameters=[CorticalLayer()],
            primary_spatial_parameter=CorticalLayer(),
            *args, **kwargs):
        """..."""
        super().__init__(
            phenomenon,
            animal=animal,
            spatial_parameters=[CorticalLayer()],
            primary_spatial_parameter=primary_spatial_parameter,
            brain_region=brain_regions.sscx,
            *args, **kwargs)

    def with_metadata(self,
            reference_dataset,
            reference_dataframe):
        """Add metadata to your data.
        This method is tailored for Rat and Mouse data.
        You can customize it for your data, or not use it!"""
        return\
            Record(
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
        return\
            pd.DataFrame(
                {'mean': scale_factor * np.array(means),
                 'std': scale_factor * np.array(stdevs) },
                index=pd.Index(
                    sorted(self.primary_spatial_parameter.values),
                    name=self.primary_spatial_parameter.label))

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
            for k in cls._available_data.keys():
                i += 1
                msg += "\t({}) {}\n".format(i, k)
            stderr.write(msg)
        return None
