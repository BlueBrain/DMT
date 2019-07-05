import numpy as np
import numpy.testing as npt
import pytest as pyt
from voxcell.nexus.voxelbrain import Atlas
from neuro_dmt.models.bluebrain.atlas import compose_atlas_adapter


# TODO: test region X OR layer Y OR column Z
class Test_compose_atlas_adapter:

    class Test_NCX_O1:
        """
        test for NCX release O1 circuit
        TODO: replace with dummy atlas mimicing properties"""

        adapted = compose_atlas_adapter(
            "/gpfs/bbp.cscs.ch/project/proj66/entities/dev/atlas/O1-152/")
        atlas = Atlas.open(
            "/gpfs/bbp.cscs.ch/project/proj66/entities/dev/atlas/O1-152/")

        def test_mask_blank_query(self):
            npt.assert_array_equal(
                self.adapted.mask_for_query({}),
                self.atlas.load_data("brain_regions").raw != 0)

        def test_warns_region(self):
            pyt.warns(Warning, self.adapted.mask_for_query, {'region': 'SSp'})
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
            pyt.warns(Warning,
                      self.adapted.cell_density, {'layer': 'L4'})
            assert np.isnan(self.adapted.cell_density({'layer': 'L4'}))
