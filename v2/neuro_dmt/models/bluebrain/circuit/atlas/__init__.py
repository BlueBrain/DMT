"""
Code to document and deal with a circuit atlas.
"""

import os
import numpy
import pandas
from voxcell.nexus.voxelbrain import Atlas
from dmt.tk import collections
from dmt.tk.field import Field, lazyfield, WithFields
from neuro_dmt.terminology.atlas import translate
from .region_layer import RegionLayer
from .principal_axis import PrincipalAxis


class BlueBrainCircuitAtlas(WithFields):
    """
    Document all the artefacts that define a circuit atlas,
    and provide tools to load them and work with them.
    """

    path = Field(
        """
        Path to the directory that holds the circuit atlas data.
        This path may be a URL.
        """)

    @lazyfield
    def atlas(self):
        """
        `Atlas` instance to load the data.
        """
        return Atlas.open(self.path)

    @lazyfield
    def hierarchy(self):
        """
        Hierarchy of brain regions.
        """
        return self.atlas.load_hierarchy()

    @lazyfield
    def region_map(self):
        """
        Region map associated with the atlas.
        """
        return self.atlas.load_region_map()

    dataset_brain_regions = Field(
        """
        Dataset that provides brain regions in `self.atlas`.
        """,
        __default_value__="brain_regions")

    @lazyfield
    def brain_regions(self):
        """
        Volumetric data that provides brain regions in the atlas.
        """
        return self.atlas.load_data(self.dataset_brain_regions).raw

    @lazyfield
    def voxel_data(self):
        """
        A representative `VoxelData` object associated with `self.atlas`.
        """
        return self.atlas.load_data(self.dataset_brain_regions)

    layers = Field(
        """
        Values of the layers in the brain region represented by the atlas. We
        assume that this atlas is for the brain region, and so provide a
        mapping for each laminar region to the values of the layers used in
        this atlas. Default value are provided for cortical circuits that use
        an atlas specific to the cortex, or a region in the cortex such as the
        Somatosensory cortex (SSCx).
        """,
        __default_value__={
            "cortical": ["L1", "L2", "L3", "L4", "L5", "L6"]})

    @lazyfield
    def region_layer(self):
        """
        An object that expresses how region and layer are combined in the
        atlas, how their acronyms are represented in the hierarchy.
        """
        return RegionLayer(atlas=self.atlas)

    @lazyfield
    def principal_axis(self):
        """
        An object to handle queries concerning the voxel principal axis.
        """
        return PrincipalAxis(atlas=self.atlas)

    def get_mask(self,
            region=None,
            layer=None,
            depth=None,
            height=None):
        """
        Mask for combinations of given parameters.
        """
        region_layer_mask =\
            self.region_layer.get_mask(
                region=region,
                layer=layer)

        if depth is None and height is None:
            return region_layer_mask

        if depth is not None and height is not None:
            raise RuntimeError(
                "Cannot define a mask for both depth and height.")

        principal_axis_mask =\
            self.principal_axis.get_mask(
                depth=depth,
                height=height)

        return numpy\
            .logical_and(
                region_layer_mask,
                principal_axis_mask)

    def random_positions(self,
            **spatial_parameters):
        """
        Generate random positions (np.array([x,y,z])) in a region
        defined by the spatial parameters passed as arguments.
        """
        mask = self.get_mask(**spatial_parameters)
        if numpy.nansum(mask) == 0:
            raise RuntimeError(
                """
                No valid voxels that satisfy spatial parameters: {}
                """.format(
                    '\n'.join(
                        "{}: {}".format(parameter, value)
                        for parameter, value in spatial_parameters.items())))
        voxel_indices = list(zip(*numpy.where(mask)))
        while True:
            yield self.voxel_data.indices_to_positions(
                voxel_indices[numpy.random.randint(len(voxel_indices))])