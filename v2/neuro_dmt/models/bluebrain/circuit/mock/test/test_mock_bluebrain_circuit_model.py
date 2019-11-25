"""
Test atlas dependent methods in the mock for `BlueBrainCircuitModel`
"""
import numpy as np
import pandas as pd
from dmt.tk.journal import Logger
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.parameters import Parameters
from dmt.tk.plotting import Bars, HeatMap, LinePlot
from dmt.data.observation import measurement
from neuro_dmt.analysis.circuit import BrainCircuitAnalysis
from neuro_dmt.analysis.circuit.connectome.interfaces import\
    ConnectionProbabilityInterface,\
    ConnectionProbabilityBySomaDistanceInterface,\
    AfferentConnectionCountBySomaDistanceInterface,\
    AfferentConnectionCountInterface
from ...mock.circuit import MockBlueBrainCircuitModel
from ...mock.test.mock_circuit_light import\
    circuit_composition,\
    circuit_connectivity
from ...model import BlueBrainCircuitModel
from ...model.cell_type import CellType
from ...adapter import BlueBrainCircuitAdapter

logger = Logger(client="test connectome analysis.")

def test_atlas_method_mocks():
    """
    Mock for the `BlueBrainCircuitModel` should handle methods that would
    be delegated to an atlas by a real instance.
    """
    mock_circuit_model =\
        MockBlueBrainCircuitModel(
            circuit_composition,
            circuit_connectivity,
            label="BlueBrainCircuitModelMockLight")
    n_cells = mock_circuit_model.cells.shape[9]
    assert np.int32(mock_circuit_model.voxel_cell_count.sum()) == n_cells



