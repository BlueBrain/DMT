"""Circuit composition data used for building and validating circuits
at the Blue Brain Project."""

import os
import numpy as np
import dmt.vtk.datasets as datasets
from dmt.vtk.utils.collections import Record
from neuro_dmt.data.bluebrain.circuit.cortex.sscx.composition\
    import SomatosensoryCortexCompositionData

class SomatosensoryCortexCellRatioData(
        SomatosensoryCortexCompositionData):
    """..."""

    def __init__(self,
                 data=os.path.join("/gpfs/bbp.cscs.ch/home/sood",
                                   "work/validations/dmt",
                                   "examples/datasets/cortex/sscx/rat",
                                   "cell_ratio"),
                 *args, **kwargs):
        """..."""
        super().__init__(data, *args, **kwargs)

    @classmethod
    def get_reference_datasets(cls, reference_data_dir):
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
                ghobril2012.short_name: cls.with_metadata(
                    ghobril2012,
                    cls.summarized(
                        ghobril2012.ratio_means,
                        ghobril2012.ratio_stds) ),
                lefort2009.short_name: cls.with_metadata(
                    lefort2009,
                    cls.summarized(
                        lefort2009.ratio_means,
                        lefort2009.ratio_stds) ),
                beaulieu1992.short_name: cls.with_metadata(
                    beaulieu1992,
                    cls.summarized(
                        beaulieu1992.ratio_means,
                        beaulieu1992.ratio_stds) ) } )
