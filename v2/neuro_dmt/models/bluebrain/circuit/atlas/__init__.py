"""
Code to document and deal with a circuit atlas.
"""

import os
import numpy
import pandas
from voxcell.nexus.voxelbrain import Atlas
from dmt.tk import collections
from dmt.tk.field import Field, lazyfield, WithFields
from neuro_dmt.terminology.parameters import\
    MTYPE, SYNAPSE_CLASS,\
    BRAIN_REGION, MESOCOLUMN, LAYER,\
    DEPTH, HEIGHT
from neuro_dmt.terminology.atlas import translate
from .region_layer import RegionLayerRepresentation


class CircuitAtlas(WithFields):
    """
    Document all the artefacts that define a circuit atlas,
    and provide tools to load them and work with them.
    """

    path_atlas = Field(
        """
        Path to the directory that holds the circuit atlas data.
        This path may be a URL.
        """)

    @lazyfield
    def atlas(self):
        """
        `Atlas` instance to load the data.
        """
        return Atlas.open(self.path_atlas)

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

    def __getattr__(self, attr):
        """
        If a method is not defined in `class CircuitAtlas`, 
        call it on `self.atlas`.
        """
        try:
            return getattr(self.atlas, attr)
        except AttributeError as error:
            raise AttributeError(
                """
                Attribute {{} defined neither for {} nor the associated {}
                instance.
                """.format(
                    self.__class__.__name__,
                    self.atlas.__class__.__name__))

    @lazyfield
    def region_layer_representation(self):
        """
        An object that expresses how region and layer are combined in the
        atlas, how their acronyms are represented in the hierarchy.
        """
        return RegionLayerRepresentation.for_atlas(atlas)

    def get_acronyms(self, regions, layers=None):
        """
        Get acronyms used by the atlas for combinations of regions and layers.
        """
        return self.region_layer_representation.get_acronyms(regions, layers)


    def get_ids(self,
            regions=None,
            layers=None,
            with_descendents=True,
            ignore_case=False):
        """
        Get atlas ids used by the atlas for combinations of regions and layers.
        """
        if regions is None and layers is None:
            raise ValueError(
                "Neither regions, nor layers passed.")
        return {_id
                for acronym in self.get_acronyms(
                        regions,
                        layers)
                for _id in self.region_map(
                        acronym,
                        attr="acronym",
                        with_descendants=with_descendents,
                        ignore_case=ignore_case)}

    def get_mask(self,
            region=None,
            layer=None,
            hypercolumn=None,
            depth=None,
            height=None):
        """
        Mask for combinations of regions and layers.
        """
        if region is None and layer is None:
            return self.atlas.load_data("brain_regions") > 0

        if region is not None:
            region_mask = numpy.any(
                [self.atlas.get_region_mask(
                    self.region_layer_representation.get_region_acronym(r),
                    attr="acronym").raw
                 for r in collections.get_list(region)],
                axis=0)

        if layer is None:
            return region_mask

        layer_mask = numpy.any(
            [self.atlas.get_region_mask(
                self.region_layer_representation.get_layer_region_regex(l),
                attr="acronym").raw
             for l in collections.get_list(layer)],
            axis=0)

        return numpy.logical_and(region_mask, layer_mask)
