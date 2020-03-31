# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Representation of layer regions in an atlas.
"""
from abc import\
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


class RegionAcronymGenerator:
    """
    Provide a uniform interface to (brain-)region acronyms in an atlas.
    Two atlases may differ in how they call the same region acronyms.
    """
    def __init__(self,
            *args, **kwargs):
        """
        By excepting any arguments in this base-class initializer,
        it's subclasses may implement any behavior.
        """
        pass

    @classmethod
    def for_atlas(cls, atlas):
        """
        `RegionAcronymGenerator` concrete implementation applicable to an
        `Atlas` instance.
        """
        for concrete_type in (
                PaxinosBrainAtlasRegions,
                O1ColumnarAtlasRegions):
           if concrete_type.is_applicable(atlas):
               return concrete_type(atlas)
        return RegionAcronymGenerator()

    @classmethod
    def is_applicable(cls, atlas):
        """
        Check if the concrete implementation `cls` is applicable to a `Atlas`
        instance.
        Default behavior for a `RegionAcronymGenerator` is implemented in
        this base-class, which an appropriate subclass should override.
        """
        return True

    def get(self, region):
        """
        Default behavior for a `RegionAcronymGenerator` is implemented in
        this base-class, which an appropriate subclass should override.
        """
        return region

    def get_region_acronym(self, region):
        """
        Same as get, but allows `RegionAcronymGenerator` to be mixed in.
        """
        return self.get(region)


class PaxinosBrainAtlasRegions(
        RegionAcronymGenerator):
    """
    Brain region acronyms according to Paxinos-Watson atlas.
    """
    @classmethod
    def is_applicable(cls, atlas):
        """..."""
        return any(
            atlas.load_region_map().find(pattern, attr="acronym")
            for pattern in ("SSCtx", "S1HL"))

    @classmethod
    def get(cls, region):
        """
        Translate from ABI.
        """
        return translate.ABI_to_Paxinos(region)


class O1ColumnarAtlasRegions(
        RegionAcronymGenerator):
    """
    Brain region acronyms in an O1 atlas.
    """
    def __init__(self, atlas):
        """
        Initialize me
        """
        self._region_map = atlas.load_region_map()

    @classmethod
    def is_applicable(cls, atlas):
        """..."""
        rmap = atlas.load_region_map()
        return rmap.find("O1", "acronym") or rmap.find("O1 mosaic", "name")

    def get(self, region):
        """..."""
        for acronym in (region, "{}_Column".format(region)):
            if self._region_map.find(acronym, "acronym"):
                return acronym
        return None


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
    layer_acronym_regex_pattern_template = ClassAttribute(
        """
        Regex expression template that can used to generate a regex expression
        for layer region acronyms needed to get a region mask from the atlas.
        """)
    region_acronym = Field(
        """
        A `RegionAcronymGenerator` that can return acronyms for a region as
        the atlas understands.
        """)

    @classmethod
    def with_region_acronym_type(cls, region_acronym_type):
        """
        Get a new type that mixes in a `RegionAcronymGenerator` type.

        Arguments
        `region_acronym_type`: `RegionAcronymGenerator` or subclass.
        """
        return type(
            "{}With{}".format(cls.__name__, region_acronym_type.__name__),
            (cls, region_acronym_type),
            {})

    @staticmethod
    def for_atlas(atlas):
        """
        Return an instance of the concrete subclass that applies to the given
        atlas.
        """
        for concrete_type in (
                FullLayerRepresentation,
                SemicolonIntRepresentation,
                BlueBrainAtlasRepresentation):
            if concrete_type.is_applicable(atlas):
                return concrete_type(
                    region_acronym=RegionAcronymGenerator.for_atlas(atlas))
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
        return self.region_acronym.get(region)

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
        return cls.layer_acronym_regex_pattern_template\
                   .format(cls.get_query_layer(layer))


class FullLayerRepresentation(
        RegionLayerRepresentation):
    """
    Layer region acronyms contain the full layer string, e.g. L2 or mc2;L2.
    """
    applicable_patterns = ("@^L1$|.*;L1$", "@^SP$|.*;SP$")

    layer_acronym_regex_pattern_template = "@{}$"

    @classmethod
    def get_query_layer(cls, layer):
        """..."""
        try:
            layer = int(layer)
        except ValueError:
            pass
        if isinstance(layer, int) and layer > 0 and layer < 7:
            return "L{}".format(layer)

        if isinstance(layer, str):
            if not layer[0] == "L":
                raise ValueError(
                    """
                    Query `layer` should start with an L for a circuit atlas
                    that uses patterns {} to represent their layers.
                    `layer` value passed: {}
                    """.format(cls.applicable_patterns,
                               layer))
        return layer


class SemicolonIntRepresentation(
        RegionLayerRepresentation):
    """
    Layer region acronyms separated region from layer by a semicolon,
    <region>;<layer>
    """
    applicable_patterns = ("@.*;6$", "@.*;SP$")

    layer_acronym_regex_pattern_template = "@;{}$"

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

    layer_acronym_regex_pattern_template = "@.*{}[ab]?$"

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
        The associated base atlas.
        """)

    @lazyfield
    def region_map(self):
        """
        Map regions
        """
        return self.atlas.load_region_map()

    @lazyfield
    def representation(self):
        """
        `RegionLayerRepresentation` instance applicable to the atlas.
        """
        return RegionLayerRepresentation.for_atlas(self.atlas)

    def get_ids(self,
            region, layer):
        """
        Get atlas IDs for a layer-region represented by the combination
        (region, layer), i.e. layer in region.

        Arguments
        ----------
        region: Brain region to search for 
        layer: Layer to search for (cortical layers should be L1, L2, ...)
        """
        region_ids = self\
            .region_map.find(
                self.representation.get_region_acronym(region),
                attr="acronym",
                with_descendants=True)
        layer_ids = self\
            .region_map.find(
                self.representation.get_layer_region_regex(layer),
                attr="acronym",
                with_descendants=True)
        return region_ids.intersection(layer_ids)

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
            [self.atlas.get_region_mask(
                atlas_layer,
                attr="acronym").raw
             for atlas_layer in atlas_layers],
            axis=0)

        if region is None:
            return layer_mask

        return numpy.logical_and(region_mask, layer_mask)
