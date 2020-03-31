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
In the atlas, a principal axis is defined for each voxel that a
cell placed in that voxel will orient itself towards.
Here we provide code that documents and provides tools to work
with the principal axis.
"""

from collections import OrderedDict
from tqdm import tqdm
import numpy as np
from voxcell.nexus.voxelbrain import Atlas
from collections.abc import Mapping
from dmt.tk.field import WithFields, Field, lazyfield
from dmt.tk.collections import get_list
from neuro_dmt.utils.geometry import Interval


class PrincipalAxis(WithFields):
    """
    A class to document and help work with the voxel principal axis.
    """
    atlas = Field(
        """
        The `Atlas` instance for which this `PrincipalAxis` instance is defined.
        """)
    layers = Field(
        """
        Layer values from bottom to top. The default value below assumes a
        cortical circuit atlas.
        """,
        __default_value__=[6, 5, 4, 3, 2, 1])

    @lazyfield
    def valid_voxels(self):
        """
        Not all voxels in the volumetric datasets are valid.
        """
        return self.atlas.load_data("brain_regions").raw != 0

    @lazyfield
    def intersection(self):
        """
        Volumetric datasets corresponding to intersection of the principal axis
        with the layer boundaries.
        """
        return OrderedDict(
            (layer, Interval(top=boundary[..., 1], bottom=boundary[..., 0]))
             for layer, boundary in (
                     (layer, self.atlas.load_data("[PH]{}".format(layer)).raw)
                     for layer in tqdm(self.layers)))

    @lazyfield
    def thickness(self):
        """
        Thickness of layers as seen by each voxel.
        """
        return OrderedDict((
            (layer, intersection.top - intersection.bottom)
            for (layer, intersection) in (
                    (layer, self.intersection[layer])
                    for layer in self.layers)))

    @lazyfield
    def position(self):
        """
        Volumentric dataset providing the position of each voxel along it's
        principal axis.
        """
        return self.atlas.load_data("[PH]y").raw

    @lazyfield
    def top(self):
        """
        Top of everything, according to each voxel.
        Assume that the last element in self.layers is the topmost layer.
        """
        return self.intersection[self.layers[-1]].top

    @lazyfield
    def bottom(self):
        """
        Bottom of everything, according to each voxel.
        Assume that the first element in self.layers is the bottomoest layer.
        """
        return self.intersection[self.layers[0]].bottom

    @lazyfield
    def height(self):
        """
        Distance from the bottom, according to each voxcell.
        """
        return self.position - self.bottom

    @lazyfield
    def depth(self):
        """
        Distance from the top, according to each voxcell.
        """
        return self.top - self.position

    @lazyfield
    def cortical_chickness(self):
        """
        Total (cortical)-thickness, according to each voxcell.
        """
        return self.top - self.bottom

    @lazyfield
    def relative_height(self):
        """
        Fraction of cortical thickness, according to each voxcell.
        """
        return self.height / self.thickness

    @lazyfield
    def relative_depth(self):
        """
        Fraction of cortical thickness, according to each voxcell.
        """
        return self.depth / self.thickness

    def get_mask(self,
            depth=None,
            height=None,
            as_fraction=True):
        """
        Get a mask at given depth or height.

        Arguments
        depth / height: A single two-tuple of floats or a list of such tuples,
        ~               with each tuple representing a bin.
        as_fraction:  Boolean indicating if the depth / height is
        ~              fraction of total (local) thickness per voxcell.
        """
        if (depth is not None) and (height is not None):
            raise TypeError(
                """
                Cannot define a principal axis mask at given depth
                as well as height.
                """)
        if (depth is None) and (height is None):
            raise TypeError(
                """
                Need at least a value for depth or height to define a
                principal axis mask.
                """)

        values =\
            (self.depth if depth is not None else self.height)\
            if not as_fraction else\
               (self.relative_depth if depth is not None else self.relative_height)

        def _get_list(item):
            """..."""
            if (
                    isinstance(item, tuple)
                    and len(item) == 2
                    and isinstance(item[0], (int, np.integer, float, np.float))
            ):
                return [item]
            if (
                    isinstance(item, Mapping)
                    and len(item) == 2
                    and "begin" in item and "end" in item
            ):
                return [item]
            return get_list(item)

        def _check_arguments(begin, end):
            """..."""
            if as_fraction:
                if (begin < 0. or begin > 1.) or (end < 0. or end > 1.):
                    raise ValueError(
                        """
                        Invalid bin begin or end for relative values:
                        \t depth : {}, height : {}, as_fraction : {}
                        """.format(depth, height, as_fraction))

        def _get_one(_bin):
            """
            Mask for one bin
            """
            try:
                begin = _bin[0]
                end   = _bin[1]
            except KeyError as key_error_0_1:
                try:
                    begin = _bin["begin"]
                    end   = _bin["end"]
                except KeyError as key_error_begin_end:
                    raise ValueError(
                        """
                        {} values of type {} are not a tuple
                        or a mapping<begin -> depth_begin, end -> depth_end>.
                        KeyErrors raised:
                        {}
                        {}
                        """.format(
                            "Depth" if depth is not None else "Height",
                            type(values),
                            key_error_0_1,
                            key_error_begin_end)
                    )
            #_check_arguments(begin, end)
            return np.logical_and(begin <= values, values < end)

        if depth is not None:
            return np.logical_and(
                self.valid_voxels,
                np.any([_get_one(_bin) for _bin in _get_list(depth)], axis=0))

        return np.logical_and(
            self.valid_voxels,
            np.any([_get_one(_bin) for _bin in _get_list(height)], axis=0))


