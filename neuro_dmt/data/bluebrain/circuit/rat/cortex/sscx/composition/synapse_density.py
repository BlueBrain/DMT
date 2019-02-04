
import os
import dmt.vtk.utils.datasets as datasets
from dmt.vtk.phenomenon import Phenomenon
from dmt.vtk.utils.collections import Record
from neuro_dmt.data.bluebrain.circuit.rat.cortex.sscx.composition\
    import RatSSCxCompositionData

class RatSSCxSynapseDensityData(
        RatSSCxCompositionData):
    """..."""

    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(
            phenomenon=Phenomenon(
                "Synapse Density",
                "Count of synapses in a unit volume",
                group="composition"),
            *args, **kwargs)

    def get_reference_datasets(self, reference_data_dir):
        defelipe2011 = datasets.load(reference_data_dir, "DeFelipe2011")
        defelipe2002 = datasets.load(reference_data_dir, "DeFelipe2002")
        anton2014 = datasets.load(reference_data_dir, "AntonSanchez2014")
        
        return Record(
            primary=anton2014.short_name,
            datasets={
                defelipe2011.short_name: self.with_metadata(
                    defelipe2011,
                    self.summarized(
                        defelipe2011.density_means,
                        defelipe2011.density_stds)),
                defelipe2002.short_name: self.with_metadata(
                    defelipe2002,
                    self.summarized(
                        defelipe2002.density_means,
                        defelipe2002.density_stds)),
                anton2014.short_name: self.with_metadata(
                    anton2014,
                    self.summarized(
                        anton2014.density_means,
                        anton2014.density_stds))})
