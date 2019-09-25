"""
Use mocks to test.
"""
import pandas
from ..mock import *
from ..mock.test_develop import *
from ..model import BlueBrainCircuitModel


def get_mock_circuit_model():
    mock_circuit = MockCircuit\
        .build(
            composition=circuit_composition,
            connectivity=circuit_connectivity)
    return BlueBrainCircuitModel(circuit=mock_circuit)

