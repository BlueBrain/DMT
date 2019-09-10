"""
Representation of layer regions in an atlas.
"""

from abc import ABC, abstractmethod, abstractclassmethod
from dmt.tk.field import Field, lazyfield, WithFields
from dmt.tk import collections


def leaves(tree):
    """
    Generate leaves in a hierarchy tree.
    """
    for child in tree.children:
        if len(child.children) == 0:
            yield child
        else:
            for grand_child in leaves(child):
                yield grand_child
    

class RegionLayerRepresentationImplementation(ABC):
    """
    An interface that describes the methods and fields that an
    implementation to be used by  `class RegionLayerRepresentation`
    must provide.
    """
    def __init__(self, *args, **kwargs):
        """Cannot be initialized."""
        raise TypeError(
            "RegionLayerRepersentationImplementations cannot be instantiated")

    @classmethod
    def is_applicable(cls, atlas):
        """
        Test if this subclass is applicable.
        This will be at the base of all mixins, so always applicable.
        """
        return True

    @abstractmethod
    def get_acronym(self, region, layer):
        """
        A pattern that can be filled in with a region and layer to obtain
        an acronym in an atlas hierarchy.
        """
        raise NotImplementedError

    @staticmethod
    def get_query_layers(layers):
        """
        One atlas' representation of layers might be different from another.
        This method should convert a value of layer to that used by that used
        by the atlas to which this `RegionLayerRepersentationType` applies.

        A default method is provided, that should be overridden to provide
        specific behavior.
        """
        return layers

    @staticmethod
    def get_query_regions(regions):
        """
        Region names and acronyms may differ between atlases. To use a single
        terminology in our work, we need a translator.
        We provide default behavior here.
        A sub-class may override this method to implement
        any peculiar behavior of a specific atlas.
        """
        return regions


    @classmethod
    def is_layer_region(cls, hierarchy_node):
        """
        Check if a hierarchy node reprensents a layer region.
        A default implementation is provided.
        A subclass may override to implement a specific behavior.
        """
        region_name = hierarchy_node.data["name"]
        return "layer" in region_name or "Layer" in region_name

    @classmethod
    def get_layer_regions(cls, hierarchy):
        """
        Layer region acronyms.
        """
        for leaf in leaves(hierarchy):
            if cls.is_layer_region(leaf):
                yield leaf.data["acronym"]


class WithJustLayerNumber:
    """
    Mixin for atlas cortical layer region representations that do not
    prefix the layer by 'L'.
    """
    layer_values = ["1", "2", "3", "4", "5", "6"]

    @classmethod
    def get_query_layers(cls, layers):
        """..."""
        def _get_one(layer):
            try:
                return layer[1] if layer[0] == 'L' else layer
            except TypeError:
                return str(layer)
        return [_get_one(layer) for layer in layers]


class WithPrefixedLayerNumber:
    """
    Mixin for atlas cortical layer region representations that prefix the
    layer by 'L'.
    """
    layer_values = ["L1", "L2", "L3", "L4", "L5", "L6"]

    @classmethod
    def get_query_layers(cls, layers):
        """..."""
        def _get_one(layer):
            try:
                if layer[0] == 'L':
                    return layer
            except TypeError:
                pass
            return "L{}".format(layer)
        return [_get_one(layer) for layer in layers]


class HasSemicolonSeparatedRegionLayer:
    """
    Mixin for `RegionLayerRepresentationImplementation`s that
    separate region from layer by a semicolon.
    """
    @abstractclassmethod
    def get_layer_regions(cls, layers):
        """..."""
        raise NotImplementedError

    @classmethod
    def is_layer_region(cls, hierarchy_node):
        """..."""
        return super().is_layer_region(hierarchy_node)\
            and ';' in hierarchy_node.data["acronym"]

    @classmethod
    def is_applicable(cls, atlas):
        """..."""
        for region_layer in cls.get_layer_regions(atlas.load_hierarchy()):
            return ";" in region_layer
        return False

    @classmethod
    def get_acronym(cls, region, layer):
        """..."""
        atlas_layer = cls.get_query_layers([layer])[0]
        return "{};{}".format(region, atlas_layer)


class HasUnseparatedRegionLayer:
    """
    Mixin for `RegionLayerRepresentationImplementation`s that
    does not separate region from layer.
    """
    @abstractclassmethod
    def get_layer_regions(cls, layers):
        """..."""
        raise NotImplementedError

    @classmethod
    def is_layer_region(cls, hierarchy_node):
        """..."""
        if not  super().is_layer_region(hierarchy_node):
            return False

        try:
            region_layer = hierarchy_node.data["acronym"]
            return region_layer[-1] in cls.layer_values\
                or region_layer[-2:] in cls.layer_values
        except IndexError:
            return False

        return False

    @classmethod
    def is_applicable(cls, atlas):
        """..."""
        for _ in cls.get_layer_regions(atlas.load_hierarchy()):
            return True
        return False

    @classmethod
    def get_acronym(cls, region, layer):
        """..."""
        atlas_layer = cls.get_query_layers([layer])[0]
        return "{}{}".format(region, atlas_layer)



