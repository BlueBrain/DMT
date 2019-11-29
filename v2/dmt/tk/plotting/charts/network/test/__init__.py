"""
Test network charts
"""
import os
from collections import defaultdict
import numpy as np
import pandas as pd
from bluepy.v2.circuit import Circuit
from bluepy.v2.enums import Cell, Synapse
import matplotlib.pyplot as plt
from dmt.tk.plotting.shapes import Circle, Arc, PolarPoint
from dmt.tk.plotting.charts.network import CircularNetworkChart

circuit_config = os.path.join(
    "/gpfs/bbp.cscs.ch/project/proj64/dissemination",
    "circuits/S1/juvenile/L23_MC_BTC_shifted_down/Bio_1/20190903",
    "CircuitConfig")
circuit = Circuit(circuit_config)
connectome = circuit.connectome
cells = circuit.cells.get()

assert cells.shape[0] > 1.6e6, cells.shape

mtypes = cells.mtype.unique()

assert len(mtypes) == 60, len(mtypes)

sample_size = 2

gids =\
    pd.concat([
        pd.DataFrame({
            "gid": circuit.cells.ids({"mtype": mtype}),
            "mtype": mtype})\
        .sample(sample_size)
        for mtype in mtypes])
assert gids.shape[0] == sample_size * 60, gids.shape


def get_efferent_synapse_counts(cell):
    """..."""
    synapse_counts = connectome\
        .efferent_synapses(
            cell.gid,
            properties=Synapse.POST_GID)\
        .value_counts()\
        .rename("synapse_count")
    pre_mtypes = pd.Series(
        synapse_counts.shape[0] * [cell.mtype],
        index=synapse_counts.index,
        name="pre_mtype")
    post_mtypes = circuit.cells\
        .get(
            group=synapse_counts.index.values,
            properties=Cell.MTYPE)\
        .rename("post_mtype")
    return pd\
        .concat(
            [pre_mtypes, post_mtypes, synapse_counts],
            axis=1)\
        .set_index(["pre_mtype", "post_mtype"])

efferent_synapses = gids.apply(
    lambda cell: connectome.efferent_synapses(
        cell.gid,
        properties=Synapse.POST_GID),
    axis=0)

assert False, efferent_synapses.shape
