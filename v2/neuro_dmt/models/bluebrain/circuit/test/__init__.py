"""
Test `BlueBrainCircuitModel`, `BlueBrainAdapter`, and `BrainCircuitAnalysis`
with some "real-world" test-cases.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from dmt.tk.parameters import Parameters
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.utils import get_label
from dmt.tk.field import\
    Field,\
    LambdaField,\
    lazyfield,\
    WithFields
from dmt.tk.phenomenon import\
    Phenomenon
from dmt.tk.parameters import\
    Parameters
from dmt.tk.plotting.bars import Bars
from neuro_dmt import terminology
from neuro_dmt.analysis.circuit.composition.interfaces import\
    CellDensityAdapterInterface
from neuro_dmt.analysis.circuit import\
    BrainCircuitAnalysis
from neuro_dmt.analysis.circuit.composition.interfaces import\
    CellDensityAdapterInterface
from neuro_dmt.analysis.circuit.test import\
    CircuitAnalysisTest
from ..model import BlueBrainCircuitModel
from ..adapter import BlueBrainCircuitAdapter


class BlueBrainCircuitAnalysisTest(CircuitAnalysisTest):
    """
    Test `BlueBrainCircuitModel` and `BlueBrainCircuitAdapter` with circuits.
    """
    adapter = Field(
        """
        The adapter to use for analysis.
        By default, these tests will use `BlueBrainCircuitAdapter`.
        """,
        __default_value__=BlueBrainCircuitAdapter())

    get_path_circuit = {
        "O1MouseSSCx": path_gpfs_project(
            66, "circuits", "O1", "20180305"),
        "O1RatSSCxDissemination": path_gpfs_project(
            62, "Circuits", "O1", "20190912_spines"),
        "S1RatSSCxDisseminationBio0": path_gpfs_project(
            64, "dissemination", "circuits"
            "S1", "juvenile", "L23_MC_BTC_shifted_down",
            "Bio_0", "20190902"),
        "S1RatSSCxDisseminationBio1": path_gpfs_project(
            64, "dissemination", "circuits"
            "S1", "juvenile", "L23_MC_BTC_shifted_down",
            "Bio_1", "20190903"),
        "S1RatSSCxDisseminationBio2": path_gpfs_project(
            64, "dissemination", "circuits"
            "S1", "juvenile", "L23_MC_BTC_shifted_down",
            "Bio_2", "20190925"),
        "S1RatSSCxDisseminationBioM": path_gpfs_project(
            64, "dissemination", "circuits"
            "S1", "juvenile", "L23_MC_BTC_shifted_down",
            "Bio_M", "20190925")}

    def test_adapter_methods(self, label_circuit, *args, **kwargs):
        """
        Test the methods defined in `BlueBrainCircuitAdapter`.
        """
        circuit_model =\
            BlueBrainCircuitModel(
                get_path_circuit[label_circuit])
        cell_density =\
            self.adapter.get_cell_density(
                circuit_model,
                layer="L1",
                method=terminology.measurement_method.exhaustive)

        assert isinstance(cell_density, (float, np.float))

        assert cell_density > 0., cell_density


