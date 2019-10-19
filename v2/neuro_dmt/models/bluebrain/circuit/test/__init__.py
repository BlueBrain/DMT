"""
Test `BlueBrainCircuitModel`, `BlueBrainAdapter`, and `BrainCircuitAnalysis`
with some "real-world" test-cases.
"""
import os
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
    path_gpfs_project,\
    CircuitAnalysisTest
from ..model import BlueBrainCircuitModel
from ..adapter import BlueBrainCircuitAdapter

def get_path_circuit(label):
    availabel_circuits = {
        "O1MouseSSCx": path_gpfs_project(
            66, "circuits", "O1", "20180305"),
        "O1RatSSCxDissemination": path_gpfs_project(
            62, "Circuits", "O1", "20190912_spines"),
        "S1RatSSCxDisseminationBio0": path_gpfs_project(
            64, "dissemination", "circuits",
            "S1", "juvenile", "L23_MC_BTC_shifted_down",
            "Bio_0", "20190902"),
        "S1RatSSCxDisseminationBio1": path_gpfs_project(
            64, "dissemination", "circuits",
            "S1", "juvenile", "L23_MC_BTC_shifted_down",
            "Bio_1", "20190903"),
        "S1RatSSCxDisseminationBio2": path_gpfs_project(
            64, "dissemination", "circuits",
            "S1", "juvenile", "L23_MC_BTC_shifted_down",
            "Bio_2", "20190925"),
        "S1RatSSCxDisseminationBioM": path_gpfs_project(
            64, "dissemination", "circuits",
            "S1", "juvenile", "L23_MC_BTC_shifted_down",
            "Bio_M", "20190925")}
    return availabel_circuits[label]


class BlueBrainCircuitAnalysisTest(WithFields):
    """
    Test `BlueBrainCircuitModel` and `BlueBrainCircuitAdapter` with circuits.
    """
    adapter = Field(
        """
        The adapter to use for analysis.
        By default, these tests will use `BlueBrainCircuitAdapter`.
        """,
        __default_value__=BlueBrainCircuitAdapter())

    def __init__(self, *args, **kwargs):
        """
        Initialize Me.
        """
        self._circuit_analysis_test = CircuitAnalysisTest(*args, **kwargs)
        super().__init__(*args, **kwargs)


    def __getattribute__(self, name_attr):
        """
        Delegate `test_` methods.
        """
        try:
            return object.__getattribute__(self, name_attr)
        except AttributeError as error:
            if name_attr.split('_')[0] != "test":
                raise error

        if not hasattr(self._circuit_analysis_test, name_attr):
            raise AttributeError(
                "'{}' object has no attribute {}"\
                .format(__class__.__name__, name_attr))

        def _wrapped(circuit_model, *args, **kwargs):
            """..."""
            return getattr(
                self._circuit_analysis_test,
                name_attr
            )(
                circuit_model, self.adapter, *args, **kwargs)

        return _wrapped

                    

    def test_circuit_model(self, circuit_label,  *args, **kwargs):
        """
        `BlueBrainCircuitModel` should be able to load circuit data.
        """
        circuit_model = BlueBrainCircuitModel(
            path_circuit_data=get_path_circuit(circuit_label))
        path = circuit_model.get_path("jinga")
        dir = os.path.dirname(path)
        assert dir == get_path_circuit(circuit_label).as_posix()
