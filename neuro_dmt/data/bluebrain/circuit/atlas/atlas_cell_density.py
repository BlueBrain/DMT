import os
import numpy as np
import pandas as Pd
from voxcell.nexus.voxelbrain import Atlas
from dmt.vtk.phenomenon import Phenomenon
from dmt.vtk.utils.collections import Record
from neuro_dmt.data.bluebrain.circuit import BlueBrainCircuitCompositionData
from neuro_dmt.measurement.parameter import CorticalLayer
from neuro_dmt.utils.brain_regions import whole_brain

class AtlasBasedCellDensityData(
        BlueBrainCircuitCompositionData):
    """get cell density data from an atlas path"""

    def __init__(self, in_region, *args, by=[CorticalLayer()], **kwargs):
        """..."""
        self.in_region = in_region
        self.spatial_parameters = by
        # TODO: define brain region based on in_region and atlas
        super().__init__(*args, # spatial_parameters=by,
                         phenomenon=Phenomenon('cell_density', 'cell_density'),
                         brain_region=whole_brain, **kwargs)

    def get_reference_datasets(self,
                               reference_data_dir):
        """get the cell density data from the atlas at reference_data_dir"""
        atlas = Atlas.open(os.path.dirname(reference_data_dir))
        total_density = sum([atlas.load_data("[cell_density]{}"\
                                             .format(sclass)).raw
                             for sclass in ['EXC', 'INH']])
        # TODO: implement compatibility with parameters other than CorticalLayer
        region_mask = atlas.get_region_mask(self.in_region)
        cell_densities = [total_density[np.logical_and(
            atlas.get_region_mask("@.*{}[ab]?$".format(layer)).raw,
            region_mask.raw)]
                          for layer in self.spatial_parameters[0].values]
        means = [np.mean(td) for td in cell_densities]
        stds = [np.std(td) for td in cell_densities]

        df = =pd.DataFrame(
                'mean': means,
                'std': stds})

        return Record(
            primary='atlas',
            datasets = {
                'atlas': Record(data=df, label='atlas')})

    def get(self, phenomenon):
        return self
