"""Validation of the somatosensory-cortex connectome."""
import numpy as np
from neuro_dmt.utils\
    import brain_regions
from neuro_dmt.models.bluebrain.circuit.adapter\
    import BlueBrainModelAdapter

class SomatosensoryCortexConnectomeValidation:
    """Mixin to provide common attributes
    for all SSCx connectome validations."""

    def __init__(
            reference_data,
            sample_size=20,
            sample_box_shape=50.*np.ones(3),
            *args, **kwargs):
        """..."""
        super().__init__(
            reference_data=reference_data,
            brain_region=brain_region.sscx,
            adapter=BlueBrainModelAdapter(
                samples_size=sample_size,
                sampled_box_shape=sampled_box_shape,
                *args, **kwargs),
            *args, **kwargs)
