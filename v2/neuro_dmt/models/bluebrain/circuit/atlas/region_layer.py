"""
Representation of layer regions in an atlas.
"""

from abc import\
    ABC,\
    abstractmethod,\
    abstractclassmethod
import numpy
from dmt.tk.field import\
    ClassAttribute,\
    Field,\
    lazyfield,\
    WithFields,\
    ABCWithFields
from dmt.tk import collections
from neuro_dmt.terminology.atlas import translate


class RegionLayerRepresentation(
        ABCWithFields):
    """
    Express how the circuit atlas represents laminar regions of a brain area
    such as the cortex.

    A brain atlas organizes brain regions in a hierarchy. Regions such as
    the primary somatosensory, and the primary somatosensory area lower limb
    fit naturally in this hierarchy based on 'is-contained-in' relationships.
    Layers, however, form a structure that is orthogonal to the regions in this
    hierarchy. Layers span all the regions in the cortex. To fit them in the
    atlas's hierarchy, each final cortical region is divided into cortical
    layers, each of which form a leaf region. Thus each cortical layer is
    chunked up and annotated by the (sub-)region containing it. The volumetric 
    data associated with the atlas uses only the ids associated with the leaf
    regions of the atlas hierarchy. Sticking chunked up layer regions into the
    hierarchy as leaf nodes allows the brain circuit atlas to use only a single
    volumetric data set. While there are only a few brain region naming
    conventions, there are no standards about how to name the layer regions. We
    track the complexity arising out of this missing naming convention.
    """
    applicable_patterns = ClassAttribute(
        """
        Regex patterns that can be used to resolve how the atlas represents
        layer regions.
        """)

    layer_acronym_pattern_template = ClassAttribute(
        """
        Regex expression template that can used to generate a regex expression
        for layer region acronyms needed to get a region mask from the atlas.
        """)

    def __init__(self, atlas):
        """
        Initialize for an atlas.
        """
        self._use_paxinos_regions = any(
            atlas.load_region_map().find(pattern, attr="acronym")
            for pattern in ("SSCtx", "S1HL"))

    @classmethod
    def for_atlas(cls, atlas):
        """
        Return an instance of the concrete subclass that applies to the given
        atlas.
        """
        for concrete_class in (
                FullLayerRepresentation,
                SemicolonIntRepresentation,
                BlueBrainAtlasRepresentation):
            if concrete_class.is_applicable(atlas):
                return concrete_class(atlas)
        raise Exception(
            "No available implementaiton applied to atlas {}"\
            .format(atlas.dirpath))


    @classmethod
    def is_applicable(cls, atlas):
        """
        Is this concrete implementation applicable to given `Atlas` instance.
        """
        return any(
            atlas.load_region_map().find(pattern, attr="acronym")
            for pattern in cls.applicable_patterns)

    def get_region_acronym(self, region):
        """
        Get acronym for region.
        """
        return translate.ABI_to_Paxinos(region)\
            if self._use_paxinos_regions else\
               region

    @abstractclassmethod
    def get_query_layer(cls, layer):
        """
        Get layer as the atlas represents it.
        """
        pass

    @classmethod
    def get_layer_region_regex(cls, layer):
        """
        Get regex that can be used to retrieve all layer-regions for a given
        layer.
        """
        return cls.layer_acronym_pattern_template\
                   .format(cls.get_query_layer(layer))
                       

class FullLayerRepresentation(
        RegionLayerRepresentation):
    """
    Layer region acronyms contain the full layer string, e.g. L2 or mc2;L2.
    """
    applicable_patterns = ("@^L1$|.*;L1$", "@^SP$|.*;SP$")

    layer_acronym_pattern_template = "@{}$"

    @classmethod
    def get_query_layer(cls, layer):
        """..."""
        return layer


class SemicolonIntRepresentation(
        RegionLayerRepresentation):
    """
    Layer region acronyms separated region from layer by a semicolon,
    <region>;<layer>
    """
    applicable_patterns = ("@.*;6$", "@.*;SP$")

    layer_acronym_pattern_template = "@;{}$"

    @classmethod
    def get_query_layer(self, layer):
        """..."""
        return layer[1]


class BlueBrainAtlasRepresentation(
        RegionLayerRepresentation):
    """
    Convention used, or to be used by the BlueBrain Atlas.
    """
    applicable_patterns = ("@.*6a$", "@.*SP$")

    layer_acronym_pattern_template = "@.*{}$"

    @classmethod
    def get_query_layer(cls, layer):
        """
        Convert argument `layer` to a form accepted by the atlases that this
        `BlueBrainAtlasRepresentation` applies to.
        """
        return layer[1:]\
            if layer.startswith('L') and layer[1] in "123456"\
               else layer.lower()



class RegionLayer(WithFields):
    """
    Handles region, layer queries for the circuit atlas.
    """
    atlas = Field(
        """
        The associated atlas.
        """)

    @lazyfield
    def region_map(self):
        """
        Map regions
        """
        return atlas.load_region_map()

    @lazyfield
    def representation(self):
        """
        `RegionLayerRepresentation` instance applicable to the atlas.
        """
        return RegionLayerRepresentation.for_atlas(self.atlas)

    def get_acronyms(self,
            regions=None,
            layers=None):
        """
        Get acronyms for combinations of regions and layers.
        """
        raise NotImplementedError

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
            layer=None):
        """
        Mask for combinations of regions and layers.
        """
        if region is None and layer is None:
            return self.atlas.load_data("brain_regions").raw > 0

        if region is not None:
            region_mask = numpy.any(
                [self.atlas.get_region_mask(
                    self.representation.get_region_acronym(r),
                    attr="acronym").raw
                 for r in collections.get_list(region)],
                axis=0)

        if layer is None:
            return region_mask

        atlas_layers = [
            self.representation.get_layer_region_regex(l)
            for l in collections.get_list(layer)] 
        layer_mask = numpy.any(
            [self.atlas.get_region_mask(atlas_layer, attr="acronym").raw
             for atlas_layer in atlas_layers],
            axis=0)

        if region is None:
            return layer_mask

        return numpy.logical_and(region_mask, layer_mask)
