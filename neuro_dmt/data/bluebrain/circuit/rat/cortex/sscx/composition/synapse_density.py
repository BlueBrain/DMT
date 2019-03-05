
import os
import dmt.vtk.utils.datasets as datasets
from dmt.vtk.phenomenon\
    import Phenomenon
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
        "synapse_density")


class RatSSCxSynapseDensityData(
        RatSSCxCompositionData):
    """..."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        self.primary_spatial_parameter=\
            CorticalLayer()
        self.measurement_parameters=\
            [CorticalLayer().label]
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
            data_path):
        """..."""
        return{
            "defelipe2011": "DeFelipe2011",
            "defelipe2002": "DeFelipe2002",
            "anton2014": "AntonSanchez2014"}

    def get_reference_datasets(self,
            reference_data_dir):
        defelipe2011=\
            datasets.load(
                reference_data_dir,
                "DeFelipe2011")
        defelipe2002=\
            datasets.load(
                reference_data_dir,
                "DeFelipe2002")
        anton2014=\
            datasets.load(
                reference_data_dir,
                "AntonSanchez2014")
        return Record(
            primary=anton2014.short_name,
            datasets={
                defelipe2011.short_name: ReferenceData(
                    data=self.with_metadata(
                        defelipe2011,
                        self.summarized(
                            defelipe2011.density_means,
                            defelipe2011.density_stds)),
                    description=defelipe2011.what,
                    measurement_parameters=self.measurement_parameters),
                defelipe2002.short_name: ReferenceData(
                    data=self.with_metadata(
                        defelipe2002,
                        self.summarized(
                            defelipe2002.density_means,
                            defelipe2002.density_stds)),
                    description=defelipe2002.what,
                    measurement_parameters=self.measurement_parameters),
                anton2014.short_name: ReferenceData(
                    data=self.with_metadata(
                        anton2014,
                        self.summarized(
                            anton2014.density_means,
                            anton2014.density_stds)),
                    description=anton2014.what,
                    measurement_parameters=self.measurement_parameters)})
