"""
Test `BlueBrainCircuitModel` and `BlueBrainCircuitAdapter` with composition
analyses and validations.
"""

from ..import BlueBrainCircuitAnalysisTest

def test_cell_density():
    """
    Should be able to analyze cell densities.
    """
    circuit_path = BlueBrainCircuitAnalysisTest.path_circuit["O1RatSSCxDissemination"]
    circuit_model = BlueBrainCircuitModel(path_circuit=circuit_path)
    adapter = 
