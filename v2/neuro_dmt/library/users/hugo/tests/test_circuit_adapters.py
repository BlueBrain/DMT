import numpy as np
import pytest as pyt
import bluepy.v2 as bp
from neuro_dmt.library.users.hugo.adapters import CircuitAdapter,\
    SYN_CLASS, LAYER, MTYPE, COLUMN, MORPH_CLASS


class TestOnNCXO1:
    """test the CircuitAdapter on O1 from neocortex release"""

    circuit_config = "/gpfs/bbp.cscs.ch/project/proj68/circuits/"\
                     "O1/20190307/CircuitConfig"
    circuit = bp.Circuit(circuit_config)
    adapted = CircuitAdapter(circuit_config)

    def test_cell_density(self):
        test_cells = self.circuit.cells.get().shape[0]
        test_mask = self.circuit.atlas.get_region_mask("O1")
        test_vol = np.sum(test_mask.raw) * test_mask.voxel_volume * 1e-9
        dens = test_cells / test_vol
        assert self.adapted.cell_density({}) == pyt.approx(dens)

    def test_cd_by_layer_mtype_column(self):
        test_cells = self.circuit.cells.get(
            {bp.Cell.LAYER: [1, 3, 6],
             bp.Cell.MTYPE: ['L23_MC', "L6_MC"],
             bp.Cell.REGION: 'mc2_Column'}).shape[0]
        col_mask = self.circuit.atlas.get_region_mask("mc2_Column")
        test_mask = np.logical_and(
            col_mask.raw,
            self.circuit.atlas.get_region_mask("@L[136]$").raw)
        test_vol = np.sum(test_mask) * col_mask.voxel_volume * 1e-9
        dens = test_cells / test_vol
        assert self.adapted.cell_density(
            {LAYER: ['L1', 'L3', 'L6'],
             MTYPE: 'MC',
             COLUMN: 'mc2'}) == pyt.approx(dens)

    def test_translate_parameters(self):
        allmc = [mc for mc in sorted(self.circuit.cells.mtypes)
                 if mc.endswith("MC")]
        allipc = [ipc for ipc in sorted(self.circuit.cells.mtypes)
                  if ipc.endswith("IPC")]
        assert self.adapted._translate_parameters_cells(
            {SYN_CLASS: ['EXC', 'INH'],
             MORPH_CLASS: ['PYR', 'INT'],
             COLUMN: ['mc2', 'mc3', 'mc0'],
             MTYPE: ['MC', 'IPC'],
             LAYER: ['L1', 'L4', 'L6', 'L2']}) ==\
            {bp.Cell.SYNAPSE_CLASS: ['EXC', 'INH'],
             bp.Cell.MORPH_CLASS: ['PYR', 'INT'],
             bp.Cell.REGION: ['mc2_Column', 'mc3_Column', 'mc0_Column'],
             bp.Cell.LAYER: [1, 4, 6, 2],
             bp.Cell.MTYPE: allmc + allipc}

    def test_mtypes(self):
        assert self.adapted.mtypes() == [
            {LAYER: 'L1', MTYPE: 'DAC'},
            {LAYER: 'L1', MTYPE: 'HAC'},
            {LAYER: 'L1', MTYPE: 'LAC'},
            {LAYER: 'L1', MTYPE: 'NGC-DA'},
            {LAYER: 'L1', MTYPE: 'NGC-SA'},
            {LAYER: 'L1', MTYPE: 'SAC'},
            {LAYER: ['L2', 'L3'], MTYPE: 'BP'},
            {LAYER: ['L2', 'L3'], MTYPE: 'BTC'},
            {LAYER: ['L2', 'L3'], MTYPE: 'CHC'},
            {LAYER: ['L2', 'L3'], MTYPE: 'DBC'},
            {LAYER: ['L2', 'L3'], MTYPE: 'LBC'},
            {LAYER: ['L2', 'L3'], MTYPE: 'MC'},
            {LAYER: ['L2', 'L3'], MTYPE: 'NBC'},
            {LAYER: ['L2', 'L3'], MTYPE: 'NGC'},
            {LAYER: ['L2', 'L3'], MTYPE: 'SBC'},
            {LAYER: 'L2', MTYPE: 'IPC'},
            {LAYER: 'L2', MTYPE: 'TPC:A'},
            {LAYER: 'L2', MTYPE: 'TPC:B'},
            {LAYER: 'L3', MTYPE: 'TPC:A'},
            {LAYER: 'L3', MTYPE: 'TPC:B'},
            {LAYER: 'L4', MTYPE: 'BP'},
            {LAYER: 'L4', MTYPE: 'BTC'},
            {LAYER: 'L4', MTYPE: 'CHC'},
            {LAYER: 'L4', MTYPE: 'DBC'},
            {LAYER: 'L4', MTYPE: 'LBC'},
            {LAYER: 'L4', MTYPE: 'MC'},
            {LAYER: 'L4', MTYPE: 'NBC'},
            {LAYER: 'L4', MTYPE: 'NGC'},
            {LAYER: 'L4', MTYPE: 'SBC'},
            {LAYER: 'L4', MTYPE: 'SSC'},
            {LAYER: 'L4', MTYPE: 'TPC'},
            {LAYER: 'L4', MTYPE: 'UPC'},
            {LAYER: 'L5', MTYPE: 'BP'},
            {LAYER: 'L5', MTYPE: 'BTC'},
            {LAYER: 'L5', MTYPE: 'CHC'},
            {LAYER: 'L5', MTYPE: 'DBC'},
            {LAYER: 'L5', MTYPE: 'LBC'},
            {LAYER: 'L5', MTYPE: 'MC'},
            {LAYER: 'L5', MTYPE: 'NBC'},
            {LAYER: 'L5', MTYPE: 'NGC'},
            {LAYER: 'L5', MTYPE: 'SBC'},
            {LAYER: 'L5', MTYPE: 'TPC:A'},
            {LAYER: 'L5', MTYPE: 'TPC:B'},
            {LAYER: 'L5', MTYPE: 'TPC:C'},
            {LAYER: 'L5', MTYPE: 'UPC'},
            {LAYER: 'L6', MTYPE: 'BP'},
            {LAYER: 'L6', MTYPE: 'BPC'},
            {LAYER: 'L6', MTYPE: 'BTC'},
            {LAYER: 'L6', MTYPE: 'CHC'},
            {LAYER: 'L6', MTYPE: 'DBC'},
            {LAYER: 'L6', MTYPE: 'HPC'},
            {LAYER: 'L6', MTYPE: 'IPC'},
            {LAYER: 'L6', MTYPE: 'LBC'},
            {LAYER: 'L6', MTYPE: 'MC'},
            {LAYER: 'L6', MTYPE: 'NBC'},
            {LAYER: 'L6', MTYPE: 'NGC'},
            {LAYER: 'L6', MTYPE: 'SBC'},
            {LAYER: 'L6', MTYPE: 'TPC:A'},
            {LAYER: 'L6', MTYPE: 'TPC:C'},
            {LAYER: 'L6', MTYPE: 'UPC'}]
