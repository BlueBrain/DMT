"""
Test develop pathway properties.
"""

from collections import OrderedDict
import numpy as np
import pandas as pd
from ..model import BlueBrainCircuitModel
from .import get_path_circuit

circuit_label = "S1RatSSCxDisseminationBio1"
circuit_model = BlueBrainCircuitModel(
    path_circuit_data=get_path_circuit(circuit_label))



"""
Test the use of pandas Series as a pathway.
"""
cell_types = pd.DataFrame(OrderedDict([
    ("mtype", ["L23_MC", "L1_DAC", "L1_BP", "L23_MC"]),
    ("etype", ["bNAC", "dNAC", "NAC", "NAC"])]))
cell_type_specifiers = tuple(cell_types.columns.values)
assert cell_type_specifiers == ("mtype", "etype")
pre_cell_types = pd.DataFrame(
    cell_types.values,
    columns=pd.MultiIndex.from_tuples(
        [("pre", value) for value in cell_types.columns]))
number_pre_types = pre_cell_types.shape[0]
post_cell_types = pd.DataFrame(
    cell_types.values,
    columns=pd.MultiIndex.from_tuples(
        [("post", value) for value in cell_types.columns]))
number_post_types = post_cell_types.shape[0]
pathways_example = pd.DataFrame(
    [pre_cell_type.append(post_cell_type)
     for _, pre_cell_type in pre_cell_types.iterrows()
     for _, post_cell_type in post_cell_types.iterrows()],
    index=range(number_pre_types * number_post_types))

pathways_circuit = circuit_model.get_pathways(("mtype", ))


