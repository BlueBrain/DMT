"""Somatosensory cortex validations."""
import numpy as np
from dmt.vtk.plotting.comparison.barplot import BarPlotComparison
from neuro_dmt.utils import brain_regions
from neuro_dmt.measurement.parameter import CorticalLayer
from neuro_dmt.models.bluebrain.circuit.adapter import BlueBrainModelAdapter

class SomatosensoryCortexCompositionValidation:
    """Mixin class that provides common attributes for
    somatosensory cortex composition validations."""

    def __init__(self,
            reference_data,
            circuit_build,
            sample_size=20,
            sampled_box_shape=50.*np.ones(3),
            *args, **kwargs):
        """..."""
        spatial_parameters \
            = kwargs.get(
                "spatial_parameters",
                {CorticalLayer()})
        super().__init__(
            reference_data=reference_data,
            brain_region=brain_regions.sscx,
            spatial_parameters=spatial_parameters,
            plotter_type=BarPlotComparison,
            adapter=BlueBrainModelAdapter(
                brain_region=brain_regions.cortex,
                circuit_build=circuit_build,
                model_label="Blue Brain O1 Circuit for SSCx",
                sample_size=sample_size,
                sampled_box_shape=sampled_box_shape,
                *args, **kwargs),
            *args, **kwargs)
