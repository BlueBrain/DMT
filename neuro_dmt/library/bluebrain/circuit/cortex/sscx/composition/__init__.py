"""Somatosensory cortex validations."""
from abc import abstractmethod
import os
import numpy as np
from dmt.vtk.plotting.comparison.barplot import BarPlotComparison
from neuro_dmt.utils import brain_regions
from neuro_dmt.measurement.parameter import CorticalLayer
from neuro_dmt.models.bluebrain.circuit.O1.adapter import BlueBrainModelAdapter
from neuro_dmt.validations.circuit.composition.by_layer.cell_density\
    import CellDensityValidation
from neuro_dmt.data.bluebrain.circuit.cortex.sscx.composition.cell_density\
    import SomatosensoryCortexCellDensityData


class SomatosensoryCortexCellDensityValidation(CellDensityValidation):
    """..."""
    def __init__(self, circuit_build, sample_size=20,
                 sampled_box_shape=50.*np.ones(3),
                 *args, **kwargs):
        super().__init__(
            reference_data=SomatosensoryCortexCellDensityData(),
            brain_region=brain_regions.cortex,
            spatial_parameters={CorticalLayer()},
            plotter_type=BarPlotComparison,
            adapter=BlueBrainModelAdapter(
                brain_region=brain_regions.cortex,
                circuit_build=circuit_build,
                model_label="Blue Brain O1 Circuit for SSCx",
                sample_size=sample_size,
                sampled_box_shape=sampled_box_shape,
                *args, **kwargs))


def validation(validation_name, circuit_build):
    """..."""
    if validation_name == "cell_density":
        return SomatosensoryCortexCellDensityValidation(
            circuit_build=circuit_build)
    raise NotImplementedError("validation named {}".format(validation_name))
