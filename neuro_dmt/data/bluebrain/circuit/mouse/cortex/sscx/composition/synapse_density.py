
import os
import dmt.vtk.datasets as datasets
from dmt.vtk.phenomenon import Phenomenon
from dmt.vtk.utils.collections import Record
from neuro_dmt.data.bluebrain.circuit.mouse.cortex.sscx.composition\
    import MouseSomatosensoryCortexCompositionData

class MouseSomatosensoryCortexSynapseDensityData(
        MouseSomatosensoryCortexCompositionData):
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
        defelipe2018 = datasets.load(reference_data_dir, "DeFelipe2018")
        
        return Record(
            primary=defelipe2018.short_name,
            datasets={
                defelipe2018.short_name: self.with_metadata(
                    defelipe2018,
                    self.summarized(
                        defelipe2018.density_means,
                        defelipe2018.density_stds) ) } )
