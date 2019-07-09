import numpy as np
import numpy.testing as npt
import pytest as pyt
from voxcell.nexus.voxelbrain import Atlas
from neuro_dmt.models.bluebrain.atlas import compose_atlas_adapter


# TODO: test region X OR layer Y OR column Z
# TODO: test excludde xyz
# TODO: test mtype density
class Test_compose_atlas_adapter:

    class Test_NCX_O1:
        """
        test for NCX release O1 circuit
        TODO: replace with dummy atlas mimicking properties"""

        adapted = compose_atlas_adapter(
            "/gpfs/bbp.cscs.ch/project/proj66/entities/dev/atlas/O1-152/")
        atlas = Atlas.open(
            "/gpfs/bbp.cscs.ch/project/proj66/entities/dev/atlas/O1-152/")

        def test_mask_blank_query(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query({}),
                self.atlas.load_data("brain_regions").raw != 0)

        def test_warns_region(self):
            with pyt.warns(Warning):
                npt.assert_array_equal(
                    self.adapted.mask_for_query({'region': 'SSp'}),
                    self.atlas.load_data("brain_regions").raw != 0)

        def test_mask_layers(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query({'layer': 'L1'}),
                self.atlas.get_region_mask("L1").raw)

        def test_mask_multiple_layers(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query(
                    {'layer': ['L2', 'L5']}),
                np.logical_or(
                    self.atlas.get_region_mask("L2").raw,
                    self.atlas.get_region_mask("L5").raw))

        def test_mask_column(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query({'column': 'mc0'}),
                self.atlas.get_region_mask("mc0_Column").raw)

        def test_mask_three_columns(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query({'column':
                                             ['mc0', 'mc6', 'mc4']}),
                np.logical_or(
                    np.logical_or(
                        self.atlas.get_region_mask("mc0_Column").raw,
                        self.atlas.get_region_mask("mc6_Column").raw),
                    self.atlas.get_region_mask("mc4_Column").raw))

        def test_mask_column_layer(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query(
                    dict(column=['mc2'], layer=['L2', 'L3'])),
                np.logical_and(
                    self.atlas.get_region_mask('mc2_Column').raw,
                    np.logical_or(
                        self.atlas.get_region_mask("L2").raw,
                        self.atlas.get_region_mask("L3").raw)))

        def test_cell_density(self):
            with pyt.warns(Warning):
                assert np.isnan(self.adapted.cell_density({'layer': 'L4'}))

    class Test_Rat_2019_O1:
        """
        Test for SSCX dissemination O1 circuit
        TODO: replace with dummy atlas mimicing properties"""

        adapted = compose_atlas_adapter(
            "/gpfs/bbp.cscs.ch/project/proj64/"
            "dissemination/data/atlas/O1/MEAN/mean")
        atlas = Atlas.open(
            "/gpfs/bbp.cscs.ch/project/proj64/"
            "dissemination/data/atlas/O1/MEAN/mean")

        def test_mask_blank_query(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query({}),
                self.atlas.load_data("brain_regions").raw != 0)

        def test_warns_region(self):
            with pyt.warns(Warning):
                npt.assert_array_equal(
                    self.adapted.mask_for_query({'region': 'SSp'}),
                    self.atlas.load_data("brain_regions").raw != 0)

        def test_mask_layers(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query({'layer': 'L1'}),
                self.atlas.get_region_mask("@;1$").raw)

        def test_mask_multiple_layers(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query(
                    {'layer': ['L2', 'L5']}),
                np.logical_or(
                    self.atlas.get_region_mask("@;2$").raw,
                    self.atlas.get_region_mask("@;5$").raw))

        def test_mask_column(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query({'column': 'mc0'}),
                self.atlas.get_region_mask("mc0_Column").raw)

        def test_mask_three_columns(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query({'column':
                                             ['mc0', 'mc6', 'mc4']}),
                np.logical_or(
                    np.logical_or(
                        self.atlas.get_region_mask("mc0_Column").raw,
                        self.atlas.get_region_mask("mc6_Column").raw),
                    self.atlas.get_region_mask("mc4_Column").raw))

        def test_mask_column_layer(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query(
                    dict(column=['mc2'], layer=['L2', 'L3'])),
                np.logical_or(
                    self.atlas.get_region_mask('mc2;2').raw,
                    self.atlas.get_region_mask('mc2;3').raw))

        def test_cell_density(self):
            npt.assert_array_equal(
                self.adapted.cell_density({'layer': 'L5', 'column': 'mc2'}),
                (self.atlas.load_data("[cell_density]EXC").raw
                 + self.atlas.load_data("[cell_density]INH").raw)[
                     self.atlas.get_region_mask("mc2;5").raw])

        def test_sclass_density(self):
            npt.assert_array_equal(
                self.adapted.cell_density({'sclass': 'EXC'}),
                self.atlas.load_data("[cell_density]EXC").raw[
                    self.atlas.load_data("brain_regions").raw != 0]
                )
            npt.assert_array_equal(
                self.adapted.cell_density({'sclass': 'INH'}),
                self.atlas.load_data("[cell_density]INH").raw[
                    self.atlas.load_data("brain_regions").raw != 0]
                )

        def test_mtype_density(self):
            npt.assert_array_equal(
                self.adapted.cell_density(
                    {'mtype': 'MC', 'layer': ['L2', 'L3']}),
                self.atlas.load_data("[cell_density]L23_MC").raw[
                    self.atlas.get_region_mask('@;2$|;3$').raw])

    class Test_Rat_2018_O1:
        """
        test for rebuilt 2018 rat atlas
        TODO: replace with dummy atlas mimicking properties
        """

        adapted = compose_atlas_adapter(
            "/gpfs/bbp.cscs.ch/project/proj64/entities/dev/atlas/"
            "fixed_77831ACA-6198-4AA0-82EF-D0475A4E0647_01-06-2018")
        atlas = Atlas.open(
            "/gpfs/bbp.cscs.ch/project/proj64/entities/dev/atlas/"
            "fixed_77831ACA-6198-4AA0-82EF-D0475A4E0647_01-06-2018")

        def test_mask_blank_query(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query({}),
                self.atlas.load_data("brain_regions").raw != 0)

        def test_warns_region(self):
            with pyt.warns(Warning):
                npt.assert_array_equal(
                    self.adapted.mask_for_query({'region': 'SSp'}),
                    self.atlas.load_data("brain_regions").raw != 0)

        def test_mask_layers(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query({'layer': 'L1'}),
                self.atlas.get_region_mask("L1").raw)

        def test_mask_multiple_layers(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query(
                    {'layer': ['L2', 'L5']}),
                np.logical_or(
                    self.atlas.get_region_mask("L2").raw,
                    self.atlas.get_region_mask("L5").raw))

        def test_mask_column(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query({'column': 'mc0'}),
                self.atlas.get_region_mask("mc0_Column").raw)

        def test_mask_three_columns(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query({'column':
                                             ['mc0', 'mc6', 'mc4']}),
                np.logical_or(
                    np.logical_or(
                        self.atlas.get_region_mask("mc0_Column").raw,
                        self.atlas.get_region_mask("mc6_Column").raw),
                    self.atlas.get_region_mask("mc4_Column").raw))

        def test_mask_column_layer(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query(
                    dict(column=['mc2'], layer=['L2', 'L3'])),
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
                self.adapted.cell_density({'layer': 'L5', 'column': 'mc2'}),
                np.sum([self.atlas.load_data(mtype).raw
                        for mtype in atlasmtypenames],
                       axis=0)[
                           np.logical_and(
                               self.atlas.get_region_mask("mc2_Column").raw,
                               self.atlas.get_region_mask("L5").raw)])

        def test_sclass_density(self):
            with pyt.warns(Warning):
                assert np.isnan(self.adapted.cell_density({'sclass': 'EXC'}))

        def test_mtype_density(self):
            npt.assert_array_equal(
                self.adapted.cell_density(
                    {'mtype': 'NGC-DA', 'layer': ['L5', 'L1']}),
                self.atlas.load_data("NGC-DA").raw[
                    self.atlas.get_region_mask('@L5$|L1$').raw])

    class Test_hippocampus:
        """
        test for O1 hippocampus atlas
        TODO: replace with dummy atlas mimicing properties"""

        adapted = compose_atlas_adapter(
            "/gpfs/bbp.cscs.ch/project/proj42/entities/dev/atlas/"
            "20190625-CA3-O1-atlas/")
        atlas = Atlas.open(
            "/gpfs/bbp.cscs.ch/project/proj42/entities/dev/atlas/"
            "20190625-CA3-O1-atlas/")

        def test_mask_blank_query(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query({}),
                self.atlas.load_data("brain_regions").raw != 0)

        def test_warns_region(self):
            with pyt.warns(Warning):
                npt.assert_array_equal(
                    self.adapted.mask_for_query({'region': 'SSp'}),
                    self.atlas.load_data("brain_regions").raw != 0)

        def test_mask_layers(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query({'layer': 'SP'}),
                self.atlas.get_region_mask("@;SP$").raw)

        def test_mask_multiple_layers(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query(
                    {'layer': ['SO', 'SLM']}),
                np.logical_or(
                    self.atlas.get_region_mask("@;SO$").raw,
                    self.atlas.get_region_mask("@;SLM$").raw))

        def test_mask_column(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query({'column': 'mc0'}),
                self.atlas.get_region_mask("mc0_Column").raw)

        def test_mask_three_columns(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query({'column':
                                             ['mc0', 'mc6', 'mc4']}),
                np.logical_or(
                    np.logical_or(
                        self.atlas.get_region_mask("mc0_Column").raw,
                        self.atlas.get_region_mask("mc6_Column").raw),
                    self.atlas.get_region_mask("mc4_Column").raw))

        def test_mask_column_layer(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query(
                    dict(column=['mc2'], layer=['SO', 'SR'])),
                np.logical_and(
                    self.atlas.get_region_mask('mc2_Column').raw,
                    np.logical_or(
                        self.atlas.get_region_mask("@;SO$").raw,
                        self.atlas.get_region_mask("@;SR$").raw)))

        def test_cell_density(self):
            with pyt.warns(Warning):
                assert np.isnan(self.adapted.cell_density({'layer': 'L4'}))


    class Test_Rat_2018_O1:
        """
        test for rebuilt 2018 rat atlas
        TODO: replace with dummy atlas mimicing properties"""

        adapted = compose_atlas_adapter(
            "/gpfs/bbp.cscs.ch/project/proj64/entities/dev/atlas/"
            "fixed_77831ACA-6198-4AA0-82EF-D0475A4E0647_01-06-2018")
        atlas = Atlas.open(
            "/gpfs/bbp.cscs.ch/project/proj64/entities/dev/atlas/"
            "fixed_77831ACA-6198-4AA0-82EF-D0475A4E0647_01-06-2018")

        def test_mask_blank_query(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query({}),
                self.atlas.load_data("brain_regions").raw != 0)

        def test_warns_region(self):
            with pyt.warns(Warning):
                npt.assert_array_equal(
                    self.adapted.mask_for_query({'region': 'SSp'}),
                    self.atlas.load_data("brain_regions").raw != 0)

        def test_mask_layers(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query({'layer': 'L1'}),
                self.atlas.get_region_mask("L1").raw)

        def test_mask_multiple_layers(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query(
                    {'layer': ['L2', 'L5']}),
                np.logical_or(
                    self.atlas.get_region_mask("L2").raw,
                    self.atlas.get_region_mask("L5").raw))

        def test_mask_column(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query({'column': 'mc0'}),
                self.atlas.get_region_mask("mc0_Column").raw)

        def test_mask_three_columns(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query({'column':
                                             ['mc0', 'mc6', 'mc4']}),
                np.logical_or(
                    np.logical_or(
                        self.atlas.get_region_mask("mc0_Column").raw,
                        self.atlas.get_region_mask("mc6_Column").raw),
                    self.atlas.get_region_mask("mc4_Column").raw))

        def test_mask_column_layer(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query(
                    dict(column=['mc2'], layer=['L2', 'L3'])),
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
                self.adapted.cell_density({'layer': 'L5', 'column': 'mc2'}),
                np.sum([self.atlas.load_data(mtype).raw
                        for mtype in atlasmtypenames],
                       axis=0)[
                           np.logical_and(
                               self.atlas.get_region_mask("mc2_Column").raw,
                               self.atlas.get_region_mask("L5").raw)])

        def test_sclass_density(self):
            with pyt.warns(Warning):
                assert np.isnan(self.adapted.cell_density({'sclass': 'EXC'}))

        def test_mtype_density(self):
            npt.assert_array_equal(
                self.adapted.cell_density(
                    {'mtype': 'NGC-DA', 'layer': ['L5', 'L1']}),
                self.atlas.load_data("NGC-DA").raw[
                    self.atlas.get_region_mask('@L5$|L1$').raw])

    class Test_BBA:
        """
        test for the AllenAtlas based BlueBrainAtlas
        TODO: replace with dummy atlas mimicing properties"""

        adapted = compose_atlas_adapter(
            "/gpfs/bbp.cscs.ch/project/proj68/entities/"
            "dev/atlas/ccf_2017-50um/20181114")
        atlas = Atlas.open(
            "/gpfs/bbp.cscs.ch/project/proj68/entities/"
            "dev/atlas/ccf_2017-50um/20181114")

        def test_mask_blank_query(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query({}),
                self.atlas.load_data("brain_regions").raw != 0)

        def test_region_mask(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query({'region': 'SSp'}),
                self.atlas.get_region_mask("SSp").raw)

        def test_mask_layers(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query({'layer': 'L2'}),
                self.atlas.get_region_mask("@.*2$").raw)

        def test_mask_multiple_layers(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query(
                    {'layer': ['SO', 'L4']}),
                np.logical_or(
                    np.logical_and(
                        self.atlas.get_region_mask("@.*so$").raw,
                        self.atlas.get_region_mask("CA")),
                    self.atlas.get_region_mask("@.*4$").raw))

        def test_warns_column(self):
            with pyt.warns(Warning):
                npt.assert_array_equal(
                    self.adapted.mask_for_query({'column': 'mc2'}),
                    self.atlas.load_data("brain_regions").raw != 0)

        def test_mask_region_layer(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query(
                    dict(region="SSp-ll", layer=['L1', 'L4'])),
                np.logical_or(
                    self.atlas.get_region_mask("SSp-ll1").raw,
                    self.atlas.get_region_mask("SSp-ll4").raw))

        def test_cell_density(self):
            npt.assert_array_equal(
                self.adapted.cell_density({"region": "RT"}),
                np.sum([
                    self.atlas.load_data("[cell_density]{}".format(sc)).raw
                    for sc in ("EXC", "INH")], axis=0)[
                            self.atlas.get_region_mask("RT").raw])

        def test_mtype_density(self):
            npt.assert_array_equal(
                self.adapted.cell_density({
                    "mtype": "IPC",
                    "region": "MOp"}),
                np.nansum([self.atlas.load_data(
                    "[cell_density]L2_IPC").raw,
                           self.atlas.load_data(
                               "[cell_density]L6_IPC").raw],
                          axis=0)[
                              self.atlas.get_region_mask("MOp").raw])
