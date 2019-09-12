"""
Test develop the behavior of CircuitAtlas
"""

import os
import numpy as np
import numpy.testing as npt
from voxcell.nexus.voxelbrain import Atlas
from dmt.tk.field import WithFields, Field, lazyfield
from dmt.tk import collections
from . import CircuitAtlas
from .region_layer import *

def project(number):
    return "/gpfs/bbp.cscs.ch/project/proj{}".format(number)

path_atlas = {
    "O1MouseSSCx": os.path.join(
        project(66),
        "entities/dev/atlas/O1-152"),
    "O1RatSSCxDiss": os.path.join(
        project(64),
        "dissemination/data/atlas/O1/MEAN/mean"),
    "S1RatSSCx": os.path.join(
        project(64),
        "entities/dev/atlas/",
        "fixed_77831ACA-6198-4AA0-82EF-D0475A4E0647_01-06-2018"),
    "O1MouseHip": os.path.join(
        project(42),
        "entities/dev/atlas/",
        "20190625-CA3-O1-atlas/"),
    "S1MouseNeoCx": os.path.join(
        project(68),
        "entities/",
        "dev/atlas/ccf_2017-50um/20181114"),
    "S1RatSSCxDiss": os.path.join(
        project(64),
        "dissemination",
        "data/atlas/S1/MEAN/juvenile_L23_MC_BTC_shifted_down",
        "Bio_M")}

def test_atlas_paths():
    """
    Paths in `path_atlas` must exist.
    """
    for name_atlas, path in path_atlas.items():
        assert Atlas.open(path),\
            "Could not open atlas {} at {}.".format(name_atlas, path)

def _expect_equal(x, y, message=""):
    try:
        message += " {} != {}".format(x, y)
        assert x == y, message
        return True
    except ValueError:
        if not message:
            message = """
            Array Left with sum {}
            != Array Right with sum {}
            """.format(
                np.nansum(x),
                np.nansum(y))
        npt.assert_array_equal(x, y, message)
        return True

    assert False, "Code execution should not reach here."

def test_representation_applicability():
    """
    One of the `RegionLayerRepresentation`s should apply.
    """
    atlas_name = "S1RatSSCxDiss"
    path = path_atlas[atlas_name]
    atlas = Atlas.open(path)
    assert FullLayerRepresentation.is_applicable(atlas)
    assert not SemicolonIntRepresentation.is_applicable(atlas)
    assert not BlueBrainAtlasRepresentation.is_applicable(atlas)
    representation = RegionLayerRepresentation.for_atlas(atlas)
    assert FullLayerRepresentation(atlas)._use_paxinos_regions

    _expect_equal(
        representation.get_region_acronym("SSp"),
        "S1",
        "atlas: ".format(atlas_name))
    _expect_equal(
        representation.get_layer_region_regex("L1"),
        "@L1$",
        "atlas: {}".format(atlas_name))

    atlas_name = "S1MouseNeoCx"
    path = path_atlas[atlas_name]
    atlas = Atlas.open(path)
    assert not FullLayerRepresentation.is_applicable(atlas)
    assert not SemicolonIntRepresentation.is_applicable(atlas)
    assert BlueBrainAtlasRepresentation.is_applicable(atlas)
    representation = RegionLayerRepresentation.for_atlas(atlas)
    assert not BlueBrainAtlasRepresentation(atlas)._use_paxinos_regions

    _expect_equal(
        representation.get_region_acronym("SSp"),
        "SSp",
        "atlas: {}".format(atlas_name))
    _expect_equal(
        representation.get_layer_region_regex("L2"),
        "@.*2$",
        "atlas: {}".format(atlas_name))


