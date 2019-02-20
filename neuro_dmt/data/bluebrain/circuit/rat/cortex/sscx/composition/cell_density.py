"""Circuit composition data used for building and validating circuits
at the Blue Brain Project."""

import os
import numpy as np
from dmt.vtk.phenomenon\
    import Phenomenon
import dmt.vtk.utils.datasets as datasets
from dmt.vtk.utils.collections\
    import Record
from dmt.data\
    import ReferenceData
from neuro_dmt.measurement.parameter\
    import CorticalLayer
from neuro_dmt.data.bluebrain.circuit.rat.cortex.sscx.composition\
    import RatSSCxCompositionData

data_path=\
    os.path.join(
        "/gpfs/bbp.cscs.ch/home/sood",
        "work/validations/dmt",
        "examples/datasets/cortex/sscx/rat/composition",
        "cell_density")


class RatSSCxCellDensityData(
        RatSSCxCompositionData):
    """Somatosensory cortex cell density data for the Rat.
    """

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
                "Cell Density",
                "Count of cells in a unit volume",
                group="composition"),
            data_location=self.get_data_location(data_path),
            datasets=reference_datasets.datasets,
            primary=reference_datasets.primary,
            *args, **kwargs)

    def get_data_location(self,
            reference_data_dir):
        """..."""
        return{
            "defelipe2017": os.path.join(
                data_path,
                "DeFelipe2017"),
            "defelipe2014": os.path.join(
                data_path,
                "DeFelipe2014"),
            "defelipe2011": os.path.join(
                data_path,
                "DeFelipe2011"),
            "defelipe2002": os.path.join(
                data_path,
                "DeFelipe2002"),
            "meyer2010": os.path.join(
                data_path,
                "Meyer2010"),
            "sonja": os.path.join(
                data_path,
                "Sonja")}

    def get_reference_datasets(self,
            reference_data_dir):
        """Available reference data to be used to validate cell density."""
        defelipe2002=\
            datasets.load(
                reference_data_dir,
                "DeFelipe2002")
        defelipe2011=\
            datasets.load(
                reference_data_dir,
                "DeFelipe2011")
        defelipe2014=\
            datasets.load(
                reference_data_dir,
                "DeFelipe2014")
        defelipe2017=\
            datasets.load(
                reference_data_dir,
                "DeFelipe2017")
        meyer2010=\
            datasets.load(
                reference_data_dir,
                "Meyer2010")
        sonja=\
            datasets.load(
                reference_data_dir,
                "Sonja")

        df2014Densities=\
            np.vstack([
                ckt['densities']
                for ckt in defelipe2014.circuits.values()])
        defelipe2014.density_means=\
            np.mean(
                df2014Densities,
                axis=0)
        defelipe2014.density_stds=\
            np.std(
                df2014Densities,
                axis=0)
        df2017Densities=\
            np.vstack([
                ckt['densities']
                for ckt in defelipe2017.circuits.values()])
        defelipe2017.density_means=\
            np.mean(
                df2017Densities,
                axis=0)
        defelipe2017.density_stds=\
            np.std(
                df2017Densities,
                axis=0)

        return Record(
            primary=defelipe2017.short_name,
            datasets={
                defelipe2017.short_name: ReferenceData(
                    data=self.with_metadata(
                        defelipe2017,
                        self.summarized(
                            defelipe2017.density_means,
                            defelipe2017.density_stds,
                            scale_factor=0.8229e-3)),
                    description=defelipe2017.what),
                defelipe2014.short_name: ReferenceData(
                    data=self.with_metadata(
                        defelipe2014,
                        self.summarized(
                            defelipe2014.density_means,
                            defelipe2014.density_stds,
                            scale_factor=1.e-3)),
                    description=defelipe2014.what),
                defelipe2011.short_name: ReferenceData(
                    data=self.with_metadata(
                        defelipe2011,
                        self.summarized(
                            defelipe2011.density_means,
                            defelipe2011.density_stds)),
                    description=defelipe2011.what),
                defelipe2002.short_name: ReferenceData(
                    data=self.with_metadata(
                        defelipe2002,
                        self.summarized(
                            defelipe2002.density_means,
                            defelipe2002.density_stds)),
                    description=defelipe2002.what),
                meyer2010.short_name: ReferenceData(
                    data=self.with_metadata(
                        meyer2010,
                        self.summarized(
                            meyer2010.density_means,
                            meyer2010.density_stds)),
                    description=meyer2010.what),
                sonja.short_name: ReferenceData(
                    data=self.with_metadata(
                        sonja,
                        self.summarized(
                            sonja.density_means,
                            sonja.density_stds)),
                        description=sonja.what)})
