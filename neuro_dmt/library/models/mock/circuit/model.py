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
Circuit specific code.
"""
import numpy as np
import pandas as pd
from dmt.tk.journal import Logger
from dmt.tk.field import Field, Record, lazyfield, WithFields
from neuro_dmt import terminology
from neuro_dmt.utils.geometry.roi import Cuboid
from neuro_dmt.analysis.reporting import CircuitProvenance
from .cell import CellCollection
from .connectome import Connectome

from .composition import CircuitComposition
from .builder import CircuitBuilder

LOGGER = Logger(client=__file__)

def build(composition, connectivity):
    """
    Build a circuit with given 'composition', and 'connectivity'.
    Parameters
    composition :: An object parameterizing a circuit's composition.
    connectivity :: An object parameterizing a circuit's connectivity
    """

    LOGGER.status("Build a Mock Circuit.")
        
    circuit_builder =\
        CircuitBuilder(
            composition=composition,
            connectivity=connectivity)
    cell_collection =\
        circuit_builder.get_cell_collection()
    return Record(
        cells=cell_collection,
        connectome=circuit_builder.get_connectome(cell_collection))


class MockCircuitModel(WithFields):
    """
    A class to mock `BlueBrainCircuitModel`.
    This mock overrides atlas related methods, plugging in mock methods
    instead of invoking them on atlas which does not exist for a mock-circuit.
    """
    voxel_dimensions = Field(
        """
        A 3D np.ndarray that provides dimensions of a mock atlas voxel data.
        """,
        __default_value__=50. * np.ones(3))

    def __init__(self,
            circuit_composition,
            circuit_connectivity,
            label="MockCircuitModel"):
        """..."""

        super().__init__(
            build(circuit_composition, circuit_connectivity),
            label=label,
            provenance=CircuitProvenance(
                label=label,
                authors=["Vishal Sood"],
                release_date="Not Applicable",
                uri=__file__,
                animal="Wistar Rat",
                age="P14",
                brain_region="SSCx"))

    @lazyfield
    def brain_regions(self):
        """
        `BlueBrainCircuit` will invoke its atlas to get layers.
        However, atlas is not defined for the mock circuit.
        """
        return self.cell_collection.regions

    @lazyfield
    def layers(self):
        """
        `BlueBrainCircuit` will invoke its atlas to get layers.
        However, atlas is not defined for the mock circuit.
        """
        def __add_prefix(layer):
            if isinstance(layer, (int, np.int)) or layer[0] != 'L':
                return "L{}".format(layer)
        return tuple(
            __add_prefix(layer) for layer in self.cell_collection.layers)

    @lazyfield
    def voxel_offset(self):
        """
        Minimum values of cell positions x, y, z components.
        """
        return np.floor(
            np.min(self.cells[[
                terminology.bluebrain.cell.x,
                terminology.bluebrain.cell.y,
                terminology.bluebrain.cell.z]])
        ).values

    @lazyfield
    def atlas(self):
        """
        Mock atlas for a mock circuit model.
        """
        raise AttributeError(
            """
            Atlas not defined for a mock circuit.
            """)

    def _positions_to_indices(self, positions):
        """
        A method defined on VoxelData.
        We need it here to mock a circuit atlas
        """
        return np.int32(np.floor(
            (positions - self.voxel_offset) / self.voxel_dimensions
        ))

    @lazyfield
    def voxel_data_shape(self):
        """..."""
        return self._positions_to_indices(
            np.max(self.cells[
                [CellProperty.X, CellProperty.Y, CellProperty.Z]
            ]).values
        ) + 1

    @lazyfield
    def voxel_cell_count(self):
        """
        Mock count of cells in each voxel of a mock atlas.
        """
        xyz = [CellProperty.X, CellProperty.Y, CellProperty.Z]
        positions = self.cells[xyz].values
        indices = [tuple(ijk) for ijk in self._positions_to_indices(positions)]
        voxel_counts = pd.Series(
            indices
        ).value_counts(
        ).reset_index(
        ).rename(
            columns={
                "index": "voxel_index",
                0: "number"
            }
        )
        voxel_count_array = np.zeros(self.voxel_data_shape)
        indices_count_array = tuple(
            np.array(
                list(voxel_counts.voxel_index.values)
            ).transpose()
        )
        voxel_count_array[indices_count_array] = voxel_counts.number.values
        return voxel_count_array

    @lazyfield
    def voxel_indexed_cell_gids(self):
        """
        A pandas series mapping a cell's gid to it's mocked voxel index.
        """
        xyz = [CellProperty.X, CellProperty.Y, CellProperty.Z]
        return pd.Series(
            self.cells.index.values,
            index=pd.MultiIndex.from_tuples(
                [tuple(ijk) 
                 for ijk in self._positions_to_indices(self.cells[xyz].values)],
                names=xyz)
        )
    def _atlas_value(self, key, value):
        """
        Value of a query parameter as understood by a mocked atlas.
        """
        return value

    def get_mask(self, query):
        """
        Get mask for a spatial query from a mocked atlas.
        """
        mask = np.zeros(self.voxel_data_shape, dtype=bool)
        mask[np.where(self.voxel_cell_count)] = True
        return mask

    def get_voxel_positions(self, voxel_ids):
        """..."""
        return pd.DataFrame(
            self.voxel_offset + self.voxel_dimensions * voxel_ids,
            columns=[CellProperty.X, CellProperty.Y, CellProperty.Z],
            index=pd.MultiIndex.from_arrays(
                [voxel_ids[:,0], voxel_ids[:, 1], voxel_ids[:, 2]],
                names=["i", "j", "k"]))

    @lazyfield
    def volume_voxel(self):
        return 100.

    def get_voxel_count(self, **spatial_query):
        """..."""
        mean = 2000 * 200 * 200 #um
        stdev = np.sqrt(mean)
        return np.random.normal(mean, stdev) / self.volume_voxel

    def get_thickness(self, *args, **kwargs):
        """..."""
        return\
            pd.DataFrame({
                layer:  np.random.uniform(0., 2000./3., size=1000)
                for layer in self.layers})
