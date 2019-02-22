"""Cell density data for the Mouse."""
import os
import numpy as np
from dmt.vtk.phenomenon\
    import Phenomenon
from dmt.vtk.utils.descriptor\
    import Field
import dmt.vtk.utils.datasets as datasets
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
        "cell_density")

def get_defelipe_data(
        file_name="DeFelipe2014Rat"):
    """"..."""
    data=\
        datasets.load(
            data_path,
            file_name)
    df2017Densities=\
        np.vstack([
            ckt["densities"]
            for ckt in data.circuits.values()])
    data.density_means=\
        np.mean(
            df2017Densities, axis=0)
    data.density_stds=\
        np.std(
            df2017Densities, axis=0)
    return data

def get_dankeller_data(
        file_name="Keller2018Feb14"):
    """..."""
    return\
        datasets.load(
            data_path,
            file_name)


class MouseSSCxCellDensityData(
        MouseSSCxCompositionData):
    """..."""
    def __init__(self,
            *args, **kwargs):
        """Initialize Me"""
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
            data_path):
        """..."""
        return{
            "keller2018": os.path.join(
                data_path,
                "Keller2018Feb14"),
            "defelipe2014": os.path.join(
                data_path,
                "DeFelipe2014Rat")}

    def get_reference_datasets(self,
            reference_data_dir,
            *args, **kwargs):
        """..."""
        keller2018=\
            self.summarized_with_metadata(
                get_dankeller_data(),
                scale_factor=1.0)
        defelipe2014=\
            self.summarized_with_metadata(
                    get_defelipe_data(),
                    scale_factor=0.8229e-3)
        return\
            Record(
                primary=keller2018.label,
                datasets={
                    keller2018.label: ReferenceData(
                        data=keller2018,
                        description=keller2018.what,
                        measurement_parameters=[CorticalLayer().label]),
                    defelipe2014.label: ReferenceData(
                        data=defelipe2014,
                        description=defelipe2014.what,
                        measurement_parameters=[CorticalLayer().label])})

    def summarized_with_metadata(self,
            dataset,
            scale_factor=1.0):
        """..."""
        return\
            self.with_metadata(
                dataset,
                self.summarized(
                    dataset.density_means,
                    dataset.density_stds,
                    scale_factor=scale_factor))
                     
    # @classmethod
    # def get_reference_datasets(self,
    #         reference_data_dir,
    #         *args, **kwargs):
    #     """...."""
    #     keller2018=\
    #         datasets.load(
    #             reference_data_dir,
    #             "Keller2018Feb14")
    #     defelipe2017=\
    #         datasets.load(
    #             reference_data_dir,
    #             "DeFelipe2014Rat")
    #     df2017Densities=\
    #         np.vstack([
    #             ckt["densities"]
    #             for ckt in defelipe2017.circuits.values()])
    #     defelipe2017.density_means=\
    #         np.mean(df2017Densities, axis=0)
    #     defelipe2017.density_stds=\
    #         np.std(df2017Densities, axis=0)
    #     return Record(
    #         primary=keller2018.short_name,
    #         datasets={
    #             keller2018.short_name: self.with_metadata(
    #                 keller2018,
    #                 self.summarized(
    #                     keller2018.density_means,
    #                     keller2018.density_stds,
    #                     scale_factor=1.0)),
    #             defelipe2017.short_name: self.with_metadata(
    #                 defelipe2017,
    #                 self.summarized(
    #                     defelipe2017.density_means,
    #                     defelipe2017.density_stds,
    #                     scale_factor=0.8229e-3) ) } )
