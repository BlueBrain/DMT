"""
In the atlas, a principal axis is defined for each voxel that a
cell placed in that voxel will orient itself towards.
Here we provide code that documents and provides tools to work
with the principal axis.
"""

from voxcell.nexus.voxelbrain import Atlas
from dmt.tk.field import WithFields, Field, lazyfield
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
            for layer, boundary  layer_boundaries}

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
    def depth(self):
        """
        ...
        """
        return self.position - self.bottom

    @lazyfield
    def height(self):
        """
        ...
        """
        return self.top - self.position

