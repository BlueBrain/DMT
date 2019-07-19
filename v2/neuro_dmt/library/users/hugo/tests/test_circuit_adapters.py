import numpy as np
import bluepy.v2 as bp
from neuro_dmt.library.users.hugo.adapters import CircuitAdapter


class TestOnNCXO1:
    """test the CircuitAdapter on O1 from neocortex release"""

    circuit_config = "/gpfs/bbp.cscs.ch/project/proj68/circuits/"\
                     "O1/20190307/CircuitConfig"
    circuit = bp.Circuit(circuit_config)
    adapted = CircuitAdapter(circuit_config)

    def test_cell_density(self):
        test_cells = self.circuit.cells.get().shape[1]
        test_vol = np.sum(self.circuit.atlas.get_region_mask("O1").raw) * 1e-9
        assert self.adapted.cell_density({}) == test_cells / test_vol

    def test_cd_by_layer_mtype_column(self):
        test_cells = self.circuit.cells.get(
            {bp.Cell.LAYER: [1, 3, 6],
             bp.Cell.MTYPE: ['L23_MC', "L6_MC"],
             bp.Cell.REGION: 'mc2_Column'}).shape[1]
        test_vol = np.sum(
            np.logical_and(
                self.circuit.atlas.get_region_mask("mc2_Column").raw,
                self.circuit.atlas.get_region_mask("@L[136]$").raw)) * 1e-9
        assert self.adapted.cell_density(
            {'layer': ['L1', 'L3', 'L6'],
             'mtype': 'MC',
             'column': 'mc2'}) == test_cells / test_vol

    def test_mtypes(self):
        assert self.adapted.mtypes() == [
            {'layer': 'L1', 'mtype': 'DAC'},
            {'layer': 'L1', 'mtype': 'HAC'},
            {'layer': 'L1', 'mtype': 'LAC'},
            {'layer': 'L1', 'mtype': 'NGC-DA'},
            {'layer': 'L1', 'mtype': 'NGC-SA'},
            {'layer': 'L1', 'mtype': 'SAC'},
            {'layer': ['L2', 'L3'], 'mtype': 'BP'},
            {'layer': ['L2', 'L3'], 'mtype': 'BTC'},
            {'layer': ['L2', 'L3'], 'mtype': 'CHC'},
            {'layer': ['L2', 'L3'], 'mtype': 'DBC'},
            {'layer': ['L2', 'L3'], 'mtype': 'LBC'},
            {'layer': ['L2', 'L3'], 'mtype': 'MC'},
            {'layer': ['L2', 'L3'], 'mtype': 'NBC'},
            {'layer': ['L2', 'L3'], 'mtype': 'NGC'},
            {'layer': ['L2', 'L3'], 'mtype': 'SBC'},
            {'layer': 'L2', 'mtype': 'IPC'},
            {'layer': 'L2', 'mtype': 'TPC:A'},
            {'layer': 'L2', 'mtype': 'TPC:B'},
            {'layer': 'L3', 'mtype': 'TPC:A'},
            {'layer': 'L3', 'mtype': 'TPC:B'},
            {'layer': 'L4', 'mtype': 'BP'},
            {'layer': 'L4', 'mtype': 'BTC'},
            {'layer': 'L4', 'mtype': 'CHC'},
            {'layer': 'L4', 'mtype': 'DBC'},
            {'layer': 'L4', 'mtype': 'LBC'},
            {'layer': 'L4', 'mtype': 'MC'},
            {'layer': 'L4', 'mtype': 'NBC'},
            {'layer': 'L4', 'mtype': 'NGC'},
            {'layer': 'L4', 'mtype': 'SBC'},
            {'layer': 'L4', 'mtype': 'SSC'},
            {'layer': 'L4', 'mtype': 'TPC'},
            {'layer': 'L4', 'mtype': 'UPC'},
            {'layer': 'L5', 'mtype': 'BP'},
            {'layer': 'L5', 'mtype': 'BTC'},
            {'layer': 'L5', 'mtype': 'CHC'},
            {'layer': 'L5', 'mtype': 'DBC'},
            {'layer': 'L5', 'mtype': 'LBC'},
            {'layer': 'L5', 'mtype': 'MC'},
            {'layer': 'L5', 'mtype': 'NBC'},
            {'layer': 'L5', 'mtype': 'NGC'},
            {'layer': 'L5', 'mtype': 'SBC'},
            {'layer': 'L5', 'mtype': 'TPC:A'},
            {'layer': 'L5', 'mtype': 'TPC:B'},
            {'layer': 'L5', 'mtype': 'TPC:C'},
            {'layer': 'L5', 'mtype': 'UPC'},
            {'layer': 'L6', 'mtype': 'BP'},
            {'layer': 'L6', 'mtype': 'BPC'},
            {'layer': 'L6', 'mtype': 'BTC'},
            {'layer': 'L6', 'mtype': 'CHC'},
            {'layer': 'L6', 'mtype': 'DBC'},
            {'layer': 'L6', 'mtype': 'HPC'},
            {'layer': 'L6', 'mtype': 'IPC'},
            {'layer': 'L6', 'mtype': 'LBC'},
            {'layer': 'L6', 'mtype': 'MC'},
            {'layer': 'L6', 'mtype': 'NBC'},
            {'layer': 'L6', 'mtype': 'NGC'},
            {'layer': 'L6', 'mtype': 'SBC'},
            {'layer': 'L6', 'mtype': 'TPC:A'},
            {'layer': 'L6', 'mtype': 'TPC:C'},
            {'layer': 'L6', 'mtype': 'UPC'}]
