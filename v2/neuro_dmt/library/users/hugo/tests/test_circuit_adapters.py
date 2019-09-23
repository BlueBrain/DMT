import numpy as np
import pytest as pyt
import bluepy.v2 as bp
from neuro_dmt.library.users.hugo.adapters import CircuitAdapter
from neuro_dmt.library.users.hugo.adapters.utils import\
    SYN_CLASS, LAYER, MTYPE, COLUMN, MORPH_CLASS, REGION,\
    PRESYNAPTIC, POSTSYNAPTIC


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

    def test_empty_lists(self):
        assert self.adapted._translate_parameters_cells(
            {SYN_CLASS: [], MORPH_CLASS: [], COLUMN: [],
             MTYPE: [], LAYER: []}) == {}

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

    def test_warns_region(self):
        with pyt.warns(Warning):
            self.adapted.cell_density({REGION: 'SSp'})
        pass


class TestOnNCXIsocortex:
    """test the CircuitAdapter on Isocortex release"""

    circuit_config = "/gpfs/bbp.cscs.ch/project/proj68/circuits/"\
                     "Isocortex/20190307/CircuitConfig"
    circuit = bp.Circuit(circuit_config)
    adapted = CircuitAdapter(circuit_config)

    def test_cell_density(self):
        test_cells = self.circuit.cells.get().shape[0]
        test_mask = self.circuit.atlas.get_region_mask("Isocortex")
        test_vol = np.sum(test_mask.raw) * test_mask.voxel_volume * 1e-9
        dens = test_cells / test_vol
        assert self.adapted.cell_density({}) == pyt.approx(dens)

    def test_cd_by_layer_mtype_region(self):
        test_cells = self.circuit.cells.get(
            {bp.Cell.LAYER: [1, 3, 6],
             bp.Cell.MTYPE: ['L23_MC', "L6_MC"],
             bp.Cell.REGION: ['SSp-ll@left', 'SSp-ll@right']}).shape[0]
        test_mask = self.circuit.atlas.get_region_mask("@SSp-ll[136]$")
        test_vol = np.sum(test_mask.raw) * test_mask.voxel_volume * 1e-9
        dens = test_cells / test_vol
        assert self.adapted.cell_density(
            {LAYER: ['L1', 'L3', 'L6'],
             MTYPE: 'MC',
             REGION: 'SSp-ll'}) == pyt.approx(dens)

    def test_translate_parameters(self):
        allmc = [mc for mc in sorted(self.circuit.cells.mtypes)
                 if mc.endswith("MC")]
        allipc = [ipc for ipc in sorted(self.circuit.cells.mtypes)
                  if ipc.endswith("IPC")]
        assert self.adapted._translate_parameters_cells(
            {SYN_CLASS: ['EXC', 'INH'],
             MORPH_CLASS: ['PYR', 'INT'],
             REGION: ['GU', 'VISa', 'MOp'],
             MTYPE: ['MC', 'IPC'],
             LAYER: ['L1', 'L4', 'L6', 'L2']}) ==\
            {bp.Cell.SYNAPSE_CLASS: ['EXC', 'INH'],
             bp.Cell.MORPH_CLASS: ['PYR', 'INT'],
             bp.Cell.REGION: ['GU@left', 'GU@right',
                              'VISa@left', 'VISa@right',
                              'MOp@left', 'MOp@right'],
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

    def test_empty_lists(self):
        assert self.adapted._translate_parameters_cells(
            {SYN_CLASS: [], MORPH_CLASS: [], REGION: [],
             MTYPE: [], LAYER: []}) == {}

    def test_warns_column(self):
        with pyt.warns(Warning):
            self.adapted.cell_density({COLUMN: 'mc2'})
        pass


class TestOnOldS1:
    """test the CircuitAdapter on Isocortex release"""

    circuit_config = "/gpfs/bbp.cscs.ch/project/proj64/circuits"\
                     "/S1.v6a/r0/CircuitConfig"
    circuit = bp.Circuit(circuit_config)
    adapted = CircuitAdapter(circuit_config)
    from voxcell.nexus.voxelbrain import Atlas
    atlas = Atlas.open("/gpfs/bbp.cscs.ch/project/proj64/circuits/S1.v6a/"
                       "r0/.atlas/C63CB79F-392A-4873-9949-0D347682253A")

    def test_cell_density(self):
        test_cells = self.circuit.cells.get().shape[0]
        test_mask = self.atlas.get_region_mask(
            "@S1HL|S1FL|S1Sh|S1Tr")
        test_vol = np.sum(test_mask.raw) * test_mask.voxel_volume * 1e-9
        dens = test_cells / test_vol
        assert self.adapted.cell_density({}) == pyt.approx(dens)

    # TODO: This test is flawed! the circuit does not get region!
    def test_cd_by_layer_mtype_region(self):
        test_cells = self.circuit.cells.get(
            {bp.Cell.LAYER: [1, 3, 6],
             bp.Cell.MTYPE: ['L23_MC', "L6_MC"]}).shape[0]
        test_mask = self.atlas.get_region_mask(
            "S1Sh")
        testvv = test_mask.voxel_volume
        test_mask = np.logical_and(
            test_mask.raw,
            self.atlas.get_region_mask("@L1|L3|L6").raw)
        test_vol = np.sum(test_mask) * testvv * 1e-9
        dens = test_cells / test_vol
        assert self.adapted.cell_density(
            {LAYER: ['L1', 'L3', 'L6'],
             MTYPE: 'MC',
             REGION: 'SSp-sh'}) == pyt.approx(dens)

    def test_translate_parameters(self):
        allmc = [mc for mc in sorted(self.circuit.cells.mtypes)
                 if mc.endswith("MC")]
        allipc = [ipc for ipc in sorted(self.circuit.cells.mtypes)
                  if ipc.endswith("IPC")]
        assert self.adapted._translate_parameters_cells(
            {SYN_CLASS: ['EXC', 'INH'],
             MORPH_CLASS: ['PYR', 'INT'],
             MTYPE: ['MC', 'IPC'],
             LAYER: ['L1', 'L4', 'L6', 'L2']}) ==\
            {bp.Cell.SYNAPSE_CLASS: ['EXC', 'INH'],
             bp.Cell.MORPH_CLASS: ['PYR', 'INT'],
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

    def test_empty_lists(self):
        assert self.adapted._translate_parameters_cells(
            {SYN_CLASS: [], MORPH_CLASS: [], REGION: [],
             MTYPE: [], LAYER: []}) == {}

    def test_warns_column(self):
        with pyt.warns(Warning):
            self.adapted.cell_density({COLUMN: 'mc2'})
        pass


class TestOnProj1RatO1:
    """test the CircuitAdapter on Isocortex release"""

    circuit_config = "/gpfs/bbp.cscs.ch/project/proj1/circuits/"\
                     "SomatosensoryCxS1-v5.r0/O1/merged_circuit/"\
                     "CircuitConfig"
    circuit = bp.Circuit(circuit_config)
    with pyt.warns(Warning):
        adapted = CircuitAdapter(circuit_config)

    def test_cell_density_raises(self):
        # dens = test_cells / test_vol
        with pyt.raises(NotImplementedError):
            self.adapted.cell_density({})

    def test_translate_parameters(self):
        allmc = [mc for mc in sorted(self.circuit.cells.mtypes)
                 if mc.endswith("MC")]
        allipc = [ipc for ipc in sorted(self.circuit.cells.mtypes)
                  if ipc.endswith("IPC")]
        assert self.adapted._translate_parameters_cells(
            {SYN_CLASS: ['EXC', 'INH'],
             MORPH_CLASS: ['PYR', 'INT'],
             MTYPE: ['MC', 'IPC'],
             LAYER: ['L1', 'L4', 'L6', 'L2'],
             COLUMN: ["mc1", "mc2"]}) ==\
            {bp.Cell.SYNAPSE_CLASS: ['EXC', 'INH'],
             bp.Cell.MORPH_CLASS: ['PYR', 'INT'],
             bp.Cell.LAYER: [1, 4, 6, 2],
             bp.Cell.MTYPE: allmc + allipc,
             bp.Cell.HYPERCOLUMN: [1, 2]}

    def test_mtypes(self):
        assert self.adapted.mtypes() == [
            {LAYER: 'L1', MTYPE: 'DAC'},
            {LAYER: 'L1', MTYPE: 'DLAC'},
            {LAYER: 'L1', MTYPE: 'HAC'},
            {LAYER: 'L1', MTYPE: 'NGC-DA'},
            {LAYER: 'L1', MTYPE: 'NGC-SA'},
            {LAYER: 'L1', MTYPE: 'SLAC'},
            {LAYER: ['L2', 'L3'], MTYPE: 'BP'},
            {LAYER: ['L2', 'L3'], MTYPE: 'BTC'},
            {LAYER: ['L2', 'L3'], MTYPE: 'ChC'},
            {LAYER: ['L2', 'L3'], MTYPE: 'DBC'},
            {LAYER: ['L2', 'L3'], MTYPE: 'LBC'},
            {LAYER: ['L2', 'L3'], MTYPE: 'MC'},
            {LAYER: ['L2', 'L3'], MTYPE: 'NBC'},
            {LAYER: ['L2', 'L3'], MTYPE: 'NGC'},
            {LAYER: ['L2', "L3"], MTYPE: 'PC'},
            {LAYER: ['L2', 'L3'], MTYPE: 'SBC'},
            {LAYER: 'L4', MTYPE: 'BP'},
            {LAYER: 'L4', MTYPE: 'BTC'},
            {LAYER: 'L4', MTYPE: 'ChC'},
            {LAYER: 'L4', MTYPE: 'DBC'},
            {LAYER: 'L4', MTYPE: 'LBC'},
            {LAYER: 'L4', MTYPE: 'MC'},
            {LAYER: 'L4', MTYPE: 'NBC'},
            {LAYER: 'L4', MTYPE: 'NGC'},
            {LAYER: 'L4', MTYPE: 'PC'},
            {LAYER: 'L4', MTYPE: 'SBC'},
            {LAYER: 'L4', MTYPE: 'SP'},
            {LAYER: 'L4', MTYPE: 'SS'},
            {LAYER: 'L5', MTYPE: 'BP'},
            {LAYER: 'L5', MTYPE: 'BTC'},
            {LAYER: 'L5', MTYPE: 'ChC'},
            {LAYER: 'L5', MTYPE: 'DBC'},
            {LAYER: 'L5', MTYPE: 'LBC'},
            {LAYER: 'L5', MTYPE: 'MC'},
            {LAYER: 'L5', MTYPE: 'NBC'},
            {LAYER: 'L5', MTYPE: 'NGC'},
            {LAYER: 'L5', MTYPE: 'SBC'},
            {LAYER: 'L5', MTYPE: 'STPC'},
            {LAYER: 'L5', MTYPE: 'TTPC1'},
            {LAYER: 'L5', MTYPE: 'TTPC2'},
            {LAYER: 'L5', MTYPE: 'UTPC'},
            {LAYER: 'L6', MTYPE: 'BP'},
            {LAYER: 'L6', MTYPE: 'BPC'},
            {LAYER: 'L6', MTYPE: 'BTC'},
            {LAYER: 'L6', MTYPE: 'ChC'},
            {LAYER: 'L6', MTYPE: 'DBC'},
            {LAYER: 'L6', MTYPE: 'IPC'},
            {LAYER: 'L6', MTYPE: 'LBC'},
            {LAYER: 'L6', MTYPE: 'MC'},
            {LAYER: 'L6', MTYPE: 'NBC'},
            {LAYER: 'L6', MTYPE: 'NGC'},
            {LAYER: 'L6', MTYPE: 'SBC'},
            {LAYER: 'L6', MTYPE: 'TPC_L1'},
            {LAYER: 'L6', MTYPE: 'TPC_L4'},
            {LAYER: 'L6', MTYPE: 'UTPC'}]

    def test_warns_missing_mtype(self):
        with pyt.warns(Warning):
            self.adapted._translate_parameters_cells({MTYPE: 'BAASDHAS'})

    def test_empty_lists(self):
        assert self.adapted._translate_parameters_cells(
            {SYN_CLASS: [], MORPH_CLASS: [], REGION: [],
             MTYPE: [], LAYER: []}) == {}

    def test_warns_region(self):
        with pyt.warns(Warning):
            self.adapted._translate_parameters_cells({REGION: 'SS'})
        pass


class TestConnectomeFunctions:
    """on proj1 rat O1"""

    circuit_config = "/gpfs/bbp.cscs.ch/project/proj1/circuits/"\
                     "SomatosensoryCxS1-v5.r0/O1/merged_circuit/"\
                     "CircuitConfig"
    circuit = bp.Circuit(circuit_config)
    with pyt.warns(Warning):
        adapted = CircuitAdapter(circuit_config)

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
        assert np.mean(self.adapted.connection_probability(
            {PRESYNAPTIC: {LAYER: "L4", MTYPE: "PC"},
             POSTSYNAPTIC: {LAYER: "L4", MTYPE: "MC"}})) ==\
            pyt.approx(exprob, rel=0.05)

    def test_conn_prob_empty_cells(self):
        assert np.isnan(self.adapted.connection_probability(
            {PRESYNAPTIC: {LAYER: "L1", MTYPE: ['PC']},
             POSTSYNAPTIC: {LAYER: "L2", MTYPE: ["CHC"]}}))

    def test_syns_per_conn(self):
        pre_group = {bp.Cell.MTYPE: ['L1_DAC']}
        post_group = {bp.Cell.MTYPE: ['L4_PC']}
        iterator = self.circuit.connectome.iter_connections(
            pre=pre_group, post=post_group, return_synapse_count=True)
        exp_syncounts = [conn[2] for conn in iterator]
        assert np.mean(self.adapted.synapses_per_connection(
            {PRESYNAPTIC: {LAYER: "L1", MTYPE: "DAC"},
             POSTSYNAPTIC: {LAYER: "L4", MTYPE: "PC"}})) ==\
            pyt.approx(np.mean(exp_syncounts), rel=0.05)

    def test_pathway_synapses(self):
        pre_group = {bp.Cell.MTYPE: ['L4_BP']}
        post_group = {bp.Cell.MTYPE: ['L23_PC']}
        exp_synapses = len(self.circuit.connectome.pathway_synapses(
            pre=pre_group, post=post_group))

        assert self.adapted.pathway_synapses(
            {PRESYNAPTIC: {LAYER: "L4", MTYPE: "BP"},
             POSTSYNAPTIC: {LAYER: ["L2", "L3"], MTYPE: "PC"}}) ==\
            exp_synapses