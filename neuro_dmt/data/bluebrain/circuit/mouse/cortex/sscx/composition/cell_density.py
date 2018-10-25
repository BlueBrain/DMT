"""Cell density data for the Mouse."""
import os
import numpy as np
from dmt.vtk.phenomenon import Phenomenon
import dmt.vtk.datasets as datasets
from dmt.vtk.utils.collections import Record
from neuro_dmt.data.bluebrain.circuit.mouse.cortex.sscx.composition\
    import MouseSomatosensoryCortexCompositionData

class MouseSomatosensoryCortexCellDensityData(
        MouseSomatosensoryCortexCompositionData):
    """Somatosensory cortex cell density data for the Rat."""
    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(
            phenomenon=Phenomenon(
                "Cell Density",
                "Count of cells in a unit volume",
                group="composition"),
            *args, **kwargs)

    def get_reference_datasets(self, reference_data_dir):
        """...."""
        keller2018\
            = datasets.load(
                reference_data_dir,
                "Keller2018Feb14")
        defelipe2017\
            = datasets.load(
                reference_data_dir,
                "DeFelipe2014Rat")
        df2017Densities\
            = np.vstack([
                ckt["densities"]
                for ckt in defelipe2017.circuits.values()])
        defelipe2017.density_means\
            = np.mean(df2017Densities, axis=0)
        defelipe2017.density_stds\
            = np.std(df2017Densities, axis=0)

        return Record(
            primary=keller2018.short_name,
            datasets={
                keller2018.short_name: self.with_metadata(
                    keller2018,
                    self.summarized(
                        keller2018.density_means,
                        keller2018.density_stds,
                        scale_factor=1.0)),
                defelipe2017.short_name: self.with_metadata(
                    defelipe2017,
                    self.summarized(
                        defelipe2017.density_means,
                        defelipe2017.density_stds,
                        scale_factor=0.8229e-3) ) } )


