"""Circuit composition data used for building and validating circuits
at the Blue Brain Project."""

import os
import numpy as np
import dmt.vtk.utils.datasets as datasets
from dmt.vtk.phenomenon\
    import Phenomenon
from dmt.data\
    import ReferenceData
from dmt.vtk.utils.collections\
    import Record
from neuro_dmt.measurement.parameter\
    import CorticalLayer
from neuro_dmt.data.bluebrain.circuit.rat.cortex.sscx.composition\
    import RatSSCxCompositionData

data_path=\
    os.path.join(
        "/gpfs/bbp.cscs.ch/home/sood",
        "work/validations/dmt",
        "examples/datasets/cortex/sscx/rat/composition",
        "inhibitory_synapse_density")

class RatSSCxInhibitorySynapseDensityData(
        RatSSCxCompositionData):
    """..."""

    def __init__(self,
            *args, **kwargs):
                 
        """..."""
        self.primary_spatial_parameter=\
            CorticalLayer()
        reference_datasets=\
            self.get_reference_datasets(
                data_path)
        super().__init__(
            phenomenon=Phenomenon(
                "Inhibitory Synapse Density",
                "Count of inhibitory synapses in a unit volume",
                group="composition"),
            data_location=self.get_data_location(data_path),
            datasets=reference_datasets.datasets,
            primary=reference_datasets.primary,
            *args, **kwargs)

    def get_data_location(self,
            reference_data_dir):
        """..."""
        return{
            "defelipe2011": "DeFelipe2011"}

    def get_reference_datasets(self,
            reference_data_dir):
        defelipe2011=\
            datasets.load(
                reference_data_dir,
                "DeFelipe2011")
        return Record(
            primary=defelipe2011.short_name,
            datasets={
                defelipe2011.short_name: ReferenceData(
                    data=self.with_metadata(
                        defelipe2011,
                        self.summarized(
                            defelipe2011.density_means,
                            defelipe2011.density_stds)),
                    description=defelipe2011.what)})

