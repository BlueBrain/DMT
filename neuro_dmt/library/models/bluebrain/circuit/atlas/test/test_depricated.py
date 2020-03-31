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
Test `CircuitAltas`
"""

import os
import numpy as np
import numpy.testing as npt
import pytest as pyt
from voxcell.nexus.voxelbrain import Atlas
from dmt.tk.field import Field, lazyfield, WithFields
from neuro_dmt.models.bluebrain.circuit import atlas as circuit_atlas
from neuro_dmt.models.bluebrain.circuit.atlas import CircuitAtlas
from neuro_dmt.terminology.parameters import\
    BRAIN_REGION, LAYER, COLUMN, MTYPE,\
    DEPTH, HEIGHT


# TODO: test region X OR layer Y OR column Z
# TODO: test excludde xyz


def test_append_nrrd():
    """
    Test appending `.nrrd` to a file's name.
    """
    assert circuit_atlas._nrrd("a") == "a.nrrd"
    files = ["a", "b", "c"]
    assert all(
        fnrrd == "{}.nrrd".format(f)
        for f, fnrrd in zip(files, circuit_atlas._nrrd(*files)))

class Test_CircuitAtlas:

    class Test_NCX_O1(WithFields):
        """
        test for NCX release O1 circuit
        TODO: replace with dummy atlas mimicking properties
        """
        path_atlas = Field(
            """
            Path to the atlas to be tested.
            """,
            __default_value__=os.path.join(
                "/gpfs/bbp.cscs.ch/project/proj66",
                "entities/dev/atlas/O1-152/"))

        @lazyfield
        def circuit_atlas(self):
            """
            The `CircuitAtlas` instance to test with.
            """
            return CircuitAtlas(self.path_atlas)

        @lazyfield
        def atlas(self):
            """
            `Atlas` instance to test against.
            """
            return Atlas.open(self.path_atlas)

        def test_mask_blank_parameters(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters({}),
                self.atlas.load_data("brain_regions").raw != 0)

        def test_warns_region(self):
            with pyt.warns(Warning):
                npt.assert_array_equal(
                    self.circuit_atlas.mask_for_parameters({BRAIN_REGION: 'SSp'}),
                    self.atlas.load_data("brain_regions").raw != 0)

        def test_mask_layers(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters({LAYER: 'L1'}),
                self.atlas.get_region_mask("L1").raw)

        def test_mask_multiple_layers(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters(
                    {LAYER: ['L2', 'L5']}),
                np.logical_or(
                    self.atlas.get_region_mask("L2").raw,
                    self.atlas.get_region_mask("L5").raw))

        def test_mask_column(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters({COLUMN: 'mc0'}),
                self.atlas.get_region_mask("mc0_Column").raw)

        def test_mask_three_columns(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters({COLUMN:
                                             ['mc0', 'mc6', 'mc4']}),
                np.logical_or(
                    np.logical_or(
                        self.atlas.get_region_mask("mc0_Column").raw,
                        self.atlas.get_region_mask("mc6_Column").raw),
                    self.atlas.get_region_mask("mc4_Column").raw))

        def test_mask_column_layer(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters(
                    {COLUMN: ['mc2'], LAYER: ['L2', 'L3']}),
                np.logical_and(
                    self.atlas.get_region_mask('mc2_Column').raw,
                    np.logical_or(
                        self.atlas.get_region_mask("L2").raw,
                        self.atlas.get_region_mask("L3").raw)))

        def test_cell_density(self):
            with pyt.warns(Warning):
                assert np.isnan(self.circuit_atlas.cell_density({LAYER: 'L4'}))

    class Test_Rat_2019_O1:
        """
        Test for SSCX dissemination O1 circuit
        TODO: replace with dummy atlas mimicing properties"""

        circuit_atlas = CircuitAtlas(
            "/gpfs/bbp.cscs.ch/project/proj64/"
            "dissemination/data/atlas/O1/MEAN/mean")
        atlas = Atlas.open(
            "/gpfs/bbp.cscs.ch/project/proj64/"
            "dissemination/data/atlas/O1/MEAN/mean")

        def test_mask_blank_parameters(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters({}),
                self.atlas.load_data("brain_regions").raw != 0)

        def test_warns_region(self):
            with pyt.warns(Warning):
                npt.assert_array_equal(
                    self.circuit_atlas.mask_for_parameters({BRAIN_REGION: 'SSp'}),
                    self.atlas.load_data("brain_regions").raw != 0)

        def test_mask_layers(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters({LAYER: 'L1'}),
                self.atlas.get_region_mask("@;1$").raw)

        def test_mask_multiple_layers(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters(
                    {LAYER: ['L2', 'L5']}),
                np.logical_or(
                    self.atlas.get_region_mask("@;2$").raw,
                    self.atlas.get_region_mask("@;5$").raw))

        def test_mask_column(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters({COLUMN: 'mc0'}),
                self.atlas.get_region_mask("mc0_Column").raw)

        def test_mask_three_columns(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters({COLUMN:
                                             ['mc0', 'mc6', 'mc4']}),
                np.logical_or(
                    np.logical_or(
                        self.atlas.get_region_mask("mc0_Column").raw,
                        self.atlas.get_region_mask("mc6_Column").raw),
                    self.atlas.get_region_mask("mc4_Column").raw))

        def test_mask_column_layer(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters(
                    {COLUMN: ['mc2'], LAYER: ['L2', 'L3']}),
                np.logical_or(
                    self.atlas.get_region_mask('mc2;2').raw,
                    self.atlas.get_region_mask('mc2;3').raw))

        def test_cell_density(self):
            npt.assert_array_equal(
                self.circuit_atlas.cell_density({LAYER: 'L5', COLUMN: 'mc2'}),
                (self.atlas.load_data("[cell_density]EXC").raw
                 + self.atlas.load_data("[cell_density]INH").raw)[
                     self.atlas.get_region_mask("mc2;5").raw])

        def test_sclass_density(self):
            npt.assert_array_equal(
                self.circuit_atlas.cell_density({'sclass': 'EXC'}),
                self.atlas.load_data("[cell_density]EXC").raw[
                    self.atlas.load_data("brain_regions").raw != 0]
                )
            npt.assert_array_equal(
                self.circuit_atlas.cell_density({'sclass': 'INH'}),
                self.atlas.load_data("[cell_density]INH").raw[
                    self.atlas.load_data("brain_regions").raw != 0]
                )

        def test_mtype_density(self):
            npt.assert_array_equal(
                self.circuit_atlas.cell_density(
                    {MTYPE: 'MC', LAYER: ['L2', 'L3']}),
                self.atlas.load_data("[cell_density]L23_MC").raw[
                    self.atlas.get_region_mask('@;2$|;3$').raw])

    class Test_Rat_2018_O1:
        """
        test for rebuilt 2018 rat atlas
        TODO: replace with dummy atlas mimicking properties
        """

        circuit_atlas = CircuitAtlas(
            "/gpfs/bbp.cscs.ch/project/proj64/entities/dev/atlas/"
            "fixed_77831ACA-6198-4AA0-82EF-D0475A4E0647_01-06-2018")
        atlas = Atlas.open(
            "/gpfs/bbp.cscs.ch/project/proj64/entities/dev/atlas/"
            "fixed_77831ACA-6198-4AA0-82EF-D0475A4E0647_01-06-2018")

        def test_mask_blank_parameters(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters({}),
                self.atlas.load_data("brain_regions").raw != 0)

        def test_warns_region(self):
            with pyt.warns(Warning):
                npt.assert_array_equal(
                    self.circuit_atlas.mask_for_parameters({BRAIN_REGION: 'SSp'}),
                    self.atlas.load_data("brain_regions").raw != 0)

        def test_mask_layers(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters({LAYER: 'L1'}),
                self.atlas.get_region_mask("L1").raw)

        def test_mask_multiple_layers(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters(
                    {LAYER: ['L2', 'L5']}),
                np.logical_or(
                    self.atlas.get_region_mask("L2").raw,
                    self.atlas.get_region_mask("L5").raw))

        def test_mask_column(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters({COLUMN: 'mc0'}),
                self.atlas.get_region_mask("mc0_Column").raw)

        def test_mask_three_columns(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters({COLUMN:
                                             ['mc0', 'mc6', 'mc4']}),
                np.logical_or(
                    np.logical_or(
                        self.atlas.get_region_mask("mc0_Column").raw,
                        self.atlas.get_region_mask("mc6_Column").raw),
                    self.atlas.get_region_mask("mc4_Column").raw))

        def test_mask_column_layer(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters(
                    {COLUMN: ['mc2'], LAYER: ['L2', 'L3']}),
                np.logical_and(
                    self.atlas.get_region_mask('mc2_Column').raw,
                    np.logical_or(
                        self.atlas.get_region_mask("L2").raw,
                        self.atlas.get_region_mask("L3").raw)))

        def test_cell_density(self):
            import glob
            from os.path import basename, join
            atlasnrrds = [basename(fpath).split(".")[0] for fpath in
                               glob.glob(join(self.atlas.dirpath,
                                              "*.nrrd"))]
            # set to avoid duplicates from .patched
            atlasmtypenames = {nrrd for nrrd in atlasnrrds
                               if (nrrd.isupper() and "[PH]" not in nrrd)}
            npt.assert_array_equal(
                self.circuit_atlas.cell_density({LAYER: 'L5', COLUMN: 'mc2'}),
                np.sum([self.atlas.load_data(mtype).raw
                        for mtype in atlasmtypenames],
                       axis=0)[
                           np.logical_and(
                               self.atlas.get_region_mask("mc2_Column").raw,
                               self.atlas.get_region_mask("L5").raw)])

        def test_sclass_density(self):
            with pyt.warns(Warning):
                assert np.isnan(self.circuit_atlas.cell_density({'sclass': 'EXC'}))

        def test_mtype_density(self):
            npt.assert_array_equal(
                self.circuit_atlas.cell_density(
                    {MTYPE: 'NGC-DA', LAYER: ['L5', 'L1']}),
                self.atlas.load_data("NGC-DA").raw[
                    self.atlas.get_region_mask('@L5$|L1$').raw])

    class Test_hippocampus:
        """
        test for O1 hippocampus atlas
        TODO: replace with dummy atlas mimicing properties"""

        circuit_atlas = CircuitAtlas(
            "/gpfs/bbp.cscs.ch/project/proj42/entities/dev/atlas/"
            "20190625-CA3-O1-atlas/")
        atlas = Atlas.open(
            "/gpfs/bbp.cscs.ch/project/proj42/entities/dev/atlas/"
            "20190625-CA3-O1-atlas/")

        def test_mask_blank_parameters(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters({}),
                self.atlas.load_data("brain_regions").raw != 0)

        def test_warns_region(self):
            with pyt.warns(Warning):
                npt.assert_array_equal(
                    self.circuit_atlas.mask_for_parameters({BRAIN_REGION: 'SSp'}),
                    self.atlas.load_data("brain_regions").raw != 0)

        def test_mask_layers(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters({LAYER: 'SP'}),
                self.atlas.get_region_mask("@;SP$").raw)

        def test_mask_multiple_layers(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters(
                    {LAYER: ['SO', 'SLM']}),
                np.logical_or(
                    self.atlas.get_region_mask("@;SO$").raw,
                    self.atlas.get_region_mask("@;SLM$").raw))

        def test_mask_column(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters({COLUMN: 'mc0'}),
                self.atlas.get_region_mask("mc0_Column").raw)

        def test_mask_three_columns(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters({COLUMN:
                                             ['mc0', 'mc6', 'mc4']}),
                np.logical_or(
                    np.logical_or(
                        self.atlas.get_region_mask("mc0_Column").raw,
                        self.atlas.get_region_mask("mc6_Column").raw),
                    self.atlas.get_region_mask("mc4_Column").raw))

        def test_mask_column_layer(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters(
                    {COLUMN: ['mc2'], LAYER: ['SO', 'SR']}),
                np.logical_and(
                    self.atlas.get_region_mask('mc2_Column').raw,
                    np.logical_or(
                        self.atlas.get_region_mask("@;SO$").raw,
                        self.atlas.get_region_mask("@;SR$").raw)))

        def test_cell_density(self):
            with pyt.warns(Warning):
                assert np.isnan(self.circuit_atlas.cell_density({LAYER: 'L4'}))

    # TODO: test being provided in-terminology region that is not present
    #       e.g. SSp-dz
    class Test_BBA:
        """
        test for the AllenAtlas based BlueBrainAtlas
        TODO: replace with dummy atlas mimicing properties"""

        circuit_atlas = CircuitAtlas(
            "/gpfs/bbp.cscs.ch/project/proj68/entities/"
            "dev/atlas/ccf_2017-50um/20181114")
        atlas = Atlas.open(
            "/gpfs/bbp.cscs.ch/project/proj68/entities/"
            "dev/atlas/ccf_2017-50um/20181114")

        def test_mask_blank_parameters(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters({}),
                self.atlas.load_data("brain_regions").raw != 0)

        def test_region_mask(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters({BRAIN_REGION: 'SSp'}),
                self.atlas.get_region_mask("SSp").raw)

        def test_mask_layers(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters({LAYER: 'L2'}),
                self.atlas.get_region_mask("@.*2$").raw)

        def test_mask_multiple_layers(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters(
                    {LAYER: ['SO', 'L4']}),
                np.logical_or(
                    np.logical_and(
                        self.atlas.get_region_mask("@.*so$").raw,
                        self.atlas.get_region_mask("CA")),
                    self.atlas.get_region_mask("@.*4$").raw))

        def test_warns_column(self):
            with pyt.warns(Warning):
                npt.assert_array_equal(
                    self.circuit_atlas.mask_for_parameters({COLUMN: 'mc2'}),
                    self.atlas.load_data("brain_regions").raw != 0)

        def test_mask_region_layer(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters(
                    {BRAIN_REGION: "SSp-ll", LAYER: ['L1', 'L4']}),
                np.logical_or(
                    self.atlas.get_region_mask("SSp-ll1").raw,
                    self.atlas.get_region_mask("SSp-ll4").raw))

        def test_cell_density(self):
            npt.assert_array_equal(
                self.circuit_atlas.cell_density({BRAIN_REGION: "RT"}),
                np.sum([
                    self.atlas.load_data("[cell_density]{}".format(sc)).raw
                    for sc in ("EXC", "INH")], axis=0)[
                            self.atlas.get_region_mask("RT").raw])

        def test_mtype_density(self):
            npt.assert_array_equal(
                self.circuit_atlas.cell_density({
                    "mtype": "IPC",
                    BRAIN_REGION: "MOp"}),
                np.nansum([self.atlas.load_data(
                    "[cell_density]L2_IPC").raw,
                           self.atlas.load_data(
                               "[cell_density]L6_IPC").raw],
                          axis=0)[
                              self.atlas.get_region_mask("MOp").raw])

        # TODO: how to handle multiple areas e.g. thalamus depth, etc.
        def test_absolute_depths(self):
            expdepths = np.unique(-self.atlas.load_data("[PH]y").raw)
            expdepths = expdepths[np.isfinite(expdepths)]
            npt.assert_array_equal(self.circuit_atlas.depths(), expdepths)

        def test_mask_for_depth(self):
            atlas_y = -self.atlas.load_data("[PH]y").raw
            posns = [(0, 25), (500, 700)]
            exp_masks = np.logical_and(
                np.any([np.logical_and(atlas_y >= p[0], atlas_y < p[1])
                        for p in posns], axis=0),
                self.atlas.load_data("brain_regions").raw != 0)

            npt.assert_array_equal(self.circuit_atlas.mask_for_parameters(
                {ABSOLUTE_DEPTH: posns}),
                                   exp_masks)
            posns = [12.5, 50]
            exp_masks = np.logical_and(
                np.any([atlas_y == p for p in posns], axis=0),
                self.atlas.load_data("brain_regions").raw != 0)

            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters(
                    {ABSOLUTE_DEPTH: posns}),
                exp_masks)

        def test_absolute_heights(self):
            expheights = np.unique(self.atlas.load_data("[PH]y").raw
                                   - self.atlas.load_data("[PH]6").raw[..., 0])
            expheights = expheights[np.isfinite(expheights)]
            npt.assert_array_equal(self.circuit_atlas.heights(), expheights)

        def test_mask_for_height(self):
            atlas_y = self.atlas.load_data("[PH]y").raw\
                      - self.atlas.load_data("[PH]6").raw[..., 0]
            posns = [(0, 25), (500, 700)]
            exp_masks = np.logical_and(
                np.any([np.logical_and(atlas_y >= p[0], atlas_y < p[1])
                        for p in posns], axis=0),
                self.atlas.load_data("brain_regions").raw != 0)

            npt.assert_array_equal(self.circuit_atlas.mask_for_parameters(
                {ABSOLUTE_HEIGHT: posns}),
                                   exp_masks)
            posns = [12.5, 50]
            exp_masks = np.logical_and(
                np.any([atlas_y == p for p in posns], axis=0),
                self.atlas.load_data("brain_regions").raw != 0)

            npt.assert_array_equal(self.circuit_atlas.mask_for_parameters(
                {ABSOLUTE_HEIGHT: posns}),
                                   exp_masks)

    # TODO: test behavior when provided PW-style brain region
    class Test_2019_S1:
        """
        test for paxinos-watson based S1 atlas of somatosensory cortex
        TODO: replace with dummy atlas mimicing properties"""

        circuit_atlas = CircuitAtlas(
            "/gpfs/bbp.cscs.ch/project/proj64/"
            "dissemination/data/atlas/S1/MEAN/mean")
        atlas = Atlas.open(
            "/gpfs/bbp.cscs.ch/project/proj64"
            "/dissemination/data/atlas/S1/MEAN/mean")

        def test_region_mask(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters({BRAIN_REGION: 'SSp'}),
                self.atlas.get_region_mask("S1").raw)

        def test_mask_multiple_layers(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters(
                    {LAYER: ['L1', 'L4']}),
                np.logical_or(
                    self.atlas.get_region_mask("@L1").raw,
                    self.atlas.get_region_mask("@L4").raw))

        def test_warns_column(self):
            with pyt.warns(Warning):
                npt.assert_array_equal(
                    self.circuit_atlas.mask_for_parameters({COLUMN: 'mc2'}),
                    self.atlas.load_data("brain_regions").raw != 0)

        def test_mask_region_layer(self):
            npt.assert_array_equal(
                self.circuit_atlas.mask_for_parameters(
                    {BRAIN_REGION: "SSp-ll", LAYER: ['L1', 'L4']}),
                np.logical_and(
                    self.atlas.get_region_mask("S1HL").raw,
                    np.logical_or(
                        self.atlas.get_region_mask("@L1").raw,
                        self.atlas.get_region_mask("@L4").raw)))

        def test_cell_density(self):
            npt.assert_array_equal(
                self.circuit_atlas.cell_density({BRAIN_REGION: "SSp-m"}),
                np.nansum([
                    self.atlas.load_data("[cell_density]{}".format(sc)).raw
                    for sc in ("EXC", "INH")], axis=0)[
                            self.atlas.get_region_mask("S1J").raw])

        def test_mtype_density(self):
            npt.assert_array_equal(
                self.circuit_atlas.cell_density({
                    "mtype": "IPC",
                    BRAIN_REGION: "SS"}),
                np.nansum([self.atlas.load_data(
                               "[cell_density]L2_IPC").raw,
                           self.atlas.load_data(
                               "[cell_density]L6_IPC").raw],
                          axis=0)[
                              self.atlas.get_region_mask("SSCtx").raw])

    # TODO: find and fix source of numpy RuntimeWarnings
    class Test_2017_S1:

        circuit_atlas = CircuitAtlas(
            "/gpfs/bbp.cscs.ch/project/proj64/circuits/S1.v6a/r0/.atlas/"
            "C63CB79F-392A-4873-9949-0D347682253A")

        atlas = Atlas.open(
            "/gpfs/bbp.cscs.ch/project/proj64/circuits/S1.v6a/r0/.atlas/"
            "C63CB79F-392A-4873-9949-0D347682253A")

        def test_absolute_depths(self):
            with pyt.raises(NotImplementedError):
                self.circuit_atlas.depths()

        # TODO: resolve height/depth difference
        def test_mask_for_depth(self):
            with pyt.raises(NotImplementedError):
                self.circuit_atlas.mask_for_parameters(
                    {ABSOLUTE_DEPTH: (0, 25)})

        def test_absolute_heights(self):
            expheights = np.unique(self.atlas.load_data("distance").raw)
            expheights = expheights[np.isfinite(expheights)]
            npt.assert_array_equal(self.circuit_atlas.heights(), expheights)

        def test_mask_for_height(self):
            atlas_y = self.atlas.load_data("distance").raw
            posns = [(0, 25), (500, 700)]
            exp_masks = np.logical_and(
                np.any([np.logical_and(atlas_y >= p[0], atlas_y < p[1])
                        for p in posns], axis=0),
                self.atlas.load_data("brain_regions").raw != 0)

            npt.assert_array_equal(self.circuit_atlas.mask_for_parameters(
                {ABSOLUTE_HEIGHT: posns}),
                                   exp_masks)

    def test_gets_voxel_volume(self):
        circuit_atlas = CircuitAtlas(
            "/gpfs/bbp.cscs.ch/project/proj66/entities/dev/atlas/O1-152/")
        assert circuit_atlas.volume_voxel == 125.0
