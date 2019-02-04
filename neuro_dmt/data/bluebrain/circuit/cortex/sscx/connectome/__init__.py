"""Circuit connectome data for the Somatosensory cortex."""
import pandas as pd
from dmt.vtk.utils.collections import Record
from dmt.vtk.phenomenon import Phenomenon
from neuro_dmt.utils import brain_regions
from neuro_dmt.data.bluebrain.circuit.cortex\
    import CortexConnectomeData

class SSCxConnectomeData(
        CortexConnectomeData):
    """..."""
    _available_data = []

    def __init__(self,
            animal,
            phenomenon,
            *args, **kwargs):
        """..."""
        super().__init__(
            phenomenon,
            animal=animal,
            brain_region=brain_regions.sscx,
            *args, **kwargs)

    def with_metadata(
            reference_dataset,
            reference_dataframe):
        """Add metadata to the data.
        This method is a similar to the one defined for composition
        reference data --- """
        return Record(
            label = reference_dataset.get(
                "short_name",
                "unknown"),
            uri = reference_dataset.get(
                "uri",
                reference_dataset.get(
                    "url",
                    "unknown")),
            citation = reference_dataset.get(
                "citation",
                "unknown"),
            what = reference_dataset.get(
                "what",
                "dunno"),
            data=reference_dataframe)

    
