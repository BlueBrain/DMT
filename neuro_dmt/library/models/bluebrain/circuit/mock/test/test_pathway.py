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
Test develop pathway property.
"""
import pandas as pd

def test_cell_group_resolution():
    """
    `PathwayProperty` should be able to resolve cell groups.
    """
    mtypes = ["L1_SBC", "L23_MC", "L4_TPC", "L5_SBC", "L6_UPC"]
    cells = pd\
        .DataFrame([
            {"mtype": mtype, "gid": range(100)
             for mtype in mtypes}])\
        .set_index("gid")
         
    pre_synaptic_cell_specifier = ("mtype",)
    post_synaptic_cell_specifier = ("mtype",)

    pre_synaptic_cells = pathway_property._resolve_cell_group(pre_synaptic_cell_specifier)

