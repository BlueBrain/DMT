"""Circuit composition data used for building and validating circuits
at the Blue Brain Project."""

import os
import numpy as np
from dmt.vtk.phenomenon import Phenomenon
import dmt.vtk.datasets as datasets
from dmt.vtk.utils.collections import Record
from neuro_dmt.data.bluebrain.circuit.rat.cortex.sscx.composition\
    import RatSomatosensoryCortexCompositionData

class RatSomatosensoryCortexCellDensityData(
        RatSomatosensoryCortexCompositionData):
    """Somatosensory cortex cell density data for the Rat."""

    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(
            phenomenon=Phenomenon(
                "Cell Density",
                "Count of cells in a unit volume",
                group="composition"),
            *args, **kwargs)

    @classmethod
    def get_reference_datasets(cls, reference_data_dir):
        """Available reference data to be used to validate cell density."""
        defelipe2002 = datasets.load(reference_data_dir, "DeFelipe2002")
        defelipe2011 = datasets.load(reference_data_dir, "DeFelipe2011")
        defelipe2014 = datasets.load(reference_data_dir, "DeFelipe2014")
        defelipe2017 = datasets.load(reference_data_dir, "DeFelipe2017")
        meyer2010    = datasets.load(reference_data_dir, "Meyer2010")
        sonja        = datasets.load(reference_data_dir, "Sonja")

        df2014Densities = np.vstack([
            ckt['densities'] for ckt in defelipe2014.circuits.values()])
        
        defelipe2014.density_means = np.mean(df2014Densities, axis=0)
        defelipe2014.density_stds  = np.std(df2014Densities, axis=0)
    
        df2017Densities = np.vstack([
            ckt['densities'] for ckt in defelipe2017.circuits.values()])
        
        defelipe2017.density_means = np.mean(df2017Densities, axis=0)
        defelipe2017.density_stds  = np.std(df2017Densities, axis=0)

        return Record(
            primary=defelipe2017.short_name,
            datasets={
                defelipe2017.short_name: cls.with_metadata(
                    defelipe2017,
                    cls.summarized(
                        defelipe2017.density_means,
                        defelipe2017.density_stds,
                        scale_factor=0.8229e-3) ),
                defelipe2014.short_name: cls.with_metadata(
                    defelipe2014,
                    cls.summarized(
                        defelipe2014.density_means,
                        defelipe2014.density_stds,
                        scale_factor=1.e-3) ),
                defelipe2011.short_name: cls.with_metadata(
                    defelipe2011,
                    cls.summarized(
                        defelipe2011.density_means,
                        defelipe2011.density_stds) ),
                defelipe2002.short_name: cls.with_metadata(
                    defelipe2002,
                    cls.summarized(
                        defelipe2002.density_means,
                        defelipe2002.density_stds) ),
                meyer2010.short_name: cls.with_metadata(
                    meyer2010,
                    cls.summarized(
                        meyer2010.density_means,
                        meyer2010.density_stds) ),
                sonja.short_name: cls.with_metadata(
                    sonja,
                    cls.summarized(
                        sonja.density_means,
                        sonja.density_stds) ) } )
