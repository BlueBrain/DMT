# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

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
