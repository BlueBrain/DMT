"""
Test develop the behavior of CircuitAtlas
"""

from . import *

def test_S1RatSSCxDiss():
    """
    Test Rat SSCx Dissemination atlas.
    """
    name_atlas = "S1RatSSCxDiss"
    circuit_atlas_test =\
        CircuitAtlasTest(
            label=name_atlas,
            path_atlas=path_atlas[name_atlas],
            regions_to_test=[("SSp-ll", "S1HL"), ("SSp-ul", "S1FL")],
            layers_to_test=[("L1", "@L1"), ("L2", "@L2")])
    circuit_atlas_test("random_positions")

def test_S1MouseNeoCx():
    """
    Test Mouse Neo-cortex atlas.
    """
    name_atlas = "S1MouseNeoCx"
    circuit_atlas_test =\
        CircuitAtlasTest(
            label=name_atlas,
            path_atlas=path_atlas[name_atlas],
            regions_to_test=[("SSp-ll", "SSp-ll"), ("SSp-ul", "SSp-ul")],
            layers_to_test=[("L1", "@.*1"), ("L2", "@.*2")])
    circuit_atlas_test("random_positions")
