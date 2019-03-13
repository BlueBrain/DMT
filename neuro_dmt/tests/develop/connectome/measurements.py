"""test develop connectome measurement methods."""

import numpy as np
import pandas as pd
from bluepy.v2.enums import Cell

def get_connection_probability(
        circuit,
        pre_mtype,
        post_mtype,
        distance_bins,
        region=None):
    """Get connection probability as a function of distance.
    """
    def __get_soma_distance(
            pre_gid,
            post_gid):
        """..."""
        positions=\
            circuit.cells.positions([
                pre_gid, post_gid])
        return np.linalg.norm(
            positions.iloc[0] - positions.iloc[1])

    pre_cell_type={
        Cell.MTYPE: pre_mtype}
    post_cell_type={
        Cell.MTYPE: post_mtype}
    if region:
        pre_cell_type.update({
            "region": region})
        post_cell_type.update({
            "region": region})
    pre_gids=\
        circuit.cells.ids(
            pre_cell_type)
    post_gids=\
        circuit.cells.ids(
            post_cell_type)
    connections=\
        circuit.connectome\
               .iter_connections(
                   pre_cell_type,
                   post_cell_type)
    connected_distances=\
        np.array([
            __get_soma_distance(pre_gid, post_gid)
            for pre_gid, post_gid in connections])
    all_distances=\
        np.array([
            __get_soma_distance(pre_gid, post_gid)
            for pre_gid in pre_gids
            for post_gid in post_gids])
    connected_distance_bins=\
        np.histogram(
            connected_distances,
            bins=distance_bins)
    all_distance_bins=\
        np.histogram(
            all_distances,
            bins=distance_bins)
    return{
        "mean": connected_distance_bins / all_distance_bins,
        "std": np.sqrt(connected_distance_bins) / all_distance_bins}


