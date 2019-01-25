"""Reference data for somatosensory cortex composition validations
 of the mouse."""
import os
import numpy as np
import pandas as pd
from dmt.vtk.phenomenon import Phenomenon
from dmt.vtk.utils.collections import Record
from dmt.vtk.measurement.parameter.group import ParameterGroup
from neuro_dmt.measurement.parameter import CorticalLayer
from neuro_dmt.data.bluebrain.circuit.cortex.sscx.composition\
    import SomatosensoryCortexCompositionData

class MouseSomatosensoryCortexCompositionData(
        SomatosensoryCortexCompositionData):
    """..."""

    def __init__(self,
                phenomenon,
                data_location = os.path.join(
                    "/gpfs/bbp.cscs.ch/home/sood",
                    "work/validations/dmt",
                    "examples/datasets/cortex/sscx/mouse"),
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
            animal="mouse",
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
    def get_available_data(cls, *args, **kwargs):
        """Get reference data by phenomenon.

        Parameters
        --------------------------------------------------------------------
        phenomenon :: Either[str, Phenomenon]"""

        from neuro_dmt.data.bluebrain.circuit.mouse.\
            cortex.sscx.composition.cell_density\
            import MouseSomatosensoryCortexCellDensityData
        from neuro_dmt.data.bluebrain.circuit.mouse.\
            cortex.sscx.composition.cell_ratio\
            import MouseSomatosensoryCortexCellRatioData
        from neuro_dmt.data.bluebrain.circuit.mouse.\
            cortex.sscx.composition.inhibitory_synapse_density\
            import  MouseSomatosensoryCortexInhibitorySynapseDensityData
        from neuro_dmt.data.bluebrain.circuit.mouse.\
            cortex.sscx.composition.synapse_density\
            import MouseSomatosensoryCortexSynapseDensityData

        return dict(
            cell_density=MouseSomatosensoryCortexCellDensityData,
            cell_ratio=MouseSomatosensoryCortexCellRatioData,
            inhibitory_synapse_density=MouseSomatosensoryCortexInhibitorySynapseDensityData,
            synapse_density=MouseSomatosensoryCortexSynapseDensityData)

        # cell_density\
        #     = MouseSomatosensoryCortexCellDensityData(
        #         *args, **kwargs)
        # cell_ratio\
        #     = MouseSomatosensoryCortexCellRatioData(
        #         *args, **kwargs)
        # inhibitory_synapse_density\
        #     = MouseSomatosensoryCortexInhibitorySynapseDensityData(
        #         *args, **kwargs)
        # synapse_density\
        #     = MouseSomatosensoryCortexSynapseDensityData(
        #         *args, **kwargs)
        # return dict(
        #     cell_density=cell_density,
        #     cell_ratio=cell_ratio,
        #     inhibitory_synapse_density=inhibitory_synapse_density,
        #     synapse_density=synapse_density)
