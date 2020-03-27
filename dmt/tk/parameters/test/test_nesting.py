# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Test nesting, unnesting
"""

import pandas as pd
import pytest as pyt
from ..import index_tree

def test_unnesting():
    """
    `index_tree.as_unnested_tree` should be able to flatten the keys
    of a nested dict.
    """
    nested_dict = dict(
        x0=dict(
            y0=dict(z0=0, z1=1),
            y1=dict(z0=2, z1=3)),
        x1=dict(
            y0=dict(z0=4, z1=5),
            y1=dict(z0=6, z1=7)))
    unnested_dict = index_tree.as_unnested_dict(nested_dict)
    assert ("x0", "y0", "z0") in unnested_dict
    assert unnested_dict[("x0", "y0", "z0")] == 0
    assert ("x0", "y0", "z1") in unnested_dict
    assert unnested_dict[("x0", "y0", "z1")] == 1
    assert ("x0", "y1", "z0") in unnested_dict
    assert unnested_dict[("x0", "y1", "z0")] == 2
    assert ("x0", "y1", "z1") in unnested_dict
    assert unnested_dict[("x0", "y1", "z1")] == 3
    assert ("x1", "y0", "z0") in unnested_dict
    assert unnested_dict[("x1", "y0", "z0")] == 4
    assert ("x1", "y0", "z1") in unnested_dict
    assert unnested_dict[("x1", "y0", "z1")] == 5
    assert ("x1", "y1", "z0") in unnested_dict
    assert unnested_dict[("x1", "y1", "z0")] == 6
    assert ("x1", "y1", "z1") in unnested_dict
    assert unnested_dict[("x1", "y1", "z1")] == 7

def test_nested_dict_from_multi_level_indexed_series():
    """
    `index_tree.as_nested_dict(...)` should return a nested dict for properly
    formed pandas.Series with a multi-level index.
    """
    empty_key_level_0 =\
        pd.Series({
            ("pre_synaptic", "mtype"): "L23_MC",
            ("pre_synaptic", "etype"): "bNAC",
            ("post_synaptic", "mtype"): "L6_TPC:A",
            ("post_synaptic", "etype"): "bNAC",
            ("soma_distance", ""): 500.})
    nested_dict =\
        index_tree.as_nested_dict(
            empty_key_level_0)
    assert "pre_synaptic" in nested_dict
    assert "mtype" in nested_dict["pre_synaptic"]
    assert nested_dict["pre_synaptic"]["mtype"] == "L23_MC"
    assert "etype" in nested_dict["pre_synaptic"]
    assert nested_dict["pre_synaptic"]["etype"] == "bNAC"

    assert "post_synaptic" in nested_dict
    assert "mtype" in nested_dict["post_synaptic"]
    assert nested_dict["post_synaptic"]["mtype"] == "L6_TPC:A"
    assert "etype" in nested_dict["post_synaptic"]
    assert nested_dict["post_synaptic"]["etype"] == "bNAC"

    assert "soma_distance" in nested_dict
    assert nested_dict["soma_distance"] == 500.

    second_level_empty_key =\
        pd.Series(
            [500., "test_value"],
            index=pd.MultiIndex.from_tuples(
                [("soma_distance", ""),
                 ("soma_distance", "test_key")]))

    with pyt.raises(TypeError):
        index_tree.as_nested_dict(second_level_empty_key)
