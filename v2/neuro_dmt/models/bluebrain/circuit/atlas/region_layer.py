"""
Representation of layer regions in an atlas.
"""

from abc import ABC, abstractmethod, abstractclassmethod
from dmt.tk.field import ClassAttribute, Field, lazyfield, ABCWithFields
from dmt.tk import collections
from neuro_dmt.terminology.atlas import translate


class RegionLayerRepresentationImplementation(ABCWithFields):
    """
    Implements `RegionLayerRepresentation`.
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
    def is_applicable(cls, atlas):
        """
        Is this implementation applicable to given `Atlas` instance.
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
    def get_query_layer(self, layer):
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
        RegionLayerRepresentationImplementation):
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
        RegionLayerRepresentationImplementation):
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
        RegionLayerRepresentationImplementation):
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



class RegionLayerRepresentation:
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

    We will use a version of the bridge pattern:
    1. https://www.giacomodebidda.com/bridge-pattern-in-python/
    2. https://sourcemaking.com/design_patterns/bridge
    3. https://simpleprogrammer.com/design-patterns-simplified-the-bridge-pattern/
    """

    def __init__(self, implementation):
        """
        Initialize with the given concrete `implementation`.

        A concrete implementation will be used to provide functionality to this
        `interface`.
        """
        self._implementation = implementation

    @classmethod
    def for_atlas(cls, atlas):
        """
        An instance for the given `Atlas` instance.
        """
        for implementation_class in (
                FullLayerRepresentation,
                SemicolonIntRepresentation,
                BlueBrainAtlasRepresentation):
            if implementation_class.is_applicable(atlas):
                return cls(implementation_class(atlas))
        raise Exception(
            "No available implementation applies to atlas {}.".format(atlas))

    def get_region_acronym(self, region):
        """
        Acronym for a region.
        """
        return self._implementation.get_region_acronym(region)

    def get_layer_region_regex(self, region):
        """
        Get acronym for region.
        """
        return self._implementation.get_layer_region_regex(region)

