"""
Test `BlueBrainCircuitModel` with mock circuit.
"""

from ...model import BlueBrainCircuitModel
from ..circuit import MockCircuit
from .import circuit_composition, circuit_connectivity

def test_model():
    """
    `BlueBrainCircuitModel` should be able to load the mock circuit. 
    """
    mock_circuit =\
        MockCircuit.build(
            circuit_composition,
            circuit_connectivity)
    circuit_model = BlueBrainCircuitModel(
        mock_circuit,
        label="BlueBrainMockCircuitModel")
