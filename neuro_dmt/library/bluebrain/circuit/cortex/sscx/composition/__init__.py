"""Somatosensory cortex validations."""
from abc import abstractmethod
import os
import numpy as np
from dmt.vtk.plotting.comparison.barplot import BarPlotComparison
from neuro_dmt.utils import brain_regions
from neuro_dmt.measurement.parameter import CorticalLayer
from neuro_dmt.models.bluebrain.circuit.O1.adapter import BlueBrainModelAdapter
from neuro_dmt.validations.circuit.composition.by_layer import\
    CellDensityValidation,\
    CellRatioValidation

from neuro_dmt.data.bluebrain.circuit.cortex.sscx.composition\
    import SomatosensoryCortexCellDensityData
from neuro_dmt.data.bluebrain.circuit.cortex.sscx.composition.cell_ratio\
    import SomatosensoryCortexCellRatioData
from neuro_dmt.data.bluebrain.circuit.cortex.sscx.composition.\
    inhibitory_synapse_density\
    import SomatosensoryCortexInhibitorySynapseDensityData
from neuro_dmt.data.bluebrain.circuit.cortex.sscx.composition.\
    synapse_density\
    import SomatosensoryCortexSynapseDensityData


class SomatosensoryCortexCellDensityValidation(
        CellDensityValidation):
    """..."""
    def __init__(self,
            circuit_build,
            sample_size=20,
            sampled_box_shape=50.*np.ones(3),
            *args, **kwargs):
        """..."""
        super().__init__(
            reference_data=SomatosensoryCortexCellDensityData(),
            brain_region=brain_regions.cortex,
            spatial_parameter=CorticalLayer(),
            plotter_type=BarPlotComparison,
            adapter=BlueBrainModelAdapter(
                brain_region=brain_regions.cortex,
                circuit_build=circuit_build,
                model_label="Blue Brain O1 Circuit for SSCx",
                sample_size=sample_size,
                sampled_box_shape=sampled_box_shape,
                *args, **kwargs),
            *args, **kwargs)


class SomatosensoryCortexCellRatioValidation(
        CellRatioValidation):
    """..."""
    def __init__(self,
            circuit_build,
            sample_size=20,
            sampled_box_shape=50.*np.ones(3),
            *args, **kwargs):
        super().__init__(
            reference_data=SomatosensoryCortexCellRatioData(),
            brain_region=brain_regions.cortex,
            spatial_parameter=CorticalLayer(),
            plotter_type=BarPlotComparison,
            adapter=BlueBrainModelAdapter(
                brain_region=brain_regions.cortex,
                circuit_build=circuit_build,
                model_label="Blue Brain O1 Circuit for SSCx",
                sample_size=sample_size,
                sampled_box_shape=sampled_box_shape,
                *args, **kwargs),
            *args, **kwargs)


class SomatosensoryCortexCellRatioValidation(
        CellRatioValidation):
    """..."""
    def __init__(self,
            circuit_build,
            sample_size=20,
            sampled_box_shape=50.*np.ones(3),
            *args, **kwargs):
        super().__init__(
            reference_data=SomatosensoryCortexCellRatioData(),
            brain_region=brain_regions.cortex,
            spatial_parameter=CorticalLayer(),
            plotter_type=BarPlotComparison,
            adapter=BlueBrainModelAdapter(
                brain_region=brain_regions.cortex,
                circuit_build=circuit_build,
                model_label="Blue Brain O1 Circuit for SSCx",
                sample_size=sample_size,
                sampled_box_shape=sampled_box_shape,
                *args, **kwargs),
            *args, **kwargs)



def validation(
        validation_name,
        circuit_build,
        output_dir_path=os.getcwd()):
    """..."""
    available_validations = dict(
        cell_density=SomatosensoryCortexCellDensityValidation,
        cell_ratio=SomatosensoryCortexCellRatioValidation)
    try:
        return available_validations[validation_name](
            circuit_build=circuit_build,
            output_dir_path=output_dir_path)
    except KeyError as e:
        raise NotImplementedError(
            "Validation named {}.\n \tKeyError: {}.\n Available validations: \n {}"\
            .format(
                validation_name, e,
                '\n'.join(
                    "\t{}".format(v) for v in available_validations.keys())) )
