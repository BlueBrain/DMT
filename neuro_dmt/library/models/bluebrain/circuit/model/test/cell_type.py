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
Test develop CellType.
"""
import pandas as pd
from neuro_dmt.models.bluebrain.circuit.model.cell_type import CellType

def test_cell_types():
    """
    `CellType` should initialize from a `dict` or a `pandas.Series`,
    and should evaluate specifiers.
    """
    expected_specifiers = frozenset(("mtype", "layer", "etype"))


    cell_types = (
        CellType(dict(
            (("mtype", "L23_MC"), ("layer", "L3"),     ("etype", "bNAC")))),
        CellType(dict(
            (("mtype", "L23_MC"), ("etype", "bNAC"),   ("layer", "L3")))),
        CellType(dict(
            (("layer", "L3"),     ("mtype", "L23_MC"), ("etype", "bNAC")))),
        CellType(dict(
            (("layer", "L3"),     ("etype", "bNAC"),   ("mtype", "L23_MC")))),
        CellType(dict(
            (("etype", "bNAC"),   ("mtype", "L23_MC"), ("layer", "L3")))),
        CellType(dict(
            (("etype", "bNAC"),   ("layer", "L2"),     ("mtype", "L23_MC")))))

    for cell_type in cell_types:
        assert isinstance(cell_type.value, pd.Series)
        assert len(cell_type.value) == 3
    
        assert cell_types[0].specifier == expected_specifiers,\
            cell_types[1].specifier
        assert cell_types[1].specifier == expected_specifiers,\
            cell_types[2].specifier
        assert cell_types[2].specifier == expected_specifiers,\
            cell_types[3].specifier
        assert cell_types[3].specifier == expected_specifiers,\
            cell_types[4].specifier
        assert cell_types[4].specifier == expected_specifiers,\
            cell_types[5].specifier
        assert cell_types[5].specifier == expected_specifiers,\
            cell_types[6].specifier

    cell_types = (
        CellType(pd.Series(
            ["L23_MC", "L3", "bNAC"], index=["mtype", "layer", "etype"])),
        CellType(pd.Series(
            ["L23_MC", "bNAC", "L3"], index=["mtype", "etype", "layer"])),
        CellType(pd.Series(
            ["L3", "L23_MC", "bNAC"], index=["layer", "mtype", "etype"])),
        CellType(pd.Series(
            ["L3", "bNAC", "L23_MC"], index=["layer", "etype", "mtype"])),
        CellType(pd.Series(
            ["bNAC", "L23_MC", "L3"], index=["etype", "mtype", "layer"])),
        CellType(pd.Series(
            ["bNAC", "L3", "L23_MC"], index=["etype", "layer", "mtype"])))

    for cell_type in cell_types:
        assert isinstance(cell_type.value, pd.Series)
        assert len(cell_type.value) == 3
    
        assert cell_types[0].specifier == expected_specifiers,\
            cell_types[1].specifier
        assert cell_types[1].specifier == expected_specifiers,\
            cell_types[2].specifier
        assert cell_types[2].specifier == expected_specifiers,\
            cell_types[3].specifier
        assert cell_types[3].specifier == expected_specifiers,\
            cell_types[4].specifier
        assert cell_types[4].specifier == expected_specifiers,\
            cell_types[5].specifier
        assert cell_types[5].specifier == expected_specifiers,\
            cell_types[6].specifier
        
def test_cell_type_pathway():
    """
    `CellType` should be able to compute a pathway,
    with or without a `pandas.MultiIndex`.
    """
    pathway =\
        CellType.pathway(
            {"mtype": "L23_MC"},
            {"mtype": "L23_MC"})
    assert pathway.pre_synaptic.mtype == "L23_MC", pathway
    assert pathway.post_synaptic.mtype == "L23_MC", pathway

    pathway =\
        CellType.pathway(
            {"mtype": "L23_MC"},
            {"mtype": "L23_MC"},
            multi_indexed=False)
    assert pathway.pre_synaptic_mtype == "L23_MC", pathway
    assert pathway.post_synaptic_mtype == "L23_MC", pathway

    

    