class HasLayerRegionWithoutRegion:
    """
    Some atlases may represent layers in each region with acronyms
    that do not contain containing region's acronym.
    """
    @abstractclassmethod
    def get_layer_regions(cls, hierarchy_node):
        """..."""
        raise NotImplementedError

    @classmethod
    def is_applicable(cls, atlas):
        """..."""
        if not super().is_applicable(atlas):
            return False
        for region_layer in cls.get_layer_regions(atlas.load_hierarchy()):
            return region_layer.data["acronym"] in cls.layer_values
        return False

    @classmethod
    def get_acronym(cls, region, layer):
        """..."""
        return layer
        

class ForO1Atlas:
    """
    Mixin for O1 atlases.
    """
    def is_applicable(cls, atlas):
        """..."""
        if not super().is_applicable(atlas):
            return False
        root = atlas.load_hierarchy().data
        return  root["acronym"] == "O1" or root["name"] == "O1 mosaic"


class O1AtlasJustPrefixedLayerRepresentation(
        HasLayerRegionWithoutRegion,
        WithPrefixedLayerNumber,
        ForO1Atlas,
        RegionLayerRepresentationImplementation):
    """
    The O1 atlas at /gpfs/project/proj66/entities/dev/atlas/O1-152
    uses acronyms L1, L2, ... for cortical layers, without prefixing
    the containing region acronym.
    """
    pass


class O1AtlasSemicolonSeparatedRepresentation(
        HasSemicolonSeparatedRegionLayer,
        WithJustLayerNumber,
        ForO1Atlas,
        RegionLayerRepresentationImplementation):
    """
    O1 atlas that separates layer from region by a semi-colon.

    Example atlas: .../proj64/dissemination/data/atlas/O1/MEAN/mean
    """
    pass


class IsoCortexAtlas2018Representation(
        HasUnseparatedRegionLayer,
        WithJustLayerNumber,
        RegionLayerRepresentationImplementation):
    """
    Representation of layer regions as used for the (mouse) isocortex release 
    of April 2018.
    """
    atlas_layer = {
        "L1": "1",
        "L2": "2",
        "L3": "3",
        "L4": "4",
        "L5": "5",
        "L6": ("6a", "6b")}

    layer_values = [
        "1", "2", "3", "4", "5", "6a", "6b"]

    @classmethod
    def is_applicable(cls, atlas):
        """..."""
        pattern_full_layer_cortical = "@^L1$|.*;L1$"
        pattern_full_layer_hippocampal = "@^SP$|.*;SP$"
        region_map = atlas.load_region_map()
        return region_map.find(pattern_full_layer_cortical, "acronym")\
            or region_map.find(pattern_full_layer_hippocampal, "acronym")

    @classmethod
    def is_layer_region(cls, hierarchy_node):
        """..."""
        if not super().is_layer_region(hierarchy_node):
            return False
        try:
            acronym = hierarchy_node.data["acronym"]
            return acronym[-1] in cls.atlas_layer_values\
                or acronym[-2:] in cls.atlas_layer_values
        except IndexError:
            return False
        return False

    @classmethod
    def get_acronym(cls, region, layer):
        """..."""
        return "{}{}".format(region, layer)

    @classmethod
    def get_query_layers(cls, layers):
        """..."""
        def _prefixed_L(layer):
            try:
                if layer[0] == 'L':
                    return layer
            except TypeError:
                pass
            return "L{}".format(layer)

        return [
            atlas_layer
            for atlas_layer in cls.atlas_layer[_prefixed_L(layer)]
            for layer in layers]


class RegionLayerRepresentation(WithFields):
    """
    Express how the circuit atlas represents laminary regions of a brain area
    such as the cortex.
    Brain regions in a brain atlas are organized in a hierarchy.
    While brain regions such as the SSp and SSp-ll fit well in a
    tree-based hierarchy, layers have to be stuck inside this tree hierarchy
    by creating leaf nodes in the hierarchy under the final brain region.
    These leaf nodes in a laminar part of the circuit are the layers.
    The problematic issue is the acronym given to these layer-regions.
    The name of the brain region node just above the layer-region is appended
    by the value of the layer, separated by a character. This class handles
    this complexity.
    Different versions of the atlas, or atlases for different parts of the
    brain follow different conventions. To handle this diversity we use a 
    version of the 'bridge' pattern:
    1. https://www.giacomodebidda.com/bridge-pattern-in-python/
    2. https://sourcemaking.com/design_patterns/bridge
    3. https://simpleprogrammer.com/design-patterns-simplified-the-bridge-pattern/
    """
    def __init__(self, implementation):
        """
        Initialize for the given `Atlas` instance.

        A concrete implementation that will be used to provide functionality
        to this 'interface'. Read the methods in the following class body to
        decide what messages this implementation must respond to.
        """
        self._implementation = implementation

    @classmethod
    def for_atlas(cls,
            atlas,
            available_implementations=[]):
        """
        An instance for the given `Atlas` instance.
        """
        for implementation in available_implementations:
            if implementation.applies(atlas):
                return cls(implementation)
        raise Exception(
            "No available implementation applies to atlas {}.".format(atlas))

    def get_acronyms(self, regions, layers=None):
        """
        Get acronyms used by the atlas corresponding to a combination of
        regions and layers.
        """
        atlas_regions = self\
            ._implementation\
            .get_query_regions(
                collections.get_list(regions))
        if layers is None:
            return atlas_regions

        atlas_layers = self\
            ._implementation\
            .get_query_layers(
                collections.get_list(layers))
        return [
            self._implementation.get_acronym(region, layer)
            for region in atlas_regions
            for layer in atlas_layers]
