"""Circuit composition data used for building and validating circuits
at the Blue Brain Project."""

import os
import numpy as np
import dmt.vtk.datasets as datasets
from dmt.vtk.phenomenon import Phenomenon
from dmt.vtk.utils.collections import Record
from neuro_dmt.data.bluebrain.circuit.rat.cortex.sscx.composition\
    import RatSomatosensoryCortexCompositionData

class RatSomatosensoryCortexCellRatioData(
        RatSomatosensoryCortexCompositionData):
    """..."""

    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(
            phenomenon=Phenomenon(
                "Cell Ratio",
                "Ratio of inhibitory to excitatory cells in a region.",
                group="composition"),
            *args, **kwargs)

    def get_reference_datasets(self, reference_data_dir):
        ghobril2012  = datasets.load(reference_data_dir, 'Ghobril2012')
        lefort2009   = datasets.load(reference_data_dir, 'Lefort2009')
        beaulieu1992 = datasets.load(reference_data_dir, 'Beaulieu1992')

        #Ghobril does not provide ratios, but counts

        cinh = np.array(ghobril2012.count_inh)
        call = np.array(ghobril2012.count_all)
        ghobril2012.ratio_means = cinh / call
        ghobril2012.ratio_stds  = np.sqrt(1./cinh + 1./call) * (cinh / call)

        return Record(
            primary=lefort2009.short_name,
            datasets={
                ghobril2012.short_name: self.with_metadata(
                    ghobril2012,
                    self.summarized(
                        ghobril2012.ratio_means,
                        ghobril2012.ratio_stds) ),
                lefort2009.short_name: self.with_metadata(
                    lefort2009,
                    self.summarized(
                        lefort2009.ratio_means,
                        lefort2009.ratio_stds) ),
                beaulieu1992.short_name: self.with_metadata(
                    beaulieu1992,
                    self.summarized(
                        beaulieu1992.ratio_means,
                        beaulieu1992.ratio_stds) ) } )
