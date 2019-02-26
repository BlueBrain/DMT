import os
import numpy as np
import pandas as pd
from abc import abstractmethod
from voxcell.nexus.voxelbrain import Atlas
from dmt.vtk.phenomenon import Phenomenon
from dmt.vtk.utils.collections import Record
from dmt.data import ReferenceData
from neuro_dmt.measurement.parameter import CorticalLayer
from neuro_dmt.utils.brain_regions import whole_brain


class AtlasBasedInSilicoConstraint(ReferenceData):
    """define an in-silico constraint for a circuit based on the atlas"""

    def __init__(self, atlas_path, in_region, *args, **kwargs):
        """..."""
        # TODO: awkward situation: part of initialization we want before subclass-specific initialization, another part we want after
        self.in_region = in_region
        self.atlas = Atlas.open(atlas_path)
        self.spatial_parameters = [CorticalLayer()]
        self.data = self.data_from_atlas()

        super().__init__(*args, **kwargs)# spatial_parameters=by,
                         # phenomenon=Phenomenon('cell_density', 'cell_density'),
                         # brain_region=whole_brain, **kwargs)

    @abstractmethod
    def measure_mask(self, mask):
        """subclasses will measure a particular property of the provided mask"""
        pass

    def data_from_atlas(self):
        """get the cell density data from the atlas at reference_data_dir, by layer"""
        atlas = self.atlas
        # TODO: implement compatibility with parameters other than CorticalLayer
        region_mask = atlas.get_region_mask(self.in_region)
        measurements = [self.measure_mask(np.logical_and(
            atlas.get_region_mask("@.*{}[ab]?$".format(layer)).raw,
            region_mask.raw))
                        for layer in self.spatial_parameters[0].values]
        means = [np.mean(td) for td in measurements]
        stds = [np.std(td) for td in measurements]

        df = pd.DataFrame({
                'mean': means,
                'std': stds})
        df.index += 1

        return Record(data=df, label='atlas')


class AtlasBasedCellDensityData(AtlasBasedInSilicoConstraint):
    """get cell density data from an atlas path"""

    def __init__(self, atlas_path, in_region, *args, **kwargs):
        """..."""
        self.atlas = Atlas.open(atlas_path)
        self.total_density = sum([self.atlas.load_data("[cell_density]{}"
                                                       .format(sclass)).raw
                                  for sclass in ['EXC', 'INH']])
        super().__init__(atlas_path, in_region, *args, **kwargs)

    def measure_mask(self, mask):
        """measure cell density of mask"""
        return self.total_density[mask] / 1000


class AtlasBasedEIRatioData(AtlasBasedInSilicoConstraint):

    def __init__(self, atlas_path, in_region, *args, **kwargs):
        self.atlas = Atlas.open(atlas_path)
        self.ratio_density =\
            self.atlas.load_data("[cell_density]EXC").raw\
            / self.atlas.load_dta("[cell_density]INH").raw


    def measure_mask(self, mask):
        """measure cell density of mask"""
        return self.ratio_density[mask]
