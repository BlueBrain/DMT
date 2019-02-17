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
from neuro_dmt.data.bluebrain.circuit.mouse.cortex.sscx.composition\
    import MouseSSCxCompositionData


class MouseSSCxCellDensityData(
        MouseSSCxCompositionData):
    """Somatosensory cortex cell density data for the Rat.
    """
    @staticmethod
    def load_defelipe_data(
            data_path,
            file_name):
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

    @staticmethod
    def load_dankeller_data(
            data_path,
            file_name):
        """..."""
        return\
            datasets.load(
                data_path,
                file_name)

    def __init__(self, *args, **kwargs):
        """..."""
        self.data_path=\
            os.path.join(
                "/gpfs/bbp.cscs.ch/home/sood",
                "work/validations/dmt",
                "examples/datasets/cortex/sscx/mouse/composition",
                "cell_density")
        self.data_location={
            'keller2018': "Keller2018Feb14",
            'defelipe2017': "DeFelipe2014Rat"}
        self.get_data={
            "keller2018": self.load_dankeller_data,
            "defelipe2017": self.load_defelipe_data}
        self.primary=\
            "keller2018"
        super().__init__(
            phenomenon=Phenomenon(
                "Cell Density",
                "Count of cells in a unit volume",
                group="composition"),
            *args, **kwargs)

    def _load_one_from_location(self,
            data_label,
            file_name,
            scale_factor=1.0):
        """..."""
        data=\
            self.get_data[data_label](
                self.data_path,
                file_name)
        self.logger.debug(
            self.logger.get_source_info(),
            """loaded mouse cell density data record {}"""\
            .format(data))
        return self.with_metadata(
            data,
            self.summarized(
                data.density_means,
                data.density_stds,
                scale_factor=1.0))

    def get_reference_datasets(self,
            reference_data_dir):
        """...."""
        keller2018=\
            datasets.load(
                reference_data_dir,
                "Keller2018Feb14")
        defelipe2017=\
            datasets.load(
                reference_data_dir,
                "DeFelipe2014Rat")
        df2017Densities=\
            np.vstack([
                ckt["densities"]
                for ckt in defelipe2017.circuits.values()])
        defelipe2017.density_means=\
            np.mean(df2017Densities, axis=0)
        defelipe2017.density_stds=\
            np.std(df2017Densities, axis=0)
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


