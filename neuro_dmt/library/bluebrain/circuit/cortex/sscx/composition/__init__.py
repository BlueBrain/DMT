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
            sample_size=20,
            sampled_box_shape=50.*np.ones(3),
            *args, **kwargs):
        """..."""
        super().__init__(
            reference_data=reference_data,
            brain_region=brain_regions.sscx,
            adapter=BlueBrainModelAdapter(
                sample_size=sample_size,
                sampled_box_shape=sampled_box_shape,
                *args, **kwargs),
            *args, **kwargs)
