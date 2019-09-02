"""
A class to help with the voxelbrain atlas.
"""

import numpy
import pandas
from voxcell.nexus.voxelbrain import Atlas, LocalAtlas, VoxelBrainAtlas
from dmt.tk.field import Field, lazyfield, WithFields
from dmt.tk import collections
from neuro_dmt.utils.geometry import Interval

class CircuitAtlas(WithFields):
    """
    Helps with `voxcell.nexus.voxelbrain.Atlas` used to analyze circuits.
    """
    uri_atlas = Field(
        """
        If this atlas is stored on Nexus...
        A default value of an empty string will indicate that the atlas
        data to be loaded as the atlas is available locally on the disk.
        """,
        __default_value__="")
    path_atlas = Field(
        """
        Path to the local disc directory holding `Atlas` datasets.
        If the `Atlas` datasets are on a service such as `Nexus`, then provide
        the local disc directory where atlas data will be cached.
        """)
    layers = Field(
        """
        Values of the layers in the brain region represented by the atlas.
        Atlas regions are organized as a hierarchical tree. For laminar 
        regions, layers are defined as leaf regions. In the atlas' hierarchy
        region nodes are split into children node. The leaf nodes represent
        layers. Several brain areas are laminar, and we require this Field to
        be a dict mapping brain area to its layer values used in the atlas.
        """,
        __default_value__={
            "cortical": [1, 2, 3, 4, 5, 6]})
    region_layer_separator = Field(
        """
        A string that separates region label from that of the layers (or an
        equivalent structure defined for the brain area represented in the
        atlas).
        """,
        __default_value__=';')
    size_voxel = Field(
        __type__=(float, numpy.float),
        """
        Size of a voxel in the atlas.
        """)
    dataset_brain_regions = Field(
        """
        Name of the dataset that contains brain region IDs.
        """,
        __default_value__="brain_regions")
    dataset_principal_axis_position = Field(
        """
        Name of the dataset associated with position along the principal axis.
        """,
        __default_value__="[PH]y")
    dataset_principal_axis_profile = Field(
        """
        Name(s) of dataset(s) that provide a profile of intersections along the 
        principal axis of a voxcel.
        """,
        __default_value__=lambda l:  "PH{}".format(l))


    def __getattr__(self, attr):
        """
        If a method is not defined here, try calling it on `self.atlas`
        """
        try:
            return getattr(self.atlas, attr)
        except AttributeError:
            raise AttributeError(
                """
                Attribute {} defined neither for {} nor the associated
                {} instance.
                """.format(
                    self.__class__.__name__,
                    self.atlas.__class__.__name__))

    @lazyfield
    def atlas(self):
        """
        The `Atlas` instance that this helper instance will work with.
        We assume that 
        """
        return VoxelBrainAtlas(self.uri, self.path_atlas)\
            if self.uri_atlas else LocalAtlas(self.path_atlas)

    @lazyfield
    def hierarchy(self):
        """
        Region hierarchy associated with the atlas.
        """
        return self.atlas.load_hierarchy()


    @lazyfield
    def principal_axis_position(self):
        """
        Position along the principal axis, as a 3D matrix.
        """
        bottoms_voxels = self.atlas\
            .load_data(self.dataset_principal_axis_position)\
            .raw
        return bottoms_voxels + self.size_voxel / 2.

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
    def brain_region(self):
        """
        3D matrix that provides the brain region ID for a given voxel.
        """
        return self.atlas.load_data(self.dataset_brain_regions)

    @lazyfield
    def principal_axis_profile(self):
        """
        Profiles along the principle axis.
        """
        return {
            layer: self.atlas.load_data(
                self.dataset_principal_axis_profile(layer))
            for layer in self.layers}

    def get_principle_axis_intersections(self, voxel):
        """
        Positions at which a voxel's principle axis intersects layers, or
        other such structures.
        """
        return {
            layer: Interval(
                top=layer_profile.raw[voxel[0], voxel[1], voxel[2], 1],
                bottom=layer_profile.raw[voxel[0], voxel[1], voxel[2], 0])
            for layer, layer_profile in self.principal_axis_position}

    def get_region_acronyms(self,
            region_or_regions,
            leaf_or_leaves=None):
        """
        A list of acronyms to search in the atlas.
        """
        regions = region_or_regions\
            if not collections.check(region_or_regions)\
               else [region_or_regions]
        if not leaf_or_leaves or len(leaf_or_leaves) == 0:
            return regions
        leaf_or_leaves = leaf_or_leaves\
            if not collections.check(leaf_or_leaves)\
               else [leaf_or_leaves]
        return [
            "{}{}{}".format(region, self.region_layer_separator, layer)
            for region in regions
            for layer in layers]

    def get_ids(self,
            regions,
            layers=None):
        """
        Atlas IDs
        """
        return {
            id for acronym in self.get_region_acronyms(regions, layers)
            for id in self.hierarchy.collect("acronym", acronym, "id")}


    def get_random_position(self,
            region=None,
            layers=None,
            height=None,
            depth=None):
        """
        Get a random position in the volume specified by the keyword arguments.
        """
        if layers is not None and depth is not None and height is not None:
            raise ValueError(
                """
                Random position can be evaluated either in a layer, or at a height,
                or at a depth. Please pass only one of these arguments.
                """)
        if depth is not None:
            raise NotImplementedError(
                "get_random_position(...) at a given depth.")
        if height is not None:
            raise NotImplementedError(
                "get_random_position(...) at a given height.")

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
