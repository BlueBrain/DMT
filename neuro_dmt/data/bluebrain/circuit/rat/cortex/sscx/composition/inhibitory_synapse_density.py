"""Circuit composition data used for building and validating circuits
at the Blue Brain Project."""

import os
import numpy as np
import dmt.vtk.datasets as datasets
from dmt.vtk.phenomenon import Phenomenon
from dmt.vtk.utils.collections import Record
from neuro_dmt.data.bluebrain.circuit.rat.cortex.sscx.composition\
    import RatSomatosensoryCortexCompositionData

class RatSomatosensoryCortexInhibitorySynapseDensityData(
        RatSomatosensoryCortexCompositionData):
    """..."""

    def __init__(self, *args, **kwargs):
                 
        """..."""
        super().__init__(
            phenomenon=Phenomenon(
                "Inhibitory Synapse Density",
                "Count of inhibitory synapses in a unit volume",
                group="composition"),
            *args, **kwargs)

    @classmethod
    def get_reference_datasets(cls, reference_data_dir):
        defelipe2011  = datasets.load(reference_data_dir, "DeFelipe2011")
        return Record(
            primary=defelipe2011.short_name,
            datasets={
                defelipe2011.short_name: cls.with_metadata(
                    defelipe2011,
                    cls.summarized(
                        defelipe2011.density_means,
                        defelipe2011.density_stds))})

