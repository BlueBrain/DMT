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
Code to document and deal with a circuit atlas.
"""

import os
from collections import OrderedDict
import numpy
import pandas
from voxcell.nexus.voxelbrain import Atlas
from dmt.tk import collections
from dmt.tk.field import Field, lazyfield, WithFields
from neuro_dmt import terminology
from neuro_dmt.terminology.atlas import translate
from .region_layer import RegionLayer
from .principal_axis import PrincipalAxis


X = terminology.circuit.position.x
Y = terminology.circuit.position.y
Z = terminology.circuit.position.z


class BlueBrainCircuitAtlas(WithFields):
    """
    Document all the artefacts that define a circuit atlas,
    and provide tools to load them and work with them.
    """

    path = Field(
        """
        Path to the directory that holds the circuit atlas data.
        This path may be a URL.
        A value is required if a base `Atlas` instance is not passed
        to the initializer.
        """,
        __required__=False)

    def __init__(self,
            base_atlas=None,
            *args, **kwargs):
        """..."""
        if base_atlas is not None:
            self._base_atlas = base_atlas
        super().__init__(*args, **kwargs)

    @lazyfield
    def base_atlas(self):
        """
        `Atlas` instance to load the data.
        """
        return Atlas.open(self.path)

    @lazyfield
    def hierarchy(self):
        """
        Hierarchy of brain regions.
        """
        return self.base_atlas.load_hierarchy()

    @lazyfield
    def region_map(self):
        """
        Region map associated with the atlas.
        """
        return self.base_atlas.load_region_map()

    dataset_brain_regions = Field(
        """
        Dataset that provides brain regions in `self.base_atlas`.
        """,
        __default_value__="brain_regions")

    @lazyfield
    def brain_regions(self):
        """
        Volumetric data that provides brain regions in the atlas.
        """
        return self.base_atlas.load_data(self.dataset_brain_regions).raw

    @lazyfield
    def voxel_data(self):
        """
        A representative `VoxelData` object associated with `self.atlas`.
        """
        return self.base_atlas.load_data(self.dataset_brain_regions)

    @lazyfield
    def volume_voxel(self):
        """
        Volume of a single voxel, in um^3.
        """
        return self.voxel_data.voxel_volume

    layers = Field(
        """
        Values of the layers in the brain region represented by the atlas. We
        assume that this atlas is for the brain region, and so provide a
        mapping for each laminar region to the values of the layers used in
        this atlas. Default value are provided for cortical circuits that use
        an atlas specific to the cortex, or a region in the cortex such as the
        Somatosensory cortex (SSCx).
        """,
        __default_value__=("L1", "L2", "L3", "L4", "L5", "L6"))

    @lazyfield
    def region_layer(self):
        """
        An object that expresses how region and layer are combined in the
        atlas, how their acronyms are represented in the hierarchy.
        """
        return RegionLayer(atlas=self.base_atlas)

    def _label_layer(self, layer):
        """..."""
        if isinstance(layer, int):
            return "L{}".format(layer)
        return layer

    @lazyfield
    def principal_axis(self):
        """
        An object to handle queries concerning the voxel principal axis.
        """
        return PrincipalAxis(atlas=self.base_atlas)

    def get_mask(self,
            region=None,
            layer=None,
            depth=None,
            height=None):
        """
        Mask for combinations of given parameters.
        """
        region_layer_mask =\
            self.region_layer.get_mask(
                region=region,
                layer=layer)

        if depth is None and height is None:
            return region_layer_mask

        if depth is not None and height is not None:
            raise TypeError(
                "Cannot define a mask for both depth and height.")

        principal_axis_mask =\
            self.principal_axis.get_mask(
                depth=depth,
                height=height)

        return numpy\
            .logical_and(
                region_layer_mask,
                principal_axis_mask)

    def get_voxel_count(self,
            region=None,
            layer=None,
            depth=None,
            height=None):
        """..."""
        return\
            numpy.sum(
                self.get_mask(
                    region=region,
                    layer=layer,
                    depth=depth,
                    height=height))

    def indices_to_positions(self, voxel_ids):
        """..."""
        return self.voxel_data.indices_to_positions(voxel_ids)

    def positions_to_indices(self, positions):
        """..."""
        return self.voxel_data.positions_to_indices(positions)

    def get_bin_counts(self,
            positions):
        """
        Get the number of positions that fall in each voxcell

        Arguments
        ---------------
        positions : Either a numpy.ndarray of dimension (N, 3),
        ~           or a pandas.DataFrame containing columns <x, y, z>
        """
        if not isinstance(positions, numpy.ndarray):
            positions = positions[[X, Y, Z]].values

        voxel_counts =\
            pandas.DataFrame(
                self.voxel_data.positions_to_indices(positions),
                columns=[X, Y, Z]
            ).apply(
                lambda row: (row[X], row[Y], row[Z]),
                axis=1
            ).value_counts(
            ).reset_index(
            ).rename(
                columns={
                    "index": "voxel_index",
                    0: "number"
                }
            )
        voxel_count_array =\
            numpy.zeros(shape=self.voxel_data.shape)
        indices_count_array =\
            tuple(
                numpy.array(
                    list(voxel_counts.voxel_index.values)
                ).transpose()
            )
        voxel_count_array[indices_count_array] = voxel_counts.number.values
        return voxel_count_array

    def random_positions(self,
            **spatial_parameters):
        """
        Generate random positions (np.array([x,y,z])) in a region
        defined by the spatial parameters passed as arguments.
        """
        mask = self.get_mask(**spatial_parameters)
        if numpy.nansum(mask) == 0:
            raise RuntimeError(
                """
                No valid voxels that satisfy spatial parameters: {}
                """.format(
                    '\n'.join(
                        "{}: {}".format(parameter, value)
                        for parameter, value in spatial_parameters.items())))
        voxel_indices = list(zip(*numpy.where(mask)))
        while True:
            yield self.voxel_data.indices_to_positions(
                voxel_indices[numpy.random.randint(len(voxel_indices))])

    def layer_thicknesses(self, voxel_indices):
        """..."""

        if isinstance(voxel_indices, pandas.DataFrame):
            voxel_indices =(
                voxel_indices.x.to_numpy(numpy.int32),
                voxel_indices.y.to_numpy(numpy.int32),
                voxel_indices.z.to_numpy(numpy.int32))

        assert isinstance(voxel_indices, (tuple, numpy.ndarray))

        if isinstance(voxel_indices, numpy.ndarray):
            assert voxel_indices.ndim == 2 and voxel_indices.shape[1] == 3
            voxel_indices =\
                (voxel_indices[:, 0], voxel_indices[:, 1], voxel_indices[:, 2])

        def _get(thickness):
            try:
                return thickness[voxel_indices]
            except IndexError as error_i:
                try:
                    return thickness[list(zip(*voxel_indices))]
                except Exception as error_e:
                    raise ValueError(
                        """
                        Argument voxel_indices may not be of good shape to extract
                        thicknesses. Tried both input, and its transform:
                        \t {}
                        \t {}
                        """.format(error_i, error_e))

        return\
            OrderedDict(
                (self._label_layer(layer), _get(thickness))
                for layer, thickness in self.principal_axis.thickness.items())
