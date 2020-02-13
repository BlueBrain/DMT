import numpy as np
import pytest as pyt
import bluepy.v2 as bp
import numpy.testing as npt
import pandas.testing as pdt
from neuro_dmt.terminology import neuroscience
from neuro_dmt.models.bluebrain.circuit.model import CircuitModel


class TestOnNCXO1:
    """test the CircuitModel on O1 from neocortex release"""

    circuit_config = "/gpfs/bbp.cscs.ch/project/proj68/circuits/"\
                     "O1/20190307/CircuitConfig"
    circuit = bp.Circuit(circuit_config)
    adapted = CircuitModel(circuit_config)

    def test_cell_density(self):
        test_cells = self.circuit.cells.get().shape[0]
        test_mask = self.circuit.atlas.get_region_mask("O1")
        test_vol = np.sum(test_mask.raw) * test_mask.voxel_volume * 1e-9
        dens = test_cells / test_vol
        assert self.adapted.cell_density(**{}) == pyt.approx(dens)

    def test_cd_by_layer_mtype_column(self):
        test_cells = self.circuit.cells.get(
            {bp.Cell.LAYER: [1, 3, 6],
             bp.Cell.MTYPE: ['L23_MC', "L6_MC"],
             bp.Cell.REGION: ['mc2_Column']}).shape[0]
        print(test_cells)
        col_mask = self.circuit.atlas.get_region_mask("mc2_Column")
        test_mask = np.logical_and(
            col_mask.raw,
            self.circuit.atlas.get_region_mask("@L[136]$").raw)
        test_vol = np.sum(test_mask) * col_mask.voxel_volume * 1e-9
        print(test_vol)
        dens = test_cells / test_vol
        assert self.adapted.cell_density(
            **{neuroscience.layer: ['L1', 'L3', 'L6'],
               neuroscience.morphology_subclass: 'MC',
               neuroscience.mesocolumn: 'mc2'}) == pyt.approx(dens)

    def test_translate_parameters(self):
        allmc = [mc for mc in sorted(self.circuit.cells.mtypes)
                 if mc.endswith("MC")]
        allipc = [ipc for ipc in sorted(self.circuit.cells.mtypes)
                  if ipc.endswith("IPC")]
        assert self.adapted._translate_parameters_cells(
            {neuroscience.synapse_class: ['EXC', 'INH'],
             neuroscience.morphology_class: ['PYR', 'INT'],
             neuroscience.mesocolumn: ['mc2', 'mc3', 'mc0'],
             neuroscience.morphology_subclass: ['MC', 'IPC'],
             neuroscience.layer: ['L1', 'L4', 'L6', 'L2']}) ==\
             {bp.Cell.SYNAPSE_CLASS: ['EXC', 'INH'],
              bp.Cell.MORPH_CLASS: ['PYR', 'INT'],
              bp.Cell.REGION: ['mc2_Column', 'mc3_Column', 'mc0_Column'],
              bp.Cell.LAYER: [1, 4, 6, 2],
              bp.Cell.MTYPE: allmc + allipc}

    def test_empty_lists(self):
        assert self.adapted._translate_parameters_cells(
            {neuroscience.synapse_class: [],
             neuroscience.morphology_class: [], neuroscience.mesocolumn: [],
             neuroscience.mtype: [], neuroscience.layer: []}) == {}

    def test_mtypes(self):
        assert self.adapted.mtypes() == [
            {neuroscience.layer: 'L1', neuroscience.mtype: 'L1_DAC', neuroscience.morphology_subclass: 'DAC'},
            {neuroscience.layer: 'L1', neuroscience.mtype: 'L1_HAC', neuroscience.morphology_subclass: 'HAC'},
            {neuroscience.layer: 'L1', neuroscience.mtype: 'L1_LAC', neuroscience.morphology_subclass: 'LAC'},
            {neuroscience.layer: 'L1', neuroscience.mtype: 'L1_NGC-DA', neuroscience.morphology_subclass: 'NGC-DA'},
            {neuroscience.layer: 'L1', neuroscience.mtype: 'L1_NGC-SA', neuroscience.morphology_subclass: 'NGC-SA'},
            {neuroscience.layer: 'L1', neuroscience.mtype: 'L1_SAC', neuroscience.morphology_subclass: 'SAC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_BP', neuroscience.morphology_subclass: 'BP'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_BTC', neuroscience.morphology_subclass: 'BTC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_CHC', neuroscience.morphology_subclass: 'CHC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_DBC', neuroscience.morphology_subclass: 'DBC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_LBC', neuroscience.morphology_subclass: 'LBC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_MC', neuroscience.morphology_subclass: 'MC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_NBC', neuroscience.morphology_subclass: 'NBC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_NGC', neuroscience.morphology_subclass: 'NGC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_SBC', neuroscience.morphology_subclass: 'SBC'},
            {neuroscience.layer: 'L2', neuroscience.mtype: 'L2_IPC', neuroscience.morphology_subclass: 'IPC'},
            {neuroscience.layer: 'L2', neuroscience.mtype: 'L2_TPC:A', neuroscience.morphology_subclass: 'TPC:A'},
            {neuroscience.layer: 'L2', neuroscience.mtype: 'L2_TPC:B', neuroscience.morphology_subclass: 'TPC:B'},
            {neuroscience.layer: 'L3', neuroscience.mtype: 'L3_TPC:A', neuroscience.morphology_subclass: 'TPC:A'},
            {neuroscience.layer: 'L3', neuroscience.mtype: 'L3_TPC:B', neuroscience.morphology_subclass: 'TPC:B'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_BP', neuroscience.morphology_subclass: 'BP'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_BTC', neuroscience.morphology_subclass: 'BTC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_CHC', neuroscience.morphology_subclass: 'CHC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_DBC', neuroscience.morphology_subclass: 'DBC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_LBC', neuroscience.morphology_subclass: 'LBC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_MC', neuroscience.morphology_subclass: 'MC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_NBC', neuroscience.morphology_subclass: 'NBC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_NGC', neuroscience.morphology_subclass: 'NGC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_SBC', neuroscience.morphology_subclass: 'SBC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_SSC', neuroscience.morphology_subclass: 'SSC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_TPC', neuroscience.morphology_subclass: 'TPC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_UPC', neuroscience.morphology_subclass: 'UPC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_BP', neuroscience.morphology_subclass: 'BP'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_BTC', neuroscience.morphology_subclass: 'BTC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_CHC', neuroscience.morphology_subclass: 'CHC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_DBC', neuroscience.morphology_subclass: 'DBC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_LBC', neuroscience.morphology_subclass: 'LBC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_MC', neuroscience.morphology_subclass: 'MC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_NBC', neuroscience.morphology_subclass: 'NBC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_NGC', neuroscience.morphology_subclass: 'NGC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_SBC', neuroscience.morphology_subclass: 'SBC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_TPC:A', neuroscience.morphology_subclass: 'TPC:A'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_TPC:B', neuroscience.morphology_subclass: 'TPC:B'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_TPC:C', neuroscience.morphology_subclass: 'TPC:C'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_UPC', neuroscience.morphology_subclass: 'UPC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_BP', neuroscience.morphology_subclass: 'BP'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_BPC', neuroscience.morphology_subclass: 'BPC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_BTC', neuroscience.morphology_subclass: 'BTC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_CHC', neuroscience.morphology_subclass: 'CHC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_DBC', neuroscience.morphology_subclass: 'DBC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_HPC', neuroscience.morphology_subclass: 'HPC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_IPC', neuroscience.morphology_subclass: 'IPC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_LBC', neuroscience.morphology_subclass: 'LBC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_MC', neuroscience.morphology_subclass: 'MC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_NBC', neuroscience.morphology_subclass: 'NBC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_NGC', neuroscience.morphology_subclass: 'NGC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_SBC', neuroscience.morphology_subclass: 'SBC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_TPC:A', neuroscience.morphology_subclass: 'TPC:A'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_TPC:C', neuroscience.morphology_subclass: 'TPC:C'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_UPC', neuroscience.morphology_subclass: 'UPC'}]

    def test_warns_region(self):
        with pyt.warns(Warning):
            self.adapted.cell_density(**{neuroscience.region: 'SSp'})
        pass


class TestOnNCXIsocortex:
    """test the CircuitModel on Isocortex release"""

    circuit_config = "/gpfs/bbp.cscs.ch/project/proj68/circuits/"\
                     "Isocortex/20190307/CircuitConfig"
    circuit = bp.Circuit(circuit_config)
    adapted = CircuitModel(circuit_config)

    def test_cell_density(self):
        test_cells = self.circuit.cells.get().shape[0]
        test_mask = self.circuit.atlas.get_region_mask("Isocortex")
        test_vol = np.sum(test_mask.raw) * test_mask.voxel_volume * 1e-9
        dens = test_cells / test_vol
        assert self.adapted.cell_density(**{}) == pyt.approx(dens)

    def test_cd_by_layer_mtype_region(self):
        test_cells = self.circuit.cells.get(
            {bp.Cell.LAYER: [1, 3, 6],
             bp.Cell.MTYPE: ['L23_MC', "L6_MC"],
             bp.Cell.REGION: ['SSp-ll@left', 'SSp-ll@right']}).shape[0]
        test_mask = self.circuit.atlas.get_region_mask("@SSp-ll[136]$")
        test_vol = np.sum(test_mask.raw) * test_mask.voxel_volume * 1e-9
        dens = test_cells / test_vol
        assert self.adapted.cell_density(
            **{neuroscience.layer: ['L1', 'L3', 'L6'],
               neuroscience.mtype: ['L23_MC', 'L6_MC'],
               neuroscience.region: 'SSp-ll'}) == pyt.approx(dens)

    def test_translate_parameters(self):
        allmc = [mc for mc in sorted(self.circuit.cells.mtypes)
                 if mc.endswith("MC")]
        allipc = [ipc for ipc in sorted(self.circuit.cells.mtypes)
                  if ipc.endswith("IPC")]
        assert self.adapted._translate_parameters_cells(
            {neuroscience.synapse_class: ['EXC', 'INH'],
             neuroscience.morphology_class: ['PYR', 'INT'],
             neuroscience.region: ['GU', 'VISa', 'MOp'],
             neuroscience.morphology_subclass: ['MC', 'IPC'],
             neuroscience.layer: ['L1', 'L4', 'L6', 'L2']}) ==\
             {bp.Cell.SYNAPSE_CLASS: ['EXC', 'INH'],
              bp.Cell.MORPH_CLASS: ['PYR', 'INT'],
              bp.Cell.REGION: ['GU@left', 'GU@right',
                               'VISa@left', 'VISa@right',
                               'MOp@left', 'MOp@right'],
              bp.Cell.LAYER: [1, 4, 6, 2],
              bp.Cell.MTYPE: allmc + allipc}

    def test_mtypes(self):
        assert self.adapted.mtypes() == [
            {neuroscience.layer: 'L1', neuroscience.mtype: 'L1_DAC', neuroscience.morphology_subclass: 'DAC'},
            {neuroscience.layer: 'L1', neuroscience.mtype: 'L1_HAC', neuroscience.morphology_subclass: 'HAC'},
            {neuroscience.layer: 'L1', neuroscience.mtype: 'L1_LAC', neuroscience.morphology_subclass: 'LAC'},
            {neuroscience.layer: 'L1', neuroscience.mtype: 'L1_NGC-DA', neuroscience.morphology_subclass: 'NGC-DA'},
            {neuroscience.layer: 'L1', neuroscience.mtype: 'L1_NGC-SA', neuroscience.morphology_subclass: 'NGC-SA'},
            {neuroscience.layer: 'L1', neuroscience.mtype: 'L1_SAC', neuroscience.morphology_subclass: 'SAC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_BP', neuroscience.morphology_subclass: 'BP'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_BTC', neuroscience.morphology_subclass: 'BTC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_CHC', neuroscience.morphology_subclass: 'CHC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_DBC', neuroscience.morphology_subclass: 'DBC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_LBC', neuroscience.morphology_subclass: 'LBC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_MC', neuroscience.morphology_subclass: 'MC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_NBC', neuroscience.morphology_subclass: 'NBC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_NGC', neuroscience.morphology_subclass: 'NGC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_SBC', neuroscience.morphology_subclass: 'SBC'},
            {neuroscience.layer: 'L2', neuroscience.mtype: 'L2_IPC', neuroscience.morphology_subclass: 'IPC'},
            {neuroscience.layer: 'L2', neuroscience.mtype: 'L2_TPC:A', neuroscience.morphology_subclass: 'TPC:A'},
            {neuroscience.layer: 'L2', neuroscience.mtype: 'L2_TPC:B', neuroscience.morphology_subclass: 'TPC:B'},
            {neuroscience.layer: 'L3', neuroscience.mtype: 'L3_TPC:A', neuroscience.morphology_subclass: 'TPC:A'},
            {neuroscience.layer: 'L3', neuroscience.mtype: 'L3_TPC:B', neuroscience.morphology_subclass: 'TPC:B'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_BP', neuroscience.morphology_subclass: 'BP'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_BTC', neuroscience.morphology_subclass: 'BTC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_CHC', neuroscience.morphology_subclass: 'CHC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_DBC', neuroscience.morphology_subclass: 'DBC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_LBC', neuroscience.morphology_subclass: 'LBC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_MC', neuroscience.morphology_subclass: 'MC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_NBC', neuroscience.morphology_subclass: 'NBC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_NGC', neuroscience.morphology_subclass: 'NGC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_SBC', neuroscience.morphology_subclass: 'SBC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_SSC', neuroscience.morphology_subclass: 'SSC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_TPC', neuroscience.morphology_subclass: 'TPC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_UPC', neuroscience.morphology_subclass: 'UPC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_BP', neuroscience.morphology_subclass: 'BP'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_BTC', neuroscience.morphology_subclass: 'BTC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_CHC', neuroscience.morphology_subclass: 'CHC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_DBC', neuroscience.morphology_subclass: 'DBC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_LBC', neuroscience.morphology_subclass: 'LBC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_MC', neuroscience.morphology_subclass: 'MC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_NBC', neuroscience.morphology_subclass: 'NBC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_NGC', neuroscience.morphology_subclass: 'NGC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_SBC', neuroscience.morphology_subclass: 'SBC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_TPC:A', neuroscience.morphology_subclass: 'TPC:A'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_TPC:B', neuroscience.morphology_subclass: 'TPC:B'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_TPC:C', neuroscience.morphology_subclass: 'TPC:C'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_UPC', neuroscience.morphology_subclass: 'UPC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_BP', neuroscience.morphology_subclass: 'BP'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_BPC', neuroscience.morphology_subclass: 'BPC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_BTC', neuroscience.morphology_subclass: 'BTC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_CHC', neuroscience.morphology_subclass: 'CHC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_DBC', neuroscience.morphology_subclass: 'DBC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_HPC', neuroscience.morphology_subclass: 'HPC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_IPC', neuroscience.morphology_subclass: 'IPC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_LBC', neuroscience.morphology_subclass: 'LBC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_MC', neuroscience.morphology_subclass: 'MC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_NBC', neuroscience.morphology_subclass: 'NBC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_NGC', neuroscience.morphology_subclass: 'NGC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_SBC', neuroscience.morphology_subclass: 'SBC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_TPC:A', neuroscience.morphology_subclass: 'TPC:A'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_TPC:C', neuroscience.morphology_subclass: 'TPC:C'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_UPC', neuroscience.morphology_subclass: 'UPC'}]

    def test_empty_lists(self):
        assert self.adapted._translate_parameters_cells(
            {neuroscience.synapse_class: [],
             neuroscience.morphology_class: [], neuroscience.region: [],
             neuroscience.mtype: [], neuroscience.layer: []}) == {}

    def test_warns_column(self):
        with pyt.warns(Warning):
            self.adapted.cell_density(**{neuroscience.mesocolumn: 'mc2'})
        pass


class TestOnOldS1:
    """test the CircuitModel on Isocortex release"""

    circuit_config = "/gpfs/bbp.cscs.ch/project/proj64/circuits"\
                     "/S1.v6a/r0/CircuitConfig"
    circuit = bp.Circuit(circuit_config)
    adapted = CircuitModel(circuit_config)
    from voxcell.nexus.voxelbrain import Atlas
    atlas = Atlas.open("/gpfs/bbp.cscs.ch/project/proj64/circuits/S1.v6a/"
                       "r0/.atlas/C63CB79F-392A-4873-9949-0D347682253A")

    def test_cell_density(self):
        test_cells = self.circuit.cells.get().shape[0]
        test_mask = self.atlas.get_region_mask(
            "@S1HL|S1FL|S1Sh|S1Tr")
        test_vol = np.sum(test_mask.raw) * test_mask.voxel_volume * 1e-9
        dens = test_cells / test_vol
        assert self.adapted.cell_density() == pyt.approx(dens)

    @pyt.mark.xfail
    def test_cd_by_layer_mtype_region(self):
        test_cells = self.circuit.cells.get(
            {bp.Cell.LAYER: [1, 3, 6],
             bp.Cell.MTYPE: ['L23_MC', "L6_MC"]})
        test_mask = self.atlas.get_region_mask(
            "S1Sh")
        testvv = test_mask.voxel_volume
        test_mask = np.logical_and(
            test_mask.raw,
            self.atlas.get_region_mask("@L1|L3|L6").raw)
        ncells = np.sum(
            self.atlas.load_data("brain_regions")
            .with_data(test_mask).inspect(test_cells))
        test_vol = np.sum(test_mask) * testvv * 1e-9
        dens = ncells / test_vol
        assert self.adapted.cell_density(
            **{neuroscience.layer: ['L1', 'L3', 'L6'],
               neuroscience.mtype: ['L23_MC', 'L6_MC'],
               neuroscience.region: 'SSp-sh'}) == pyt.approx(dens)

    def test_translate_parameters(self):
        allmc = [mc for mc in sorted(self.circuit.cells.mtypes)
                 if mc.endswith("MC")]
        allipc = [ipc for ipc in sorted(self.circuit.cells.mtypes)
                  if ipc.endswith("IPC")]
        assert self.adapted._translate_parameters_cells(
            {neuroscience.synapse_class: ['EXC', 'INH'],
             neuroscience.morphology_class: ['PYR', 'INT'],
             neuroscience.morphology_subclass: ['MC', 'IPC'],
             neuroscience.layer: ['L1', 'L4', 'L6', 'L2']}) ==\
             {bp.Cell.SYNAPSE_CLASS: ['EXC', 'INH'],
              bp.Cell.MORPH_CLASS: ['PYR', 'INT'],
              bp.Cell.LAYER: [1, 4, 6, 2],
              bp.Cell.MTYPE: allmc + allipc}

    def test_mtypes(self):
        assert self.adapted.mtypes() == [
            {neuroscience.layer: 'L1', neuroscience.mtype: 'L1_DAC', neuroscience.morphology_subclass: 'DAC'},
            {neuroscience.layer: 'L1', neuroscience.mtype: 'L1_HAC', neuroscience.morphology_subclass: 'HAC'},
            {neuroscience.layer: 'L1', neuroscience.mtype: 'L1_LAC', neuroscience.morphology_subclass: 'LAC'},
            {neuroscience.layer: 'L1', neuroscience.mtype: 'L1_NGC-DA', neuroscience.morphology_subclass: 'NGC-DA'},
            {neuroscience.layer: 'L1', neuroscience.mtype: 'L1_NGC-SA', neuroscience.morphology_subclass: 'NGC-SA'},
            {neuroscience.layer: 'L1', neuroscience.mtype: 'L1_SAC', neuroscience.morphology_subclass: 'SAC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_BP', neuroscience.morphology_subclass: 'BP'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_BTC', neuroscience.morphology_subclass: 'BTC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_CHC', neuroscience.morphology_subclass: 'CHC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_DBC', neuroscience.morphology_subclass: 'DBC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_LBC', neuroscience.morphology_subclass: 'LBC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_MC', neuroscience.morphology_subclass: 'MC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_NBC', neuroscience.morphology_subclass: 'NBC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_NGC', neuroscience.morphology_subclass: 'NGC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_SBC', neuroscience.morphology_subclass: 'SBC'},
            {neuroscience.layer: 'L2', neuroscience.mtype: 'L2_IPC', neuroscience.morphology_subclass: 'IPC'},
            {neuroscience.layer: 'L2', neuroscience.mtype: 'L2_TPC:A', neuroscience.morphology_subclass: 'TPC:A'},
            {neuroscience.layer: 'L2', neuroscience.mtype: 'L2_TPC:B', neuroscience.morphology_subclass: 'TPC:B'},
            {neuroscience.layer: 'L3', neuroscience.mtype: 'L3_TPC:A', neuroscience.morphology_subclass: 'TPC:A'},
            {neuroscience.layer: 'L3', neuroscience.mtype: 'L3_TPC:B', neuroscience.morphology_subclass: 'TPC:B'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_BP', neuroscience.morphology_subclass: 'BP'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_BTC', neuroscience.morphology_subclass: 'BTC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_CHC', neuroscience.morphology_subclass: 'CHC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_DBC', neuroscience.morphology_subclass: 'DBC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_LBC', neuroscience.morphology_subclass: 'LBC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_MC', neuroscience.morphology_subclass: 'MC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_NBC', neuroscience.morphology_subclass: 'NBC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_NGC', neuroscience.morphology_subclass: 'NGC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_SBC', neuroscience.morphology_subclass: 'SBC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_SSC', neuroscience.morphology_subclass: 'SSC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_TPC', neuroscience.morphology_subclass: 'TPC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_UPC', neuroscience.morphology_subclass: 'UPC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_BP', neuroscience.morphology_subclass: 'BP'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_BTC', neuroscience.morphology_subclass: 'BTC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_CHC', neuroscience.morphology_subclass: 'CHC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_DBC', neuroscience.morphology_subclass: 'DBC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_LBC', neuroscience.morphology_subclass: 'LBC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_MC', neuroscience.morphology_subclass: 'MC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_NBC', neuroscience.morphology_subclass: 'NBC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_NGC', neuroscience.morphology_subclass: 'NGC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_SBC', neuroscience.morphology_subclass: 'SBC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_TPC:A', neuroscience.morphology_subclass: 'TPC:A'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_TPC:B', neuroscience.morphology_subclass: 'TPC:B'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_TPC:C', neuroscience.morphology_subclass: 'TPC:C'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_UPC', neuroscience.morphology_subclass: 'UPC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_BP', neuroscience.morphology_subclass: 'BP'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_BPC', neuroscience.morphology_subclass: 'BPC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_BTC', neuroscience.morphology_subclass: 'BTC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_CHC', neuroscience.morphology_subclass: 'CHC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_DBC', neuroscience.morphology_subclass: 'DBC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_HPC', neuroscience.morphology_subclass: 'HPC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_IPC', neuroscience.morphology_subclass: 'IPC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_LBC', neuroscience.morphology_subclass: 'LBC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_MC', neuroscience.morphology_subclass: 'MC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_NBC', neuroscience.morphology_subclass: 'NBC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_NGC', neuroscience.morphology_subclass: 'NGC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_SBC', neuroscience.morphology_subclass: 'SBC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_TPC:A', neuroscience.morphology_subclass: 'TPC:A'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_TPC:C', neuroscience.morphology_subclass: 'TPC:C'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_UPC', neuroscience.morphology_subclass: 'UPC'}]

    def test_empty_lists(self):
        assert self.adapted._translate_parameters_cells(
            {neuroscience.synapse_class: [],
             neuroscience.morphology_class: [], neuroscience.region: [],
             neuroscience.mtype: [], neuroscience.layer: []}) == {}

    def test_warns_column(self):
        with pyt.warns(Warning):
            self.adapted.cell_density(**{neuroscience.mesocolumn: 'mc2'})
        pass


class TestOnProj1RatO1:
    """test the CircuitModel on Isocortex release"""

    circuit_config = "/gpfs/bbp.cscs.ch/project/proj1/circuits/"\
                     "SomatosensoryCxS1-v5.r0/O1/merged_circuit/"\
                     "CircuitConfig"
    circuit = bp.Circuit(circuit_config)
    with pyt.warns(Warning):
        adapted = CircuitModel(circuit_config)

    def test_cell_density_raises(self):
        # dens = test_cells / test_vol
        with pyt.raises(NotImplementedError):
            self.adapted.cell_density()

    def test_translate_parameters(self):
        allmc = [mc for mc in sorted(self.circuit.cells.mtypes)
                 if mc.endswith("MC")]
        allipc = [ipc for ipc in sorted(self.circuit.cells.mtypes)
                  if ipc.endswith("IPC")]
        assert self.adapted._translate_parameters_cells(
            {neuroscience.synapse_class: ['EXC', 'INH'],
             neuroscience.morphology_class: ['PYR', 'INT'],
             neuroscience.morphology_subclass: ['MC', 'IPC'],
             neuroscience.layer: ['L1', 'L4', 'L6', 'L2'],
             neuroscience.mesocolumn: ["mc1", "mc2"]}) ==\
            {bp.Cell.SYNAPSE_CLASS: ['EXC', 'INH'],
             bp.Cell.MORPH_CLASS: ['PYR', 'INT'],
             bp.Cell.LAYER: [1, 4, 6, 2],
             bp.Cell.MTYPE: allmc + allipc,
             bp.Cell.HYPERCOLUMN: [1, 2]}

    def test_mtypes(self):
        assert self.adapted.mtypes() == [
            {neuroscience.layer: 'L1', neuroscience.mtype: 'L1_DAC', neuroscience.morphology_subclass: 'DAC'},
            {neuroscience.layer: 'L1', neuroscience.mtype: 'L1_DLAC', neuroscience.morphology_subclass: 'DLAC'},
            {neuroscience.layer: 'L1', neuroscience.mtype: 'L1_HAC', neuroscience.morphology_subclass: 'HAC'},
            {neuroscience.layer: 'L1', neuroscience.mtype: 'L1_NGC-DA', neuroscience.morphology_subclass: 'NGC-DA'},
            {neuroscience.layer: 'L1', neuroscience.mtype: 'L1_NGC-SA', neuroscience.morphology_subclass: 'NGC-SA'},
            {neuroscience.layer: 'L1', neuroscience.mtype: 'L1_SLAC', neuroscience.morphology_subclass: 'SLAC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_BP', neuroscience.morphology_subclass: 'BP'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_BTC', neuroscience.morphology_subclass: 'BTC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_ChC', neuroscience.morphology_subclass: 'ChC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_DBC', neuroscience.morphology_subclass: 'DBC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_LBC', neuroscience.morphology_subclass: 'LBC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_MC', neuroscience.morphology_subclass: 'MC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_NBC', neuroscience.morphology_subclass: 'NBC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_NGC', neuroscience.morphology_subclass: 'NGC'},
            {neuroscience.layer: ['L2', "L3"], neuroscience.mtype: 'L23_PC', neuroscience.morphology_subclass: 'PC'},
            {neuroscience.layer: ['L2', 'L3'], neuroscience.mtype: 'L23_SBC', neuroscience.morphology_subclass: 'SBC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_BP', neuroscience.morphology_subclass: 'BP'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_BTC', neuroscience.morphology_subclass: 'BTC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_ChC', neuroscience.morphology_subclass: 'ChC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_DBC', neuroscience.morphology_subclass: 'DBC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_LBC', neuroscience.morphology_subclass: 'LBC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_MC', neuroscience.morphology_subclass: 'MC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_NBC', neuroscience.morphology_subclass: 'NBC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_NGC', neuroscience.morphology_subclass: 'NGC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_PC', neuroscience.morphology_subclass: 'PC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_SBC', neuroscience.morphology_subclass: 'SBC'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_SP', neuroscience.morphology_subclass: 'SP'},
            {neuroscience.layer: 'L4', neuroscience.mtype: 'L4_SS', neuroscience.morphology_subclass: 'SS'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_BP', neuroscience.morphology_subclass: 'BP'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_BTC', neuroscience.morphology_subclass: 'BTC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_ChC', neuroscience.morphology_subclass: 'ChC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_DBC', neuroscience.morphology_subclass: 'DBC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_LBC', neuroscience.morphology_subclass: 'LBC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_MC', neuroscience.morphology_subclass: 'MC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_NBC', neuroscience.morphology_subclass: 'NBC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_NGC', neuroscience.morphology_subclass: 'NGC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_SBC', neuroscience.morphology_subclass: 'SBC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_STPC', neuroscience.morphology_subclass: 'STPC'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_TTPC1', neuroscience.morphology_subclass: 'TTPC1'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_TTPC2', neuroscience.morphology_subclass: 'TTPC2'},
            {neuroscience.layer: 'L5', neuroscience.mtype: 'L5_UTPC', neuroscience.morphology_subclass: 'UTPC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_BP', neuroscience.morphology_subclass: 'BP'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_BPC', neuroscience.morphology_subclass: 'BPC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_BTC', neuroscience.morphology_subclass: 'BTC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_ChC', neuroscience.morphology_subclass: 'ChC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_DBC', neuroscience.morphology_subclass: 'DBC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_IPC', neuroscience.morphology_subclass: 'IPC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_LBC', neuroscience.morphology_subclass: 'LBC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_MC', neuroscience.morphology_subclass: 'MC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_NBC', neuroscience.morphology_subclass: 'NBC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_NGC', neuroscience.morphology_subclass: 'NGC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_SBC', neuroscience.morphology_subclass: 'SBC'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_TPC_L1', neuroscience.morphology_subclass: 'TPC_L1'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_TPC_L4', neuroscience.morphology_subclass: 'TPC_L4'},
            {neuroscience.layer: 'L6', neuroscience.mtype: 'L6_UTPC', neuroscience.morphology_subclass: 'UTPC'}]

    @pyt.mark.xfail
    def test_warns_missing_mtype(self):
        with pyt.warns(Warning):
            self.adapted._translate_parameters_cells(
                {neuroscience.mtype: 'BAASDHAS'})

    def test_warns_missing_morphsubclass(self):
        with pyt.warns(Warning):
            self.adapted._translate_parameters_cells(
                {neuroscience.morphology_subclass: 'BAASDHAS'})

    def test_empty_lists(self):
        assert self.adapted._translate_parameters_cells(
            {neuroscience.synapse_class: [],
             neuroscience.morphology_class: [],
             neuroscience.region: [],
             neuroscience.mtype: [], neuroscience.layer: []}) == {}

    def test_warns_region(self):
        with pyt.warns(Warning):
            self.adapted._translate_parameters_cells({neuroscience.region: 'SS'})
        pass


class TestOnNewS1:
    circuit_config = "/gpfs/bbp.cscs.ch/project/proj64/dissemination/circuits"\
                     "/S1/juvenile/L23_MC_BTC_shifted_down/Bio_M/20190925/"\
                     "CircuitConfig"
    circuit = bp.Circuit(circuit_config)
    adapted = CircuitModel(circuit_config)

    def test_translates_region(self):
        params = self.adapted._translate_parameters_cells(
            {neuroscience.region: 'SSp-ll'})
        assert params[bp.Cell.REGION] == ['S1HL']


class TestConnectomeFunctions:
    """on proj1 rat O1"""

    circuit_config = "/gpfs/bbp.cscs.ch/project/proj1/circuits/"\
                     "SomatosensoryCxS1-v5.r0/O1/merged_circuit/"\
                     "CircuitConfig"
    circuit = bp.Circuit(circuit_config)
    with pyt.warns(Warning):
        adapted = CircuitModel(circuit_config)

    def test_connection_probability(self):
        # will not be precise enough to succeed
        pre_group = {bp.Cell.MTYPE: ['L4_PC']}
        post_group = {bp.Cell.MTYPE: ['L4_MC']}
        exp_num = len(tuple(self.circuit.connectome.iter_connections(
            pre=pre_group, post=post_group)))
        pre_group_len = self.circuit.cells.get(pre_group).shape[0]
        post_group_len = self.circuit.cells.get(post_group).shape[0]
        num_pairs = pre_group_len * post_group_len
        exprob = exp_num / num_pairs
        assert self.adapted.connection_probability(
            **{neuroscience.presynaptic:
               {neuroscience.layer: "L4", neuroscience.morphology_subclass: "PC"},
               neuroscience.postsynaptic:
               {neuroscience.layer: "L4",
                neuroscience.morphology_subclass: "MC"}},
            sample_size=1000) ==\
                pyt.approx(exprob, rel=0.1)

    def test_conn_prob_empty_cells(self):
        assert np.isnan(self.adapted.connection_probability(
            **{neuroscience.presynaptic:
               {neuroscience.layer: "L1", neuroscience.morphology_subclass: ['PC']},
               neuroscience.postsynaptic:
               {neuroscience.layer: "L2", neuroscience.morphology_subclass: ["CHC"]}}))

    def test_syns_per_conn(self):
        pre_group = {bp.Cell.MTYPE: ['L1_DAC']}
        post_group = {bp.Cell.MTYPE: ['L4_PC']}
        iterator = self.circuit.connectome.iter_connections(
            pre=pre_group, post=post_group, return_synapse_count=True)
        exp_syncounts = [conn[2] for conn in iterator]
        assert self.adapted.synapses_per_connection(
            **{neuroscience.presynaptic:
               {neuroscience.layer: "L1", neuroscience.morphology_subclass: "DAC"},
               neuroscience.postsynaptic:
               {neuroscience.layer: "L4",
                neuroscience.morphology_subclass: "PC"}},
            sample_size=1000) ==\
            pyt.approx(np.mean(exp_syncounts), rel=0.1)

    def test_pathway_synapses(self):
        pre_group = {bp.Cell.MTYPE: ['L4_BP']}
        post_group = {bp.Cell.MTYPE: ['L23_PC']}
        exp_synapses = len(self.circuit.connectome.pathway_synapses(
            pre=pre_group, post=post_group))

        assert self.adapted.pathway_synapses(
            **{neuroscience.presynaptic:
               {neuroscience.layer: "L4", neuroscience.morphology_subclass: "BP"},
             neuroscience.postsynaptic:
               {neuroscience.layer: ["L2", "L3"],
                neuroscience.morphology_subclass: "PC"}}) ==\
            exp_synapses


class TestHeightAndDepth:

    def test_O1_circuit_heights_and_depths(self):
        cfg = "/gpfs/bbp.cscs.ch/project/proj68/circuits/O1/20190307/CircuitConfig"
        model = CircuitModel(cfg)
        circuit = bp.Circuit(cfg)
        height = circuit.atlas.load_data("[PH]y").raw
        depth = circuit.atlas.load_data("[PH]1").raw[..., 1]\
                - circuit.atlas.load_data("[PH]y").raw\


        height_all = height[circuit.atlas.get_region_mask("O1").raw]
        depth_all = depth[circuit.atlas.get_region_mask("O1").raw]

        npt.assert_array_equal(model.heights(),
                               np.unique(height_all[np.isfinite(height_all)]))
        npt.assert_array_equal(
            model.heights(**{neuroscience.layer: "L1"}),
            np.unique(height[circuit.atlas.get_region_mask("L1").raw]))
        npt.assert_array_equal(
            model.depths(), np.unique(depth_all[np.isfinite(depth_all)]))

    #TODO: this is imprecise when using the atlaas
    #      TODO: implement more precise version for O1
    #      TODO: determine a way to improve the atlas-based version
    @pyt.mark.xfail
    def test_O1_circuit_height_depth_parameters(self):
        cfg = "/gpfs/bbp.cscs.ch/project/proj68/circuits/O1/20190307/CircuitConfig"
        model = CircuitModel(cfg)
        circuit = bp.Circuit(cfg)
        height = circuit.atlas.load_data("[PH]y").raw\
            - circuit.atlas.load_data("[PH]6").raw[..., 0]
        depth = -circuit.atlas.load_data("[PH]y").raw
        pdt.assert_frame_equal(model.get_cells(**{neuroscience.height: (0, 600)}),
                               circuit.cells.get({bp.Cell.Y: [0, 600]}))
        # TODO: voxel-related inaccuracy
        print(model.get_cells(**{neuroscience.depth: (0, 100)}).y.min())
        print(circuit.cells.get({bp.Cell.Y: [1277.5, 1377.5]}).y.min())
        pdt.assert_frame_equal(model.get_cells(**{neuroscience.depth: (0, 100)}),
                               circuit.cells.get({bp.Cell.Y: [1277.5, 1377.5]}))

    # TODO: edge case: asking for get cells with properties excluding positions


# TODO:
class TestOldstyleHippocampus:
    """old hippocampus with regions as layers"""
    # circuit_config = "/gpfs/bbp.cscs.ch/project/proj42/circuits/"\
    #                  "CA1.O1/20180219/CircuitConfig"
    # circuit = bp.Circuit(circuit_config)
    # adapted = CircuitModel(circuit_config)
    pass


# TODO:
class TestNewStyleHippocampus:
    """new hippocampus with string layers"""
    pass


# TODO:
class TestCA1Circuit:
    pass


# TODO:
class TestO1Thalamus:
    circuit_config = "/gpfs/bbp.cscs.ch/project/proj55/iavarone/"\
                     "releases/circuits/O1/2019-07-18/CircuitConfig"
    circuit = bp.Circuit(circuit_config)
    adapted = CircuitModel(circuit_config)

    def test_translate_layer(self):
        assert self.adapted._translate_parameters_cells(
            {neuroscience.layer: ['RT', 'VPL']}) ==\
            {bp.Cell.LAYER: ['Rt', 'VPL']}


def test_accepts_tuples():

    circuit_config = "/gpfs/bbp.cscs.ch/project/proj68/circuits/"\
                     "O1/20190307/CircuitConfig"
    circuit = bp.Circuit(circuit_config)
    adapted = CircuitModel(circuit_config)
    import pandas as pd
    pd.testing.assert_frame_equal(
        adapted.get_cells(**{neuroscience.layer: ('L1', 'L2')}),
        circuit.cells.get({bp.Cell.LAYER: [1, 2]}))
