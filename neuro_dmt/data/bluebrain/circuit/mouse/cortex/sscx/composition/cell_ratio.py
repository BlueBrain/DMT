"""Cell ratio data for the Mouse."""
import os
import numpy as np
from dmt.vtk.phenomenon import Phenomenon
import dmt.vtk.utils.datasets as datasets
from dmt.vtk.utils.collections import Record
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
        "cell_ratio")

def get_lefort_data(
        file_name="LeFort2009"):
    """..."""
    data=\
        datasets.load(
            data_path,
            "LeFort2009")
    count_inhibitory=\
        np.array(data.count_inh)
    count_all=\
        np.array(data.count_all)
    data.ratio_means=\
        count_inhibitory / count_all
    data.ratio_stds=\
        np.sqrt(1./count_inhibitory + 1./count_all)\
        * (count_inhibitory/count_all)
    return data

class MouseSSCxCellRatioData(
        MouseSSCxCompositionData):
    """Somatosensory cortex cell density data for the Rat.
    """
    def __init__(self,
            *args, **kwargs):
        """Initialize Me"""
        self.primary_spatial_parameter=\
            CorticalLayer()
        lefort2009=\
            self.summarized_with_metadata(
                get_lefort_data())
        super().__init__(
            phenomenon=Phenomenon(
                "Cell Ratio",
                "Ratio of inhibitory to excitatory cells in a region.",
                group="composition"),
            data_location={
                lefort2009.label: os.path.join(
                   data_path,
                    "LeFort2009")},
            datasets={
                lefort2009.label: ReferenceData(
                    data=lefort2009,
                    description=lefort2009.what,
                    measurement_parameters=[CorticalLayer().label])},
            primary=lefort2009.label,
            *args, **kwargs)

    def summarized_with_metadata(self,
            dataset):
        """..."""
        return\
            self.with_metadata(
                dataset,
                self.summarized(
                    dataset.ratio_means,
                    dataset.ratio_stds))

    def get_reference_datasets(self, reference_data_dir):
        """...."""
        lefort2009\
            = datasets.load(reference_data_dir, "LeFort2009")
        cinh = np.array(lefort2009.count_inh)
        call = np.array(lefort2009.count_all)
        lefort2009.ratio_means = cinh / call
        lefort2009.ratio_stds = np.sqrt(1./cinh + 1./call) * (cinh/call)

        return Record(
            primary=lefort2009.short_name,
            datasets={
                lefort2009.short_name: self.with_metadata(
                    lefort2009,
                    self.summarized(
                        lefort2009.ratio_means,
                        lefort2009.ratio_stds) ) } )
