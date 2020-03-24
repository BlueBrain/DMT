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