class CircuitAtlasTest(WithFields):
    """
    Test `CircuitAtlas`.
    """
    label = Field(
        """
        Provide a label to be used when complaining about test failures.
        """)
    path_atlas = Field(
        """
        Path to the atlas to be tested.
        """)
    regions_to_test = Field(
        """
        A list of acronyms to test with.
        """)
    layers_to_test = Field(
        """
        A list of lists to test with.
        """)

    @lazyfield
    def circuit_atlas(self):
        """
        `CircuitAtlas` instance to be tested.
        """
        return CircuitAtlas(path=self.path_atlas)

    @lazyfield
    def atlas(self):
        """
        `Atlas` instance to test against.
        """
        return Atlas.open(self.path_atlas)

    @lazyfield
    def atlas_layers(self):
        """
        Layers as the underlying atlas understands them.
        """
        def __get_one(layer):
            return self\
                .circuit_atlas\
                .region_layer_representation\
                .get_layer_region_regex(layer)
        return [
            __get_one(layer)
            for layer in collections.get_list(self.layers_to_test)]

    @lazyfield
    def atlas_regions(self):
        """
        Regions as the underlying atlas understands them.
        """
        def __get_one(region):
            return self\
                .circuit_atlas\
                .region_layer_representation\
                .get_region_acronym(region)

        return [
            __get_one(region)
            for region in collections.get_list(self.regions_to_test)]

    def region_mask(self):
        """
        Test that masks for regions are good.
        """
        for region in self.regions_to_test:
            atlas_region = self\
                .circuit_atlas\
                .region_layer_representation\
                .get_region_acronym(region)
            _expect_equal(
                self.circuit_atlas.get_mask(region=region),
                self.atlas.get_region_mask(atlas_region).raw)

    def layer_mask(self):
        """
        Test that masks for layers are good.
        """
        layer = collections.get_list(self.layers_to_test)[0]
        circuit_atlas_mask = self\
            .circuit_atlas\
            .get_mask(layer=layer)
        assert len(circuit_atlas_mask.shape) == 3
        assert np.nansum(circuit_atlas_mask) > 0
        atlas_layer = self.atlas_layers[0]
        atlas_mask = self\
            .atlas\
            .get_region_mask(atlas_layer, attr="acronym")\
            .raw
        _expect_equal(
            circuit_atlas_mask, atlas_mask,
            """Compared circuit atlas mask layer {}
            against atlas mask layer {}""".format(layer, atlas_layer))

    def multiple_layer_mask(self):
        """
        Test that masks for multiple layers at once are good.
        """
        layers = collections.get_list(self.layers_to_test)

        if len(layers) < 2:
            raise ValueError(
                """
                Cannot run multiple layer mask test if layers to test are < 2:
                {}.
                """.format(self.layers_to_test))

        circuit_atlas_mask = self\
            .circuit_atlas\
            .get_mask(layer=collections.get_list(layers))
        assert len(circuit_atlas_mask.shape) == 3
        assert np.nansum(circuit_atlas_mask) > 0
        atlas_mask = np.any(
            [self.atlas.get_region_mask(atlas_layer, attr="acronym").raw
             for atlas_layer in self.atlas_layers],
            axis=0)
        _expect_equal(
            circuit_atlas_mask, atlas_mask,
            """circuit atlas mask with {} Trues
            != atlas mask with {} Trues""".format(
                np.nansum(circuit_atlas_mask),
                np.nansum(atlas_mask)))

    def region_layer_mask(self):
        """
        Tests that mask for region, layer pair is good.
        """
        layer = collections.get_list(self.layers_to_test)[0]
        region = collections.get_list(self.regions_to_test)[0]
        circuit_atlas_mask = self\
            .circuit_atlas\
            .get_mask(
                region=region,
                layer=layer)
        atlas_layer = self.atlas_layers[0]
        atlas_region = self.atlas_regions[0]
        atlas_region_mask = self\
            .atlas\
            .get_region_mask(atlas_region, attr="acronym")\
            .raw
        atlas_layer_mask = self\
            .atlas\
            .get_region_mask(atlas_layer, attr="acronym")\
            .raw
        atlas_mask = np.logical_and(atlas_region_mask, atlas_layer_mask)
        _expect_equal(circuit_atlas_mask, atlas_mask)

    def region_multiple_layer_mask(self):
        """
        Tests that masks for region, layer pairs for a single region
        and multiple layers are good.
        """
        layers = collections.get_list(self.layers_to_test)

        if len(layers) < 2:
            raise ValueError(
                """
                Cannot run multiple layer mask test if layers to test are < 2:
                {}.
                """.format(self.layers_to_test))

        region = collections.get_list(self.regions_to_test)[0]
        circuit_atlas_mask = self\
            .circuit_atlas\
            .get_mask(
                region=region,
                layer=layers)
        atlas_region = self.atlas_regions[0]
        atlas_region_mask = self\
            .atlas\
            .get_region_mask(atlas_region, attr="acronym")\
            .raw
        atlas_layer_mask =  np.any(
            [self.atlas.get_region_mask(atlas_layer, attr="acronym").raw
             for atlas_layer in self.atlas_layers],
            axis=0)
        atlas_mask = np.logical_and(atlas_region_mask, atlas_layer_mask)
        _expect_equal(circuit_atlas_mask, atlas_mask)
            
    def multiple_region_multiple_layer_mask(self):
        """
        Tests that masks for region, layer pairs for a single region
        and multiple layers are good.
        """
        layers = collections.get_list(self.layers_to_test)
        regions = collections.get_list(self.regions_to_test)
        if len(layers) < 2 or len(regions) < 2 :
            raise ValueError(
                """
                Cannot run multiple region, layer mask test
                if layers to test are < 2 or regions to test are < 2:
                {} {}.
                """.format(
                    self.layers_to_test,
                    self.regions_to_test))

        circuit_atlas_mask = self\
            .circuit_atlas\
            .get_mask(
                region=regions,
                layer=layers)
        atlas_region_mask = np.any(
            [self.atlas.get_region_mask(atlas_region, attr="acronym").raw
             for atlas_region in self.atlas_regions],
            axis=0)
        atlas_layer_mask =  np.any(
            [self.atlas.get_region_mask(atlas_layer, attr="acronym").raw
             for atlas_layer in self.atlas_layers],
            axis=0)
        atlas_mask = np.logical_and(atlas_region_mask, atlas_layer_mask)
        _expect_equal(circuit_atlas_mask, atlas_mask)

    def run_mask_tests(self):
        """
        Run only mask tests.
        """
        self.region_mask()
        self.layer_mask()
        self.multiple_layer_mask()
        self.region_layer_mask()
        self.multiple_region_multiple_layer_mask()
        return (True, "All Good")

    def run_density_tests(self):
        """
        Run only cell density tests.
        """
        return (False, "No cell density tests defined")

    testable_features = ("masks", "densities")

    def __call__(self, *features_to_test):
        """
        Run all tests.
        """
        if len(features_to_test) > 0:
            testable_features =\
                set(features_to_test)\
                .intersection(self.testable_features)
            if len(testable_features) == 0:
                raise ValueError(
                    "None of the features {}  are testable."\
                    .format(features_to_test))
        else:
            testable_features = self.testable_features

        if "masks" in testable_features:
            result, message = self.run_mask_tests()
            assert result, message
        if "densities" in testable_features:
            result, message = self.run_density_tests()
            assert result, message


def test_S1RatSSCxDiss():
    """
    Test Rat SSCx Dissemination atlas.
    """
    name_atlas = "S1RatSSCxDiss"
    circuit_atlas_test =\
        CircuitAtlasTest(
            label=name_atlas,
            path_atlas=path_atlas[name_atlas],
            regions_to_test=["SSp-ll", "SSp-ul"],
            layers_to_test=["L1", "L2"])
    circuit_atlas_test("masks")


def test_S1MouseNeoCx():
    """
    Test Mouse Neo-cortex atlas.
    """
    name_atlas = "S1MouseNeoCx"
    circuit_atlas_test =\
        CircuitAtlasTest(
            label=name_atlas,
            path_atlas=path_atlas[name_atlas],
            regions_to_test=["SSp-ll", "SSp-ul"],
            layers_to_test=["L1", "L2"])
    circuit_atlas_test("masks")
