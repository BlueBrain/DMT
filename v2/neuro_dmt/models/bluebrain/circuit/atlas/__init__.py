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
        return RegionLayerRepresentation(atlas)

    def get_acronyms(self, regions, layers=None):
        """
        Get acronyms used by the atlas for combinations of regions and layers.
        """
        return self.region_layer_representation.get_acronyms(regions, layers)


    def get_ids(self,
            regions, layers=None,
            with_descendents=True,
            ignore_case=False):
        """
        Get atlas ids used by the atlas for combinations of regions and layers.
        """
        return {_id
                for acronym in self.get_acronyms(
                        regions,
                        layers)
                for _id in self.region_map(
                        acronym,
                        attr="acronym",
                        with_descendants=with_descendents,
                        ignore_case=ignore_case)}

    def get_mask(self, regions, layers=None):
        """
        Mask for combinations of regions and layers.
        """
        masks = [
            self.atlas.get_region_mask(acronym, attr="acronym")
            for acronym in self.get_acronyms(self, regions, layers)]
        return numpy.any(masks, axis=0)
