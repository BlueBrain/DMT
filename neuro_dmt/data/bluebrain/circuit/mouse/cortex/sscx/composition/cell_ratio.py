"""Cell ratio data for the Mouse."""
import os
import numpy as np
from dmt.vtk.phenomenon import Phenomenon
import dmt.vtk.utils.datasets as datasets
from dmt.vtk.utils.collections import Record
from neuro_dmt.data.bluebrain.circuit.mouse.cortex.sscx.composition\
    import MouseSSCxCompositionData

class MouseSSCxCellRatioData(
        MouseSSCxCompositionData):
    """Somatosensory cortex cell density data for the Rat."""
    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(
            phenomenon=Phenomenon(
                "Cell Ratio",
                "Ratio of inhibitory to excitatory cells in a region.",
                group="composition"),
            *args, **kwargs)

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
