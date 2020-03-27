# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Tests for `BlueBrainCircuitAtlas` and it's associated classes and code.
"""
import os
import numpy as np
import numpy.testing as npt
from voxcell.nexus.voxelbrain import Atlas
from dmt.tk.journal import Logger
from dmt.tk.field import WithFields, Field, lazyfield
from dmt.tk.collections import take, get_list
from .. import BlueBrainCircuitAtlas

def project(number):
    """
    Get path to the project, given its number.
    """
    return "/gpfs/bbp.cscs.ch/project/proj{}".format(number)

path_rat_sscx_dissemination_atlases = os.path.join(
    project(64),
    "dissemination",
    "data/atlas/S1/MEAN/juvenile_L23_MC_BTC_shifted_down_L1_ALL_INH")
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
    "S1RatSSCxDiss_Bio0": os.path.join(
        path_rat_sscx_dissemination_atlases,
        "Bio_0"),
    "S1RatSSCxDiss_Bio1": os.path.join(
        path_rat_sscx_dissemination_atlases,
        "Bio_1"),
    "S1RatSSCxDiss_Bio2": os.path.join(
        path_rat_sscx_dissemination_atlases,
        "Bio_2"),
    "S1RatSSCxDiss_BioM": os.path.join(
        path_rat_sscx_dissemination_atlases,
        "Bio_M")}

def expect_equal(x, y, message=""):
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

logger = Logger(
    client="CircuitAtlasTest",
    level=Logger.Level.TEST)


class CircuitAtlasTest(WithFields):
    """
    Test `BlueBrainCircuitAtlas`.
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
        The first element of each tuple should be the value that 
        `BlueBrainCircuitAtlas` methods will accept for queries,
        the second element should be what the underlying atlas will understand.
        Notice that these two values can be different --- 
        `BlueBrainCircuitAtlas` will accept terms as used in the ABI
        atlas, which will be internally translated by the code to adapt to
        a Paxinos atlas.
        """)
    layers_to_test = Field(
        """
        A list of two-tuples off acronyms to test with.
        The first element of each tuple should be the value that 
        `BlueBrainCircuitAtlas` will accept for queries, the second element 
        should be what the underlying atlas will understand. We have to pass 
        both because different implementations of the atlas may differ in their 
        layer-naming convention.
        """)

    @lazyfield
    def circuit_atlas(self):
        """
        `BlueBrainCircuitAtlas` instance to be tested.
        """
        return BlueBrainCircuitAtlas(path=self.path_atlas)

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
        for region, atlas_region in get_list(self.regions_to_test):
            expect_equal(
                self.circuit_atlas.get_mask(region=region),
                self.atlas.get_region_mask(atlas_region).raw)

    def layer_mask(self):
        """
        Test that masks for layers are good.
        """
        layer, atlas_layer = get_list(self.layers_to_test)[0]
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
        layers_to_test = get_list(self.layers_to_test)

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
        layer, atlas_layer = get_list(self.layers_to_test)[0]
        region, atlas_region = get_list(self.regions_to_test)[0]
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
        layers_to_test = get_list(self.layers_to_test)

        if len(layers_to_test) < 2:
            raise ValueError(
                """
                Cannot run multiple layer mask test if layers to test are < 2:
                {}.
                """.format(self.layers_to_test))

        region, atlas_region = get_list(self.regions_to_test)[0]
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
        layers_to_test = get_list(self.layers_to_test)
        regions_to_test = get_list(self.regions_to_test)
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

    def random_position_inside_volume(self,  number=1000):
        """
        Test that `BlueBrainCircuitAtlas` yields random positions inside voxel 
        data volume.
        """
        regions_to_test = [
            region for region, _ in get_list(self.regions_to_test)]
        layers_to_test = [
            layer for layer, _ in get_list(self.layers_to_test)]
        voxel_data = self.atlas.load_data("brain_regions")
        brain_regions = voxel_data.raw
        for region in regions_to_test:
            for layer in layers_to_test:
                logger.info(
                    logger.get_source_info(),
                    """
                    Test random position for region {}, layer {}.
                    """.format(region, layer))
                region_layer_mask = self\
                    .circuit_atlas\
                    .get_mask(
                        region=region,
                        layer=layer)
                random_positions = self\
                    .circuit_atlas\
                    .random_positions(
                        region=region,
                        layer=layer)
                layer_region_ids = self\
                    .circuit_atlas\
                    .region_layer\
                    .get_ids(region, layer)
                for n, rpos in enumerate(take(number, random_positions)):
                    voxel_indices = voxel_data.positions_to_indices(rpos)
                    for axis, index in [("X", 0), ("Y", 1), ("Z", 2)]:
                        observed = voxel_indices[index]
                        upper_bound = voxel_data.shape[0]
                        assert  observed <= upper_bound,\
                            """
                            Random position should lie inside the volume.
                            For position {}, {} index {} is not less than {}
                            """.format(
                                rpos,
                                axis,
                                observed,
                                upper_bound)
                    i = voxel_indices[0]
                    j = voxel_indices[1]
                    k = voxel_indices[2]
                    assert region_layer_mask[i, j, k],\
                        """
                        Region layer mask should be True at indices ({}, {}, {})
                        """.format(i, j, k)
                    _id = brain_regions[i, j, k]
                    assert _id in layer_region_ids,\
                        "ID {} should be in layer region ids {}".format(
                            _id, layer_region_ids)
                assert n == number - 1,\
                    """
                    Random position generator should be infinite.
                    Instead it could generate only {} values (compared
                    to the requested {}).
                    """.format(n, number)

        return ("True", "All Good")

    def run_random_position_tests(self):
        """
        Run only random position tests.
        """
        self.random_position_inside_volume()

        return ("True", "All Good")

    testable_features = ("masks", "densities", "random_positions")

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
        if "random_positions" in testable_features:
            result, message = self.run_random_position_tests()
            assert result, message
        

