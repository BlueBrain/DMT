"""Data for the circuit composition of Rat Somatosensory cortex."""
import os
import numpy as np
import pandas as pd
from dmt.vtk.phenomenon\
    import Phenomenon
from dmt.vtk.utils.collections\
    import Record
from dmt.vtk.utils.descriptor\
    import Field
from neuro_dmt.data.bluebrain.circuit.cortex.sscx.composition\
    import SSCxCompositionData


class RatSSCxCompositionData(
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
                "examples/datasets/cortex/sscx/rat/composition"))
                

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
            animal = "rat",
            phenomenon = phenomenon,
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
            import RatSSCxCellDensityData
        from neuro_dmt.data.bluebrain.circuit.rat.\
            cortex.sscx.composition.cell_ratio\
            import RatSSCxCellRatioData
        from neuro_dmt.data.bluebrain.circuit.rat.\
            cortex.sscx.composition.inhibitory_synapse_density\
            import  RatSSCxInhibitorySynapseDensityData
        from neuro_dmt.data.bluebrain.circuit.rat.\
            cortex.sscx.composition.synapse_density\
            import RatSSCxSynapseDensityData

        return dict(
            cell_density=RatSSCxCellDensityData,
            cell_ratio=RatSSCxCellRatioData,
            inhibitory_synapse_density=RatSSCxInhibitorySynapseDensityData,
            synapse_density=RatSSCxSynapseDensityData)
        
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
