# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Circle shapes.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PatchPolygon
from matplotlib.collections import PatchCollection
from dmt.tk.field import Field, lazyfield
from .import Curve


class Circle(Curve):
    """
    Circular shapes.
    """
    center = Field(
        """
        Center of the circle.
        """,
        __default_value__=np.zeros(2))
    radius = Field(
        """
        Radius of the circles.
        """,
        __default_value__=1.)
    rotation = Field(
        """
        Circle's base angle to +X-axis.
        """,
        __default_value__=0.)


    def point_at(self, position):
        """

        Arguments
        --------------
        position :: either an angular position or a PolarPoint.
        """
        try:
            return self.center + np.array([
                position.radial * np.sin(position.angular + self.rotation),
                position.radial * np.cos(position.angular + self.rotation)])
        except AttributeError:
            return self.center + np.array([
                self.radius * np.sin(position + self.rotation),
                self.radius * np.cos(position + self.rotation)])
        
    def segment_points(self,
            angle_begin=0.,
            angle_end=2.*np.pi,
            number=100):
        """
        Segment points from starting angle to ending angle,
        along the circle's periphery.
        """
        return np.array([
            self.point_at(angle)
            for angle in np.linspace(angle_begin, angle_end, number)])

    def arc(self,
            angle_begin,
            angle_end,
            label="",
            radius=None):
        """..."""
        if radius is None:
            radius = self.radius
        if not label:
            label="arc_{}_{}".format(angle_begin, angle_end)
        return Arc(
            label=label,
            center=self.center,
            radius=radius,
            rotation=self.rotation,
            angle_begin=angle_begin,
            angle_end=angle_end)

    def points(self, number=100):
        """..."""
        return self.segment_points(number=number)


class Arc(Circle):
    """
    Part of a circle.
    """
    angle_begin = Field(
        """
        Angle at which the arc starts.
        """)
    angle_end = Field(
        """
        Angle at which the arc stops.
        """)
    def points(self, number=100):
        """..."""
        return self.segment_points(
            angle_begin=self.angle_begin,
            angle_end=self.angle_end,
            number=number)
