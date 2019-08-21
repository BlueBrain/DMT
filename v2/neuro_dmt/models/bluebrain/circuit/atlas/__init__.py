"""
Utilities to handle the atlas behind a circuit.
Bluebrain circuits are built against a brain atlas.
"""

import numpy
import pandas
from voxcell.nexus.voxelbrain import Atlas
from voxcell import VoxelData
from dmt.tk.field import Field, lazyfield, WithFields
from dmt.tk.utils import collections
from neuro_dmt.utils.geometry import Interval


class AtlasHelper(WithFields):
    """
    Helps with `class Atlas`, and used to analyze circuits.
    """
    atlas = Field(
        """
        `Atlas` instance to help
        """)
    layers = Field(
        """
        Values of the layers in the brain region represented by this Atlas.
        The default value assumes that this Atlas represents a region in the
        cortex.
        """,
        __default_value__=[1, 2, 3, 4, 5, 6])
    acronym_separator = Field(
        """
        A char, or string that separates region label from that of the layers.
        """,
        __default_value__=';')
    dataset_orientation_position = Field(
        """
        Dataset associated with position along the orientation.
        """,
        __default_value__="[PH]y")
    dataset_orientation_layer_interval = Field(
        """
        For each voxel in the atlas, the positions along the voxel's
        orientation where the orientation (vector) intersects each layer's
        upper and lower boundaries are recorded as an interval. This `Field`
        should provide an dictionary mapping layer to the dataset containing
        intersections for that layer. The default value provided below assumes
        that this `Atlas` instance represents a region in the cortex.
        """,
        __default_value__={
            layer: "[PH]{}".format(layer) for layer in [1, 2, 3, 4, 5, 6]})
    dataset_brain_regions = Field(
        """
        Dataset containing with brain regions.
        """,
        __default_value__="brain_regions")
    voxel_size = Field(
        """
        Size off a voxel in the atlas.
        """)

    @lazyfield
    def hierarchy(self):
        """
        Brain regions in an `Atlas` are nested.
        Hierarchy of brain-regions.
        """
        return self.atlas.load_hierarchy()

    @lazyfield
    def orientation_position_voxel(self):
        """
        Position of a voxel, measured along it's `orientation_profile`.
        """
         bottoms_voxel = self\
             .atlas\
             .load_data(
                 self.dataset_orientation_position)\
             .raw
         return bottoms_voxel + self.voxel_size/2.

    @lazyfield
    def voxel_data(self):
        """
        A circuit atlas contains several datasets, each stored/loaded as
        `VoxelData`. Each of these `VoxelData` are equivalent, differing only
        in their content. `AtlasHelper.voxel_data` can be any of these
        `VoxelData` objects.
        """
        return self.atlas.load_data(self.dataset_brain_regions)

    @lazyfield
    def brain_region_voxel(self):
        """
        A 3D array that provides the brain region (ID) for given voxel.
        """
        return self.atlas.load_data(self.dataset_brain_regions)

    @lazyfield
    def orientation_profile_voxel(self):
        """
        Each voxel has an orientation profile.
        """
        return {
            layer: self.atlas.load_data(
                self.dataset_orientation_layer_interval)
            for layer in self.layers}

    def get_orientation_profile(self, voxel):
        """
        Get orientation profile for a voxel.

        Arguments
        ----------
        voxel :: Voxel indicies.
        """
        return {
            layer: Interval(
                top=layer_profile.raw[voxel[0], voxel[1], voxel[2], 1],
                bottom=layer_profile[voxel[0], voxel[1], voxel[2], 0])
            for layer, layer_profile in self.orientation_profile_voxel.items()}

    def get_atlas_region_acronyms(self,
            region,
            layers=None):
        """
        A list of acronyms to search in the atlas.

        Arguments
        --------
        """

        if not collections.check(layers):
            return [
                "{}{}{}".format(
                    region,
                    self.acronym_separator,
                    layers)]


        if layers is None or len(layers) == 0:
            return [region]

        return [
            "{}{}{}".format(
                region,
                self.acronym_separator,
                layer)
            for layer in layers]

    def get_atlas_ids(self,
            region,
            layers=None):
        """
        Get `Atlas` ids for region and layers.
        """
        return {
            id for acronym in self.get_atlas_region_acronyms(region, layers)
            for id in self.hierarchy.collect("acronym", acronym, "id")}

    def get_region_mask(self,
            region):
        """
        Voxeldata as a raw 3D array, non-nan only at voxels
        that fall in `region`.
        """
        return self.atlas.get_region_mask(region)

    def get_random_position(self,
            region=None,
            layers=None,
            depth=None):
        """
        Get a random position in the area specified by `(region, layer)` or
        `(region, depth)`.
        """
        if layers is not None and depth is not None:
            raise ValueError(
                "Random position can be evaluated either in a layer or
                at a depth. Not Both.")
        if depth is not None:
            raise NotImplementedError(
                "get_random_position(...) at given depth.")

        atlas_ids = self.get_atlas_ids(region, layers)
        if self.voxel_data.count(atlas_ids) == 0:
            return None

        count = 0
        while count < 10000000: #try 10 million times
            random_voxel = self\
                .voxel_data\
                .indices_to_position(
                    numpy.array([
                        numpy.random.randint(n)
                        for n in self.voxel_data.shape]))
            if self.brain_region_voxel.lookup(random_voxel) in atlas_ids:
                return random_voxel
            count += 1

        return None
