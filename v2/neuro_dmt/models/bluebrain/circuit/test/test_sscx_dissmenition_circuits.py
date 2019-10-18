"""
Test using SSCx dissemination circuits.
"""

from .import BlueBrainCircuitAnalysisTest

def test_adapter_methods():
    """
    Test adapter methods.
    """
    tester = BlueBrainCircuitAnalysisTest()
    tester.test_adapter_methods("S1RatSSCxDisseminationBio1")
