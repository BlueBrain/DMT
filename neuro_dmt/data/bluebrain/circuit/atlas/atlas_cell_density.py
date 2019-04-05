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

    def __init__(self,
            atlas_path,
            in_region,
            *args, **kwargs):
        """..."""
        # TODO: awkward situation: part of initialization we want before subclass-specific initialization, another part we want after
        self.in_region = in_region
        self.atlas = Atlas.open(atlas_path)
        self.spatial_parameters = [CorticalLayer()]
        super().__init__(
            measurement_parameters=[
                sp.label for sp in self.spatial_parameters],
            *args, **kwargs)

    @abstractmethod
    def measure_mask(self, mask):
        """subclasses will measure a particular property of the provided mask"""
        pass

    @property
    def data(self):
        return self.data_from_atlas()

    @staticmethod
    def nan_filled(array_with_nans, value=0.):
        """..."""
        array_filled=\
            np.zeros(
                array_with_nans.shape)
        nan_indexes=\
            ~np.isnan(array_with_nans)
        array_filled[nan_indexes]=\
            array_with_nans[nan_indexes]
        return array_filled

    def data_from_atlas(self):
        """get the cell density data from the atlas at reference_data_dir, by layer"""
        atlas = self.atlas
        # TODO: implement compatibility with parameters other than CorticalLayer
        region_mask=\
            atlas.get_region_mask(
                self.in_region)
        measurements=[
            self.measure_mask(
                np.logical_and(
                    atlas.get_region_mask(
                        "@.*{}[ab]?$".format(layer)).raw,
                    region_mask.raw))
            for layer in self.spatial_parameters[0].values]
        means = [np.mean(td) for td in measurements]
        stds = [np.std(td) for td in measurements]

        return\
            Record(
                label="atlas",
                data=pd.DataFrame(
                    {"mean": means, "std": stds},
                    index=pd.Index(
                        [1,2,3,4,5,6],
                        name="layer")),
                region_label="isocortex",
                uri="not-available",
                what="data from atlas voxels",
                citation="not-available")


class AtlasBasedCellDensityData(AtlasBasedInSilicoConstraint):
    """get cell density data from an atlas path"""

    def __init__(self, atlas_path, in_region, *args, **kwargs):
        """..."""
        self.total_density=\
            None
        super().__init__(
            atlas_path,
            in_region,
            *args, **kwargs)

    def measure_mask(self, mask):
        """measure cell density of mask"""
        if self.total_density is None:
            self.total_density=\
                sum([
                    self.atlas.load_data("[cell_density]{}".format(sclass)).raw
                    for sclass in ['EXC', 'INH']])
        return self.total_density[mask] / 1000.


class AtlasBasedEIRatioData(AtlasBasedInSilicoConstraint):

    def __init__(self, atlas_path, in_region, *args, **kwargs):
        self._excitatory_density=\
            None
        self._inhibitory_density=\
            None
        self._ratio=\
            None
        super().__init__(
            atlas_path,
            in_region,
            *args, **kwargs)
    def measure_mask(self, mask):
        """measure cell density of mask"""
        if self._ratio is None:
            self._excitatory_density=\
                self.nan_filled(
                    self.atlas.load_data(
                        "[cell_density]EXC").raw)
            self._inhibitory_density=\
                self.nan_filled(
                    self.atlas.load_data(
                        "[cell_density]INH").raw)
            self._ratio=\
                self._inhibitory_density / (1.e-9 + self._excitatory_density)
        return\
            self._ratio[mask]
