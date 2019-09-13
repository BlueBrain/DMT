"""
Test develop the behavior of CircuitAtlas
"""

import numpy as np
from voxcell.nexus.voxelbrain import Atlas
from dmt.tk.field import WithFields, Field, lazyfield
from dmt.tk import collections
from .. import CircuitAtlas
from . import *

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
        A list of two-tuples of acronyms to test with.
        The first element of each tuple should be the value that `CircuitAtlas`
        will accept for queries, the second element should be what the
        underlying atlas will understand. Notice that these two values can be
        different --- `CircuitAtlas` will accept terms as used in the ABI
        atlas, which will be internally translated by the code to adapt to
        a Paxinos atlas.
        """)
    layers_to_test = Field(
        """
        A list of two-tuples off acronyms to test with.
        The first element of each tuple should be the value that `CircuitAtlas`
        will accept for queries, the second element should be what the
        underlying atlas will understand. We have to pass both because
        different implementations of the atlas may differ in their layer-naming
        convention.
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

    def region_mask(self):
        """
        Test that masks for regions are good.
        """
        for region, atlas_region in collections.get_list(self.regions_to_test):
            expect_equal(
                self.circuit_atlas.get_mask(region=region),
                self.atlas.get_region_mask(atlas_region).raw)

    def layer_mask(self):
        """
        Test that masks for layers are good.
        """
        layer, atlas_layer = collections.get_list(self.layers_to_test)[0]
        circuit_atlas_mask = self\
            .circuit_atlas\
            .get_mask(layer=layer)
        assert len(circuit_atlas_mask.shape) == 3
        assert np.nansum(circuit_atlas_mask) > 0
        atlas_mask = self\
            .atlas\
            .get_region_mask(atlas_layer, attr="acronym")\
            .raw
        expect_equal(
            circuit_atlas_mask, atlas_mask,
            """
            Compared circuit atlas mask layer {}
            against atlas mask layer {}
            """.format(layer, atlas_layer))

    def multiple_layer_mask(self):
        """
        Test that masks for multiple layers at once are good.
        """
        layers_to_test = collections.get_list(self.layers_to_test)

        if len(layers_to_test) < 2:
            raise ValueError(
                """
                Cannot run multiple layer mask test if layers to test are < 2:
                {}.
                """.format(self.layers_to_test))

        circuit_atlas_mask = self\
            .circuit_atlas\
            .get_mask(layer=[layer for layer, _ in layers_to_test])

        assert len(circuit_atlas_mask.shape) == 3
        assert np.nansum(circuit_atlas_mask) > 0

        atlas_mask = np.any(
            [self.atlas.get_region_mask(atlas_layer, attr="acronym").raw
             for _, atlas_layer in layers_to_test],
            axis=0)
        expect_equal(
            circuit_atlas_mask, atlas_mask,
            """circuit atlas mask with {} Trues
            != atlas mask with {} Trues""".format(
                np.nansum(circuit_atlas_mask),
                np.nansum(atlas_mask)))

    def region_layer_mask(self):
        """
        Tests that mask for region, layer pair is good.
        """
        layer, atlas_layer = collections.get_list(self.layers_to_test)[0]
        region, atlas_region = collections.get_list(self.regions_to_test)[0]
        circuit_atlas_mask = self\
            .circuit_atlas\
            .get_mask(region=region, layer=layer)

        atlas_region_mask = self\
            .atlas\
            .get_region_mask(atlas_region, attr="acronym")\
            .raw
        atlas_layer_mask = self\
            .atlas\
            .get_region_mask(atlas_layer, attr="acronym")\
            .raw
        atlas_mask = np.logical_and(atlas_region_mask, atlas_layer_mask)
        expect_equal(circuit_atlas_mask, atlas_mask)

    def region_multiple_layer_mask(self):
        """
        Tests that masks for region, layer pairs for a single region
        and multiple layers are good.
        """
        layers_to_test = collections.get_list(self.layers_to_test)

        if len(layers_to_test) < 2:
            raise ValueError(
                """
                Cannot run multiple layer mask test if layers to test are < 2:
                {}.
                """.format(self.layers_to_test))

        region, atlas_region = collections.get_list(self.regions_to_test)[0]
        circuit_atlas_mask = self\
            .circuit_atlas\
            .get_mask(
                region=region,
                layer=[layer for layer, _ in layers_to_test])
        atlas_region_mask = self\
            .atlas\
            .get_region_mask(atlas_region, attr="acronym")\
            .raw
        atlas_layer_mask = np.any(
            [self.atlas.get_region_mask(atlas_layer, attr="acronym").raw
             for _,natlas_layer in layers_to_test],
            axis=0)
        atlas_mask = np.logical_and(atlas_region_mask, atlas_layer_mask)
        expect_equal(circuit_atlas_mask, atlas_mask)

    def multiple_region_multiple_layer_mask(self):
        """
        Tests that masks for region, layer pairs for a single region
        and multiple layers are good.
        """
        layers_to_test = collections.get_list(self.layers_to_test)
        regions_to_test = collections.get_list(self.regions_to_test)
        if len(layers_to_test) < 2 or len(regions_to_test) < 2 :
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
                region=[region for region, _ in regions_to_test],
                layer=[layer for layer, _ in layers_to_test])
        atlas_region_mask = np.any(
            [self.atlas.get_region_mask(atlas_region, attr="acronym").raw
             for _, atlas_region in regions_to_test],
            axis=0)
        atlas_layer_mask =  np.any(
            [self.atlas.get_region_mask(atlas_layer, attr="acronym").raw
             for _, atlas_layer in layers_to_test],
            axis=0)
        atlas_mask = np.logical_and(atlas_region_mask, atlas_layer_mask)
        expect_equal(circuit_atlas_mask, atlas_mask)

    def depth_mask(self):
        """
        Test that mask for depth is good.
        """
        depths_to_test = [(0, 25), (500, 700)]

        circuit_atlas_mask = self.circuit_atlas.get_mask(depth=depths_to_test)

        top = self.atlas.load_data("[PH]1").raw[..., 1]
        pdy = top - self.atlas.load_data("[PH]y").raw

        valid_voxel = self.atlas.load_data("brain_regions").raw != 0
        at_depth_voxel = np.any(
            [np.logical_and(x <= pdy, pdy < y) for x, y in depths_to_test],
            axis=0)
        atlas_mask = np.logical_and(at_depth_voxel, valid_voxel)

        expect_equal(
            circuit_atlas_mask,
            atlas_mask,
            """
            Circuit atlas mask with total Trues: {},
            Direct Atlas mask with total Trues: {}
            """.format(
                np.nansum(circuit_atlas_mask),
                np.nansum(atlas_mask)))

    def height_mask(self):
        """
        Test that mask for height is good.
        """
        heights_to_test = [(0, 25), (500, 700)]

        circuit_atlas_mask = self.circuit_atlas.get_mask(height=heights_to_test)
        
        bottom = self.atlas.load_data("[PH]6").raw[..., 0]
        phy = self.atlas.load_data("[PH]y").raw - bottom

        valid_voxel = self.atlas.load_data("brain_regions").raw != 0
        at_height_voxel = np.any(
            [np.logical_and(x <= phy, phy < y) for x, y in heights_to_test],
            axis=0)
        atlas_mask = np.logical_and(at_height_voxel, valid_voxel)

        expect_equal(
            circuit_atlas_mask,
            atlas_mask,
            """
            Circuit atlas mask with total Trues: {},
            Direct Atlas mask with total Trues: {}
            """.format(
                np.nansum(circuit_atlas_mask),
                np.nansum(atlas_mask)))       

    def run_mask_tests(self):
        """
        Run only mask tests.
        """
        self.region_mask()
        self.layer_mask()
        self.multiple_layer_mask()
        self.region_layer_mask()
        self.multiple_region_multiple_layer_mask()
        self.depth_mask()
        self.height_mask()
        return (True, "All Good")

    def run_density_tests(self):
        """
        Run only cell density tests.
        """
        return (False, "No density tests defined.")

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
            regions_to_test=[("SSp-ll", "S1HL"), ("SSp-ul", "S1FL")],
            layers_to_test=[("L1", "@L1"), ("L2", "@L2")])
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
            regions_to_test=[("SSp-ll", "SSp-ll"), ("SSp-ul", "SSp-ul")],
            layers_to_test=[("L1", "@.*1"), ("L2", "@.*2")])
    circuit_atlas_test("masks")
