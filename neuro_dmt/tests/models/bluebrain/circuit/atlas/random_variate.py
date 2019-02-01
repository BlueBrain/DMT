"""Test develop random variates for the Atlas based circuit.
Methods tested here will find their way into AtlasCircuitGeometry..."""
from bluepy.v2.circuit import Circuit
from bluepy.v2.enums import Cell
import numpy as np

circuit\
    = Circuit(
        '/gpfs/bbp.cscs.ch/project/proj42/circuits/O1/20180904/CircuitConfig')

def get_atlas_ids(
        hierarchy,
        column_index,
        *layers):
    """..."""
    if not layers:
        return hierarchy.collect(
            "acronym", "mc{}".format(column_index), "id")
    return {
        id for layer in layers
        for id in hierarchy.collect(
                "acronym", "mc{};{}".format(column_index, layer), "id")}

def get_cell_density(
        circuit,
        column_index,
        layers=[],
        cell_type={}):
    """..."""
    hierarchy\
        = circuit.atlas.load_hierarchy()
    brain_regions\
        = circuit.atlas.load_data(
            "brain_regions")
    column_atlas_ids\
        = get_atlas_ids(
            hierarchy,
            column_index)
    column_cell_query\
        = {k: v for k, v in cell_type.items()}
    column_cell_query.update({
        Cell.REGION: "@mc{}.*".format(column_index)})
    column_cells\
        = circuit.cells.ids(column_cell_query)
    if not layers:
        return (1.e6 *
                len(column_cells) /
                brain_regions.volume(
                    column_atlas_ids))
    layers_atlas_ids\
        = get_atlas_ids(hierarchy, column_index, *layers)
    
    def __layer_cell_query(layer):
        """..."""
        layer_cell_query\
            = {k: v for k, v in cell_type.items()}
        layer_cell_query.update({
            "layer": layer})
        return layer_cell_query

    layers_cells\
        = [gid for layer in layers
           for gid in circuit.cells.ids(
                   __layer_cell_query(
                   layer))]
    column_layer_atlas_ids\
        = column_atlas_ids.intersection(
        layers_atlas_ids)
    column_layer_cells\
        = np.intersect1d(
            column_cells,
    layers_cells)
    return(1.e6 *
           len(column_layer_cells) /
           brain_regions.volume(
               column_layer_atlas_ids))
