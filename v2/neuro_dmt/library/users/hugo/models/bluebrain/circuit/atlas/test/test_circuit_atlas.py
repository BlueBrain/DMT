"""
Test `CircuitAltas`
"""

import os
import numpy as np
import numpy.testing as npt
import pytest as pyt
from voxcell.nexus.voxelbrain import Atlas
from neuro_dmt.models.bluebrain.circuit.atlas import CircuitAtlas
from neuro_dmt.terminology import neuroscience


# TODO: test region X OR layer Y OR column Z
# TODO: test excludde xyz
# TODO: group tests differently, group by capability and bring in atlases
#       representing cases of each capability

class Test_CircuitAtlas:

    class Test_NCX_O1:
        """
        test for NCX release O1 circuit
        TODO: replace with dummy atlas mimicking properties
        """
        path_atlas =\
            "/gpfs/bbp.cscs.ch/project/proj66/"\
            "entities/dev/atlas/O1-152/"

        circuit_atlas =\
            CircuitAtlas(path_atlas)

        atlas = Atlas.open(path_atlas)

        def test_mask_blank_parameters(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(**{}),
                self.atlas.load_data("brain_regions").raw != 0)

        def test_warns_region(self):
            with pyt.warns(Warning):
                npt.assert_array_equal(
                    self.circuit_atlas.get_mask(**{neuroscience.region: 'SSp'}),
                    self.atlas.load_data("brain_regions").raw != 0)

        def test_mask_layers(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(**{neuroscience.layer: 'L1'}),
                self.atlas.get_region_mask("L1").raw)

        def test_mask_multiple_layers(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(
                    **{neuroscience.layer: ['L2', 'L5']}),
                np.logical_or(
                    self.atlas.get_region_mask("L2").raw,
                    self.atlas.get_region_mask("L5").raw))

        def test_mask_column(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(**{neuroscience.mesocolumn: 'mc0'}),
                self.atlas.get_region_mask("mc0_Column").raw)

        def test_mask_three_columns(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(**{neuroscience.mesocolumn:
                                             ['mc0', 'mc6', 'mc4']}),
                np.logical_or(
                    np.logical_or(
                        self.atlas.get_region_mask("mc0_Column").raw,
                        self.atlas.get_region_mask("mc6_Column").raw),
                    self.atlas.get_region_mask("mc4_Column").raw))

        def test_mask_column_layer(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(
                    **{neuroscience.mesocolumn: ['mc2'],
                       neuroscience.layer: ['L2', 'L3']}),
                np.logical_and(
                    self.atlas.get_region_mask('mc2_Column').raw,
                    np.logical_or(
                        self.atlas.get_region_mask("L2").raw,
                        self.atlas.get_region_mask("L3").raw)))

        def test_cell_density(self):
            with pyt.warns(Warning):
                assert np.isnan(self.circuit_atlas.cell_density(
                    **{neuroscience.layer: 'L4'}))

    class Test_Rat_2019_O1:
        """
        Test for SSCX dissemination O1 circuit
        TODO: replace with dummy atlas mimicing properties"""
        path_atlas = "/gpfs/bbp.cscs.ch/project/proj64/"\
                     "dissemination/data/atlas/O1/MEAN/mean"
        circuit_atlas = CircuitAtlas(path_atlas)
        atlas = Atlas.open(
            "/gpfs/bbp.cscs.ch/project/proj64/"
            "dissemination/data/atlas/O1/MEAN/mean")

        def test_mask_blank_parameters(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(),
                self.atlas.load_data("brain_regions").raw != 0)

        def test_warns_region(self):
            with pyt.warns(Warning):
                npt.assert_array_equal(
                    self.circuit_atlas.get_mask(**{neuroscience.region: 'SSp'}),
                    self.atlas.load_data("brain_regions").raw != 0)

        def test_mask_layers(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(**{neuroscience.layer: 'L1'}),
                self.atlas.get_region_mask("@;1$").raw)

        def test_mask_multiple_layers(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(
                    **{neuroscience.layer: ['L2', 'L5']}),
                np.logical_or(
                    self.atlas.get_region_mask("@;2$").raw,
                    self.atlas.get_region_mask("@;5$").raw))

        def test_mask_column(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(**{neuroscience.mesocolumn: 'mc0'}),
                self.atlas.get_region_mask("mc0_Column").raw)

        def test_mask_three_columns(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(**{neuroscience.mesocolumn:
                                             ['mc0', 'mc6', 'mc4']}),
                np.logical_or(
                    np.logical_or(
                        self.atlas.get_region_mask("mc0_Column").raw,
                        self.atlas.get_region_mask("mc6_Column").raw),
                    self.atlas.get_region_mask("mc4_Column").raw))

        def test_mask_column_layer(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(
                    **{neuroscience.mesocolumn: ['mc2'],
                       neuroscience.layer: ['L2', 'L3']}),
                np.logical_or(
                    self.atlas.get_region_mask('mc2;2').raw,
                    self.atlas.get_region_mask('mc2;3').raw))

        def test_cell_density(self):
            npt.assert_array_equal(
                self.circuit_atlas.cell_density(**{neuroscience.layer: 'L5',
                                                   neuroscience.mesocolumn: 'mc2'}),
                np.mean((self.atlas.load_data("[cell_density]EXC").raw
                         + self.atlas.load_data("[cell_density]INH").raw)[
                             self.atlas.get_region_mask("mc2;5").raw]))

        def test_sclass_density(self):
            npt.assert_array_equal(
                self.circuit_atlas.cell_density(**{neuroscience.synapse_class: 'EXC'}),
                np.mean(self.atlas.load_data("[cell_density]EXC").raw[
                    self.atlas.load_data("brain_regions").raw != 0]
                ))
            npt.assert_array_equal(
                self.circuit_atlas.cell_density(**{neuroscience.synapse_class: 'INH'}),
                np.mean(self.atlas.load_data("[cell_density]INH").raw[
                    self.atlas.load_data("brain_regions").raw != 0]
                ))

        def test_mtype_density(self):
            npt.assert_array_equal(
                self.circuit_atlas.cell_density(
                    **{neuroscience.morphology_subclass: 'MC', neuroscience.layer: ['L2', 'L3']}),
                np.mean(self.atlas.load_data("[cell_density]L23_MC").raw[
                    self.atlas.get_region_mask('@;2$|;3$').raw]))

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
                self.circuit_atlas.get_mask(),
                self.atlas.load_data("brain_regions").raw != 0)

        def test_warns_region(self):
            with pyt.warns(Warning):
                npt.assert_array_equal(
                    self.circuit_atlas.get_mask(**{neuroscience.region: 'SSp'}),
                    self.atlas.load_data("brain_regions").raw != 0)

        def test_mask_layers(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(**{neuroscience.layer: 'L1'}),
                self.atlas.get_region_mask("L1").raw)

        def test_mask_multiple_layers(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(
                    **{neuroscience.layer: ['L2', 'L5']}),
                np.logical_or(
                    self.atlas.get_region_mask("L2").raw,
                    self.atlas.get_region_mask("L5").raw))

        def test_mask_column(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(**{neuroscience.mesocolumn: 'mc0'}),
                self.atlas.get_region_mask("mc0_Column").raw)

        def test_mask_three_columns(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(**{neuroscience.mesocolumn:
                                             ['mc0', 'mc6', 'mc4']}),
                np.logical_or(
                    np.logical_or(
                        self.atlas.get_region_mask("mc0_Column").raw,
                        self.atlas.get_region_mask("mc6_Column").raw),
                    self.atlas.get_region_mask("mc4_Column").raw))

        def test_mask_column_layer(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(
                    **{neuroscience.mesocolumn: ['mc2'], neuroscience.layer: ['L2', 'L3']}),
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
                self.circuit_atlas.cell_density(**{neuroscience.layer: 'L5', neuroscience.mesocolumn: 'mc2'}),
                np.mean(np.sum([self.atlas.load_data(mtype).raw
                                for mtype in atlasmtypenames],
                               axis=0)[
                                   np.logical_and(
                                       self.atlas.get_region_mask("mc2_Column").raw,
                                       self.atlas.get_region_mask("L5").raw)]))

        def test_sclass_density(self):
            with pyt.warns(Warning):
                assert np.isnan(self.circuit_atlas.cell_density(**{neuroscience.synapse_class: 'EXC'}))

        def test_mtype_density(self):
            npt.assert_array_equal(
                self.circuit_atlas.cell_density(
                    **{neuroscience.morphology_subclass: 'NGC-DA', neuroscience.layer: ['L5', 'L1']}),
                np.mean(self.atlas.load_data("NGC-DA").raw[
                    self.atlas.get_region_mask('@L5$|L1$').raw]))

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
                self.circuit_atlas.get_mask(**{}),
                self.atlas.load_data("brain_regions").raw != 0)

        def test_warns_region(self):
            with pyt.warns(Warning):
                npt.assert_array_equal(
                    self.circuit_atlas.get_mask(**{neuroscience.region: 'SSp'}),
                    self.atlas.load_data("brain_regions").raw != 0)

        def test_mask_layers(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(**{neuroscience.layer: 'SP'}),
                self.atlas.get_region_mask("@;SP$").raw)

        def test_mask_multiple_layers(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(
                    **{neuroscience.layer: ['SO', 'SLM']}),
                np.logical_or(
                    self.atlas.get_region_mask("@;SO$").raw,
                    self.atlas.get_region_mask("@;SLM$").raw))

        def test_mask_column(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(**{neuroscience.mesocolumn: 'mc0'}),
                self.atlas.get_region_mask("mc0_Column").raw)

        def test_mask_three_columns(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(**{neuroscience.mesocolumn:
                                             ['mc0', 'mc6', 'mc4']}),
                np.logical_or(
                    np.logical_or(
                        self.atlas.get_region_mask("mc0_Column").raw,
                        self.atlas.get_region_mask("mc6_Column").raw),
                    self.atlas.get_region_mask("mc4_Column").raw))

        def test_mask_column_layer(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(
                    **{neuroscience.mesocolumn: ['mc2'], neuroscience.layer: ['SO', 'SR']}),
                np.logical_and(
                    self.atlas.get_region_mask('mc2_Column').raw,
                    np.logical_or(
                        self.atlas.get_region_mask("@;SO$").raw,
                        self.atlas.get_region_mask("@;SR$").raw)))

        def test_cell_density(self):
            with pyt.warns(Warning):
                assert np.isnan(self.circuit_atlas.cell_density(**{neuroscience.layer: 'L4'}))

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
                self.circuit_atlas.get_mask(**{}),
                self.atlas.load_data("brain_regions").raw != 0)

        def test_region_mask(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(**{neuroscience.region: 'SSp'}),
                self.atlas.get_region_mask("SSp").raw)

        def test_mask_layers(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(**{neuroscience.layer: 'L2'}),
                self.atlas.get_region_mask("@.*2$").raw)

        def test_mask_multiple_layers(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(
                    **{neuroscience.layer: ['SO', 'L4']}),
                np.logical_or(
                    np.logical_and(
                        self.atlas.get_region_mask("@.*so$").raw,
                        self.atlas.get_region_mask("CA")),
                    self.atlas.get_region_mask("@.*4$").raw))

        def test_warns_column(self):
            with pyt.warns(Warning):
                npt.assert_array_equal(
                    self.circuit_atlas.get_mask(**{neuroscience.mesocolumn: 'mc2'}),
                    self.atlas.load_data("brain_regions").raw != 0)

        def test_mask_region_layer(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(
                    **{neuroscience.region: "SSp-ll", neuroscience.layer: ['L1', 'L4']}),
                np.logical_or(
                    self.atlas.get_region_mask("SSp-ll1").raw,
                    self.atlas.get_region_mask("SSp-ll4").raw))

        def test_cell_density(self):
            npt.assert_array_equal(
                self.circuit_atlas.cell_density(**{neuroscience.region: "RT"}),
                np.sum([
                    self.atlas.load_data("[cell_density]{}".format(sc)).raw
                    for sc in ("EXC", "INH")], axis=0)[
                            self.atlas.get_region_mask("RT").raw])

        def test_mtype_density(self):
            npt.assert_array_equal(
                self.circuit_atlas.cell_density(**{
                    neuroscience.morphology_subclass: "IPC",
                    neuroscience.region: "MOp"}),
                np.mean(np.nansum([self.atlas.load_data(
                    "[cell_density]L2_IPC").raw,
                                   self.atlas.load_data(
                                       "[cell_density]L6_IPC").raw],
                                  axis=0)[
                                      self.atlas.get_region_mask("MOp").raw]))

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

            npt.assert_array_equal(self.circuit_atlas.get_mask(
                **{neuroscience.depth: posns}),
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

            npt.assert_array_equal(self.circuit_atlas.get_mask(
                **{neuroscience.height: posns}),
                                   exp_masks)

    # TODO: test behavior when provided PW-style brain region
    class Test_2019_S1:
        """
        test for paxinos-watson based S1 atlas of somatosensory cortex
        TODO: replace with dummy atlas mimicing properties"""

        circuit_atlas = CircuitAtlas(
            "/gpfs/bbp.cscs.ch/project/proj64/dissemination/data/atlas/"
            "S1/MEAN/juvenile_L23_MC_BTC_shifted_down/Bio_M")
        atlas = Atlas.open(
            "/gpfs/bbp.cscs.ch/project/proj64/dissemination/data/atlas/"
            "S1/MEAN/juvenile_L23_MC_BTC_shifted_down/Bio_M")

        def test_region_mask(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(**{neuroscience.region: 'SSp'}),
                self.atlas.get_region_mask("S1").raw)

        def test_mask_multiple_layers(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(
                    **{neuroscience.layer: ['L1', 'L4']}),
                np.logical_or(
                    self.atlas.get_region_mask("@L1").raw,
                    self.atlas.get_region_mask("@L4").raw))

        def test_warns_column(self):
            with pyt.warns(Warning):
                npt.assert_array_equal(
                    self.circuit_atlas.get_mask(**{neuroscience.mesocolumn: 'mc2'}),
                    self.atlas.load_data("brain_regions").raw != 0)

        def test_mask_region_layer(self):
            npt.assert_array_equal(
                self.circuit_atlas.get_mask(
                    **{neuroscience.region: "SSp-ll", neuroscience.layer: ['L1', 'L4']}),
                np.logical_and(
                    self.atlas.get_region_mask("S1HL").raw,
                    np.logical_or(
                        self.atlas.get_region_mask("@L1").raw,
                        self.atlas.get_region_mask("@L4").raw)))

        def test_cell_density(self):
            npt.assert_array_equal(
                self.circuit_atlas.cell_density(**{neuroscience.region: "SSp-m"}),
                np.mean(np.nansum([
                    self.atlas.load_data("[cell_density]{}".format(sc)).raw
                    for sc in ("EXC", "INH")], axis=0)[
                            self.atlas.get_region_mask("S1J").raw]))

        def test_msubclass_density(self):
            npt.assert_array_equal(
                self.circuit_atlas.cell_density(**{
                    neuroscience.morphology_subclass: "IPC",
                    neuroscience.region: "SS"}),
                np.mean(np.nansum([self.atlas.load_data(
                    "[cell_density]L2_IPC").raw,
                                   self.atlas.load_data(
                                       "[cell_density]L6_IPC").raw],
                                  axis=0)[
                                      self.atlas.get_region_mask("SSCtx").raw]))

        def test_mtype_density(self):
            npt.assert_array_equal(
                self.circuit_atlas.cell_density(**{
                    neuroscience.mtype: "L2_IPC",
                    neuroscience.region: "SSp-ll"}),
                np.mean(self.atlas.load_data("[cell_density]L2_IPC").raw[
                    self.atlas.get_region_mask("S1HL").raw]))

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
                self.circuit_atlas.get_mask(
                    **{neuroscience.depth: (0, 25)})

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
            npt.assert_array_equal(self.circuit_atlas.get_mask(
                **{neuroscience.height: posns}),
                                   exp_masks)

        def test_mask_for_single_height(self):
            atlas_y = self.atlas.load_data("distance").raw
            posn = (0, 25)
            exp_masks = np.logical_and(
                np.logical_and(atlas_y >= posn[0], atlas_y < posn[1]),
                self.atlas.load_data("brain_regions").raw != 0)
            npt.assert_array_equal(self.circuit_atlas.get_mask(
                **{neuroscience.height: posn}),
                                   exp_masks)

    def test_gets_voxel_volume(self):
        circuit_atlas = CircuitAtlas(
            "/gpfs/bbp.cscs.ch/project/proj66/entities/dev/atlas/O1-152/")
        assert circuit_atlas.voxel_volume == 125.0


def test_accepts_tuples():
    path_atlas = "/gpfs/bbp.cscs.ch/project/proj66/"\
                 "entities/dev/atlas/O1-152/"
    circuit_atlas = CircuitAtlas(path_atlas)
    atlas = Atlas.open(path_atlas)

    npt.assert_equal(circuit_atlas.get_mask(**{neuroscience.layer:
                                               ('L1', 'L2')}),
                     atlas.get_region_mask("@L1|L2").raw)
