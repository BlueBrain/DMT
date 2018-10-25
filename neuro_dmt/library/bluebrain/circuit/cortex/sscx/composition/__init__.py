"""Somatosensory cortex validations."""
import numpy as np
from dmt.vtk.plotting.comparison.barplot import BarPlotComparison
from neuro_dmt.utils import brain_regions
from neuro_dmt.models.bluebrain.circuit.adapter import BlueBrainModelAdapter

class SomatosensoryCortexCompositionValidation:
    """Mixin class that provides common attributes for
    somatosensory cortex composition validations."""

    def __init__(self,
            reference_data,
            circuit_geometry,
            sample_size=20,
            sampled_box_shape=50.*np.ones(3),
            *args, **kwargs):
        """..."""
        model_label\
            = "Blue Brain {} Circuit for SSCx".format(
                circuit_geometry.label)
        super().__init__(
            reference_data=reference_data,
            brain_region=brain_regions.sscx,
            plotter_type=BarPlotComparison,
            adapter=BlueBrainModelAdapter(
                brain_region=brain_regions.cortex, #consider removing this
                circuit_geometry=circuit_geometry,
                model_label=model_label,
                sample_size=sample_size,
                sampled_box_shape=sampled_box_shape,
                *args, **kwargs),
            *args, **kwargs)
