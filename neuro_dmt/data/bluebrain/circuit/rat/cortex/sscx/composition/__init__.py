"""Data for the circuit composition of Rat Somatosensory cortex."""
import os
from abc import abstractmethod
import numpy as np
import pandas as pd
from dmt.vtk.phenomenon import Phenomenon
from dmt.vtk.utils.collections import Record
from dmt.vtk.measurement.parameter.group import ParameterGroup
from neuro_dmt.measurement.parameter import CorticalLayer
from neuro_dmt.data.bluebrain.circuit.cortex.sscx.composition\
    import SomatosensoryCortexCompositionData
from neuro_dmt.data.bluebrain.circuit.cortex.sscx.composition\
    import SomatosensoryCortexCompositionData


class RatSomatosensoryCortexCompositionData(
        SomatosensoryCortexCompositionData):
    """..."""

    spatial_parameter_label = CorticalLayer().label

    def __init__(self, phenomenon, *args, **kwargs):
        """..."""
        self.phenomenon = phenomenon
        self.spatial_parameters = {CorticalLayer()}
        super().__init__(
            data=RatSomatosensoryCortexCompositionData.data_location(phenomenon),
            animal="rat",
            *args, **kwargs)

    @classmethod
    def with_metadata(cls, reference_dataset, reference_dataframe):
        """..."""
        return Record(
            label = reference_dataset.get('short_name', 'unknown'),
            region_label = CorticalLayer().label,
            uri = reference_dataset.get('url', 'unknown'),
            citation = reference_dataset.get('citation', 'unknown'),
            what = reference_dataset.get('what', 'dunno'),
            data=reference_dataframe)

    @classmethod
    def summarized(cls, means, stdevs, scale_factor=1.0):
        """..."""
        means = np.array(means)
        stdevs = np.array(stdevs)
        label = cls.spatial_parameter_label
        return pd.DataFrame(
            {label:  range(1, 7),
             'mean': scale_factor * means,
             'std': scale_factor * stdevs})\
                 .set_index(label)
                     
    @staticmethod
    def data_location(phenomenon):
        """..."""
        return os.path.join(
            "/gpfs/bbp.cscs.ch/home/sood",
            "work/validations/dmt",
            "examples/datasets/cortex/sscx/rat",
            phenomenon.label)

    @staticmethod
    def get(phenomenon):
        """Get reference data by phenomenon.

        Parameters
        --------------------------------------------------------------------
        phenomenon :: Either[str, Phenomenon]"""

        from neuro_dmt.data.bluebrain.circuit.rat.\
            cortex.sscx.composition.cell_density\
            import RatSomatosensoryCortexCellDensityData
        from neuro_dmt.data.bluebrain.circuit.rat.\
            cortex.sscx.composition.cell_ratio\
            import RatSomatosensoryCortexCellRatioData
        from neuro_dmt.data.bluebrain.circuit.rat.\
            cortex.sscx.composition.inhibitory_synapse_density\
            import  RatSomatosensoryCortexInhibitorySynapseDensityData
        from neuro_dmt.data.bluebrain.circuit.rat.\
            cortex.sscx.composition.synapse_density\
            import RatSomatosensoryCortexSynapseDensityData

        plabel = (phenomenon.label if isinstance(phenomenon, Phenomenon) 
                  else phenomenon)

        if plabel == "cell_density":
            return RatSomatosensoryCortexCellDensityData()
        if plabel == "cell_ratio":
            return RatSomatosensoryCortexCellRatioData()
        if plabel == "inhibitory_synapse_density":
            return RatSomatosensoryCortexInhibitorySynapseDensityData()
        if plabel == "synapse_density":
            return RatSomatosensoryCortexSynapseDensityData()

        raise NotImplementedError("Data for phenomenon {}".format(phenomenon))

    
