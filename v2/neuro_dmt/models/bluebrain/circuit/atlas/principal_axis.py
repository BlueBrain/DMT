"""
In the atlas, a principal axis is defined for each voxel that a
cell placed in that voxel will orient itself towards.
Here we provide code that documents and provides tools to work
with the principal axis.
"""

import numpy as np
from voxcell.nexus.voxelbrain import Atlas
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
        layer_boundaries = (
            (layer, self.atlas.load_data("[PH]{}".format(layer)).raw)
            for layer in self.layers)
        return {
            layer: Interval(top=boundary[..., 1], bottom=boundary[..., 0])
            for layer, boundary in layer_boundaries}

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
        ...
        """
        return self.position - self.bottom

    @lazyfield
    def depth(self):
        """
        ...
        """
        return self.top - self.position

    def get_mask(self,
            depth=None,
            height=None):
        """
        Get a mask at given depth or height.

        Arguments
        depth / height: A single tuple of floats or a list of such tuples,
        with each tuple representing a bin.
        """
        def _get_list(item):
            """..."""
            if (
                    isinstance(item, tuple)
                    and len(item) > 0
                    and isinstance(item[0], (int, np.integer, float, np.float))
            ):
                return [item]
            return get_list(item)

        def _get_one(_bin):
            """
            Mask for one bin
            """
            values = self.depth if depth is not None else self.height
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
            return np.logical_and(begin <= values, values < end)

        if depth is not None:
            if height is not None:
                raise TypeError(
                    """
                    Cannot define a principal axis mask at given depth
                    as well as height.
                    """)
            return np.logical_and(
                self.valid_voxels,
                np.any([_get_one(_bin) for _bin in _get_list(depth)], axis=0))

        if height is None:
            raise TypeError(
                """
                Need at least a value for depth or height to define a
                principal axis mask.
                """)
        return np.logical_and(
            self.valid_voxels,
            np.any([_get_one(_bin) for _bin in _get_list(height)], axis=0))
                

