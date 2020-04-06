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
Region of Interest
"""

import math
import numpy as np
from dmt.tk.field import Field, LambdaField, lazyfield, WithFields


class Cuboid(WithFields):
    """
    A region.
    """
    position_corner_0 = Field(
        """
        A corner of this cuboid.
        """)
    position_corner_1 = Field(
        """
        Another corner of this cuboid, diagonally opposite to the other.
        """)
    closed = Field(
        """
        Is the geometry closed?
        """,
        __default_value__=True)

    def __init__(self,
            positions_corner_0,
            positions_corner_1,
            closed=False,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args,
            position_corner_0=positions_corner_0,
            position_corner_1=positions_corner_1,
            closed=closed,
            **kwargs)


    @property
    def volume(self):
        """
        Volume of this cuboid.
        """
        return np.abs(np.prod(self.position_corner_0, self.position_corner_1))

    @property
    def bbox(self):
        """
        A box that bounds this cuboid.
        """
        return (self.position_corner_0, self.position_corner_1)

    def contains(self, position):
        """???"""
        check = np.less_equal if self.closed else np.less
        return np.all(
            np.logical_and(
                check(self.position_corner_0, position),
                check(self.position_corner_1, position)),
        axis=1)
    
   
class Cube(Cuboid):
    def __init__(self, position_center, length_side, closed=True):
        super().__init__(
            position_corner_0=position_center - length_side / 2.,
            position_corner_1=position_center + length_side / 2.,
            closed=closed)


class Sphere(WithFields):
    """
    Region in 3D
    """
    position_center = Field(
        """
        Three dimensional array providing position of the cube's center.
        """)
    radius = Field(
        """
        Radius of the sphere
        """)
    closed = Field(
        """
        Is the sphere closed?
        """,
        __default_value__=True)

    @property
    def volume(self):
        return (4. / 3.) * math.pi * math.pow(self.radius, 3)

    @property
    def bbox(self):
        return (self.center - self.radius, self.center + self.radius)

    def contains(self, position):
        check = np.less_equal if self.closed else np.less
        return check(
            np.linalg.norm(position - self.center, axis=0),
            self.radius)


