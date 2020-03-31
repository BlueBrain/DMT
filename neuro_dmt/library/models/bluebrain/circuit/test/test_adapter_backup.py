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
Test adapter for Blue Brain circuit models.
"""

import numpy
import pandas
from dmt.tk.plotting.bars import Bars
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.parameters import Parameters
from dmt.tk.collections import take
from neuro_dmt.models.bluebrain.circuit import BlueBrainCircuitModel
from neuro_dmt.models.bluebrain.circuit.adapter import BlueBrainModelAdapter
from neuro_dmt.models.bluebrain.circuit.mock.adapter import MockCircuitAdapter
from neuro_dmt.analysis.circuit import BrainCircuitAnalysis
from neuro_dmt.analysis.circuit.composition.interfaces\
    import CellDensityAdapterInterface
from neuro_dmt.terminology import method
from . import path_circuit, expect_equal

cell_density_phenomenon =\
    Phenomenon(
        "Cell Density",
        "Count of cells in a unit volume.",
        group="composition")
cell_density_analysis =\
    BrainCircuitAnalysis(
        phenomenon=cell_density_phenomenon,
        AdapterInterface=CellDensityAdapterInterface,
        measurement_parameters=Parameters(
            pandas.DataFrame({"layer": ["L1", "L2", "L3", "L4", "L5", "L6"]})),
        plotter=Bars(
            xvar="layer",
            xlabel="Layer",
            yvar=cell_density_phenomenon.label,
            ylabel=cell_density_phenomenon.name))

def test_RatSSCxDiss_cell_density_analysis():
    """
    Test cell density analysis on the Rat SSCx dissemination model.
    """
    circuit_path = path_circuit["S1RatSSCxDiss"]
    circuit_model = BlueBrainCircuitModel(path_circuit_data=circuit_path)
    adapter = BlueBrainModelAdapter(circuit_model=circuit_model)

    cell_density = numpy.mean([
        adapter.get_cell_density(
            layer="L1",
            method=method.OVERALL)
        for _ in range(1000)])
    assert cell_density > 0.,\
        """
        Cell density in layer 1 of the primary somatosensory cortex
        cannot be 0. or negative: {}
        """.format(cell_density)

    brain_region_ids =\
        circuit_model.atlas.region_layer.get_ids(layer="L1")
            
    def _get_cell_brain_region(cell):
        voxel_indices =\
            circuit_model.atlas.voxel_data.positions_to_indices(
                [cell.x, cell.y, cell.z])
        return circuit_model.atlas.brain_regions[
            voxel_indices[0], voxel_indices[1], voxel_indices[2]]
    for roi in take(10, adapter.random_region_of_interest(
            circuit_model, layer="L1")):
        cells = circuit_model.get_cells_in_region(roi)
        cell_position_voxel_ids = {
            _get_cell_brain_region(cell)
            for _, cell in cells.iterrows()}
        assert len(brain_region_ids.intersection(cell_position_voxel_ids)),\
            "At least one cell id {} should be in L1 brain ids {}".format(
                cell_position_voxel_ids,
                brain_region_ids)

    cell_density_analysis.adapter = adapter
    cell_density_measurement =\
        cell_density_analysis.get_measurement(circuit_model)
    cell_density_summary = cell_density_measurement\
        .groupby("layer")\
        .agg(["mean", "std"])\
        .cell_density
    cell_density_mean = cell_density_summary["mean"]
    index_values = cell_density_summary\
        .sort_values(by="mean")\
        .index\
        .values
    assert index_values[0] == "L1"

    expect_equal(
        index_values[0], "L1")
    assert cell_density_mean["L1"] < cell_density_mean["L2"]
    assert cell_density_mean["L2"] > cell_density_mean["L3"]
    assert cell_density_mean["L3"] < cell_density_mean["L4"]
    assert cell_density_mean["L4"] > cell_density_mean["L5"]
    assert cell_density_mean["L5"] < cell_density_mean["L6"]
