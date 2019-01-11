"""Data for the circuit composition of Rat Somatosensory cortex."""
import os
import numpy as np
import pandas as pd
from dmt.vtk.phenomenon import Phenomenon
from dmt.vtk.utils.collections import Record
from dmt.vtk.measurement.parameter.group import ParameterGroup
from neuro_dmt.measurement.parameter import CorticalLayer
from neuro_dmt.data.bluebrain.circuit.cortex.sscx.composition\
    import SomatosensoryCortexCompositionData

class RatSomatosensoryCortexCompositionData(
        SomatosensoryCortexCompositionData):
    """..."""

    def __init__(self,
                phenomenon,
                data_location = os.path.join(
                    "/gpfs/bbp.cscs.ch/home/sood",
                    "work/validations/dmt",
                    "examples/datasets/cortex/sscx/rat"),
                *args, **kwargs):
        """
        Parameters
        ------------------------------------------------------------------------
        phenomenon :: Phenomenon

        Warning
        ------------------------------------------------------------------------
        Default data location above is hard-coded to a path on GPFS, which turns
        out to be a location under this (dmt) project directory. We should
        change this by a relative path using a global variable pointing to this
        project directory."""
        super().__init__(
            animal="rat",
            phenomenon=phenomenon,
            data_location=data_location,
            *args, **kwargs)

    @classmethod
    def get_available_data_keys(cls):
        """A list of keys(labels) for available data."""
        return ["cell_density",
                "cell_ratio",
                "inhibitory_synapse_density",
                "synapse_density"]

    @classmethod
    def get_available_data(cls):
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

        return dict(
            cell_density=RatSomatosensoryCortexCellDensityData,
            cell_ratio=RatSomatosensoryCortexCellRatioData,
            inhibitory_synapse_density=RatSomatosensoryCortexInhibitorySynapseDensityData,
            synapse_density=RatSomatosensoryCortexSynapseDensityData)
        
        # cell_density=\
        #     RatSomatosensoryCortexCellDensityData(
        #         *args, **kwargs)
        # cell_ratio=\
        #     RatSomatosensoryCortexCellRatioData(
        #         *args, **kwargs)
        # inhibitory_synapse_density=\
        #     RatSomatosensoryCortexInhibitorySynapseDensityData(
        #         *args, **kwargs)
        # synapse_density=\
        #     RatSomatosensoryCortexSynapseDensityData(
        #         *args, **kwargs)
        # return dict(
        #     cell_density=cell_density,
        #     cell_ratio=cell_ratio,
        #     inhibitory_synapse_density=inhibitory_synapse_density,
        #     synapse_density=synapse_density)
