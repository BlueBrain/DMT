
import os
import dmt.vtk.datasets as datasets
from dmt.vtk.phenomenon import Phenomenon
from dmt.vtk.utils.collections import Record
from neuro_dmt.data.bluebrain.circuit.rat.cortex.sscx.composition\
    import RatSomatosensoryCortexCompositionData

class RatSomatosensoryCortexSynapseDensityData(
        RatSomatosensoryCortexCompositionData):
    """..."""

    def __init__(self,
                 data=os.path.join("/gpfs/bbp.cscs.ch/home/sood",
                                   "work/validations/dmt",
                                   "examples/datasets/cortex/sscx/rat",
                                   "synapse_density"),
                 *args, **kwargs):
        """..."""
        super().__init__(
            phenomenon=Phenomenon(
                "Synapse Density",
                "Count of synapses in a unit volume",
                group="composition"),
            *args, **kwargs)

    @classmethod
    def get_reference_datasets(cls, reference_data_dir):
        defelipe2011 = datasets.load(reference_data_dir, "DeFelipe2011")
        defelipe2002 = datasets.load(reference_data_dir, "DeFelipe2002")
        anton2014 = datasets.load(reference_data_dir, "AntonSanchez2014")
        
        return Record(
            primary=anton2014.short_name,
            datasets={
                defelipe2011.short_name: cls.with_metadata(
                    defelipe2011,
                    cls.summarized(
                        defelipe2011.density_means,
                        defelipe2011.density_stds)),
                defelipe2002.short_name: cls.with_metadata(
                    defelipe2002,
                    cls.summarized(
                        defelipe2002.density_means,
                        defelipe2002.density_stds)),
                anton2014.short_name: cls.with_metadata(
                    anton2014,
                    cls.summarized(
                        anton2014.density_means,
                        anton2014.density_stds))})
