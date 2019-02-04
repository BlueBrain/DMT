"""Reference data for somatosensory cortex composition validations
 of the mouse."""
import os
import numpy as np
import pandas as pd
from dmt.vtk.phenomenon\
    import Phenomenon
from dmt.vtk.utils.collections\
    import Record
from dmt.vtk.utils.descriptor\
    import Field
from dmt.vtk.measurement.parameter.group\
    import ParameterGroup
from neuro_dmt.measurement.parameter\
    import CorticalLayer
from neuro_dmt.data.bluebrain.circuit.cortex.sscx.composition\
    import SSCxCompositionData

class MouseSSCxCompositionData(
        SSCxCompositionData):
    """..."""

    data_location=\
        Field(
            __name__ = "data_location",
            __type__ = str,
            __doc__ = """This should be the directory where composition data is
            located, under which individual files contain measurement data of a
            single phenomenon.""",
            __default__ = os.path.join(
                "/gpfs/bbp.cscs.ch/home/sood",
                "work/validations/dmt",
                "examples/datasets/cortex/sscx/mouse/composition"))
    def __init__(self,
            phenomenon,
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
            import MouseSSCxCellDensityData
        from neuro_dmt.data.bluebrain.circuit.mouse.\
            cortex.sscx.composition.cell_ratio\
            import MouseSSCxCellRatioData
        from neuro_dmt.data.bluebrain.circuit.mouse.\
            cortex.sscx.composition.inhibitory_synapse_density\
            import  MouseSSCxInhibitorySynapseDensityData
        from neuro_dmt.data.bluebrain.circuit.mouse.\
            cortex.sscx.composition.synapse_density\
            import MouseSSCxSynapseDensityData

        return dict(
            cell_density=MouseSSCxCellDensityData,
            cell_ratio=MouseSSCxCellRatioData,
            inhibitory_synapse_density=MouseSSCxInhibitorySynapseDensityData,
            synapse_density=MouseSSCxSynapseDensityData)

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
