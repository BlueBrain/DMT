"""Circuit composition data used for building and validating circuits
at the Blue Brain Project."""

import os
import numpy as np
import dmt.vtk.utils.datasets as datasets
from dmt.vtk.phenomenon\
    import Phenomenon
from dmt.vtk.utils.collections\
    import Record
from dmt.data\
    import ReferenceData
from neuro_dmt.measurement.parameter\
    import CorticalLayer
from neuro_dmt.data.bluebrain.circuit.mouse.cortex.sscx.composition\
    import MouseSSCxCompositionData

data_path=\
    os.path.join(
        "/gpfs/bbp.cscs.ch/home/sood",
        "work/validations/dmt",
        "examples/datasets/cortex/sscx/mouse/composition",
        "inhibitory_synapse_density")

class MouseSSCxInhibitorySynapseDensityData(
        MouseSSCxCompositionData):
    """..."""

    def __init__(self, *args, **kwargs):
        """Initialize Me"""
        self.primary_spatial_parameter=\
            CorticalLayer()
        defelipe2018=\
            self.summarized_with_metadata(
                datasets.load(
                    data_path,
                    "DeFelipe2018"))
        super().__init__(
            phenomenon=Phenomenon(
                "Inhibitory Synapse Density",
                "Count of inhibitory synapses in a unit volume",
                group="composition"),
            data_location={
                defelipe2018.label: os.path.join(
                    data_path,
                    "DeFelipe2018")},
            datasets={
                defelipe2018.label: ReferenceData(
                    data=defelipe2018,
                    description=defelipe2018.what,
                    measurement_parameters=[CorticalLayer().label])},
            primary=defelipe2018.label,
            *args, **kwargs)

    def summarized_with_metadata(self,
            dataset):
        """..."""
        return\
            self.with_metadata(
                dataset,
                self.summarized(
                    dataset.density_means,
                    dataset.density_stds))

    def get_reference_datasets(self,
            reference_data_dir):
        defelipe2018=\
            datasets.load(
                reference_data_dir,
                "DeFelipe2018")
        return\
            Record(
                primary=defelipe2018.short_name,
                datasets={
                    defelipe2018.short_name: self.with_metadata(
                        defelipe2018,
                        self.summarized(
                            defelipe2018.density_means,
                            defelipe2018.density_stds))})

