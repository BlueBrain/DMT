"""
Shapes made with matplotlib.
"""
from abc import ABC, abstractmethod
from collections import namedtuple
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PatchPolygon
from matplotlib.collections import PatchCollection
from dmt.tk.field import Field, LambdaField, lazyfield, WithFields


PolarPoint = namedtuple("PolarPoint", ["radial", "angular"])

class Geometry(ABC, WithFields):
    """
    Base class for Geometries.
    """
    label = Field(
        """
        A label to be displayed.
        """)
    children = Field(
        """
        `Geometry`s spawned from this `Geometry`.
        """,
        __default_value__=[])
    
    @lazyfield
    def identifier(self):
        """
        Identifier can be used as a key in a mapping providing
        features for this `Geometry`.
        Override the return to specialize...
        """
        return self.label

    def spawn(self,
            type_geometry,
            *args, **kwargs):
        """
        Create a new geometry.
        """
        self.children.append(type_geometry(*args, **kwargs))
        return self.children

    @abstractmethod
    def points(self, number):
        """
        Points on this `Geometry`'s boundary.
        """
        raise NotImplementedError

    @abstractmethod
    def _draw_this(self,
            *args, **kwargs):
        """
        Draw only this geometry.
        """
        raise NotImplementedError
        
    def draw(self,
            *args, **kwargs):
        """
        Draw this geometry, and all the geometries it has spawned.
        """
        for child in self.children:
            child.draw(*args, **kwargs)
        self._draw_this(*args, **kwargs)


class Curve(Geometry):
    """
    A curve on a plane, like a circle, or an arc.
    """

    def _draw_this(self,
            number_points=100,
            *args, **kwargs):
        points =\
            self.points(
                number=number_points)
        return\
            plt.plot(
                points[:, 0],
                points[:, 1],
                *args, **kwargs)


class Path(Curve):
    """
    A curve with points on the curve provided explicitly.
    """,
    vertices = Field(
        """
        A sequence of 2D vertices that define this `Path`.
        """)

    def points(self, number=100):
        """
        Convert vertices to the number of points demanded.
        """
        if number > len(self.vertices):
            return self.vertices
        return np.random.choice(
            self.vertices, number, replace=False)


class Polygon(Geometry):
    """
    Polygon is a sequences of vertices.
    """
    sides = Field(
        """
        Sequence of `Paths`
        """)
    facecolor = Field(
        """
        Colors to use for this `Polygon`.
        """,
        __default_value__="red")

    def points(self, number=None):
        """
        Points of a given number does not make sense.
        """
        return [
            point for side in self.sides
            for point in side.vertices]

    def _draw_this(self,
            axes=None,
            *args, **kwargs):
        """
        Draw this polygon.
        """
        if axes is None:
            axes = plt.gca()

        patch_polygon =\
            PatchPolygon(
                np.vstack([
                    side.vertices
                    for side in self.sides]))
        axes.add_collection(
            PatchCollection(
                [patch_polygon],
                facecolors=(self.facecolor,),
                edgecolors=("grey",),
                linewidths=(1,),))
                
        return axes
        

from .circle import Circle, Arc
