"""Circuit composition data used for building and validating circuits
at the Blue Brain Project."""

import os
import numpy as np
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
        "cell_ratio")


class RatSSCxCellRatioData(
        RatSSCxCompositionData):
    """..."""

    def __init__(self, *args, **kwargs):
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
                "Cell Ratio",
                "Ratio of inhibitory to excitatory cells in a region.",
                group="composition"),
            data_location=self.get_data_location(data_path),
            datasets=reference_datasets.datasets,
            primary=reference_datasets.primary,
            *args, **kwargs)

    def get_data_location(self,
            data_path):
        """..."""
        return{
            "ghobril2012": os.path.join(
                data_path,
                "Ghobril2012"),
            "lefort2009": os.path.join(
                data_path,
                "Lefort2009"),
            "beaulieu1992": os.path.join(
                data_path,
                "Beaulieu1992")}

    def get_reference_datasets(self,
            reference_data_dir):
        ghobril2012=\
            datasets.load(
                reference_data_dir,
                'Ghobril2012')
        lefort2009=\
            datasets.load(
                reference_data_dir,
                'Lefort2009')
        beaulieu1992=\
            datasets.load(
                reference_data_dir,
                'Beaulieu1992')

        #Ghobril does not provide ratios, but counts

        count_inhibitory=\
            np.array(
                ghobril2012.count_inh)
        count_all=\
            np.array(
                ghobril2012.count_all)
        ghobril2012.ratio_means= count_inhibitory / count_all
        ghobril2012.ratio_stds=\
            np.sqrt(
                1./count_inhibitory + 1./count_all)\
                * (count_inhibitory / count_all)
        return Record(
            primary=lefort2009.short_name,
            datasets={
                ghobril2012.short_name: ReferenceData(
                    data=self.with_metadata(
                        ghobril2012,
                        self.summarized(
                            ghobril2012.ratio_means,
                            ghobril2012.ratio_stds)),
                    description=ghobril2012.what,
                    measurement_parameters=self.measurement_parameters),
                lefort2009.short_name: ReferenceData(
                    data=self.with_metadata(
                        lefort2009,
                        self.summarized(
                            lefort2009.ratio_means,
                            lefort2009.ratio_stds)),
                    description=lefort2009.what,
                    measurement_parameters=self.measurement_parameters),
                beaulieu1992.short_name: ReferenceData(
                    data=self.with_metadata(
                        beaulieu1992,
                        self.summarized(
                            beaulieu1992.ratio_means,
                            beaulieu1992.ratio_stds)),
                    description=beaulieu1992.what,
                    measurement_parameters=self.measurement_parameters)})
