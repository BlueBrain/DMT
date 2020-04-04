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
Code for manipulating geometric features of Blue Brain Project circuits.
"""
import numpy as np
from dmt.tk.field import Field, lazyproperty, WithFields
from neuro_dmt import terminology
from neuro_dmt.utils.geometry.roi import Cuboid

class Position(WithFields):
    """
    A three dimensional position.
    """
    X = Field(
        """
        X dimension of position.
        """)
    Y = Field(
        """
        Y dimension of position.
        """)
    Z = Field(
        """
        Z dimension of position.
        """)
    value_type = Field(
        """
        The type used to represent a position.
        For example it can simple be a 3-tuple, or np.array.
        """,
        __default_value__=np.array)

    @property
    def value(self):
        """
        Value of this Position cast to its value_type
        """
        return self.value_type(
            (self.X, self.Y, self.Z))

    @classmethod
    def sample(cls,
            box,
            n=None):#A rectangular bounding box in which points will be sampled
        """
        Sample 'n' random positions in a bounding box.
        """
        try:
            p0, p1 = box.bbox
        except AttributeError:
            #not a RegionOfInterest, assume it is a two tuple of positions
            p0, p1 = box
        random_in_unit_box =\
            np.random.random(
                3 if n is None else [n, 3])
        return p0 + random_in_unit_box * (p1 - p0)

    @classmethod
    def random(cls,
            Xrange,
            Yrange,
            Zrange):
        """
        A random value of Position, with coordinates chosen in the range given
        by Xrange, Yrange, and Zrange.
        """

        def __random_float(min_value, max_value):
            u = np.random.random_sample()
            return (1. - u) * min_value + u * max_value

        return Position(
            X=__random_float(*Xrange),
            Y=__random_float(*Yrange),
            Z=__random_float(*Zrange))

    @property
    def as_tuple(self):
        """
        As (X, Y, Z)
        """
        return (self.X, self.Y, self.Z)

    @property
    def as_array(self):
        """
        As numpy array
        """
        return np.array(self.as_tuple)



def rectangular_column(center, cross_section, height, axis=2):
    """
    A column along 'axis' with a rectangular base.

    Parameters
    ---------------
    center :: a list or dict representing geometric center of the column
    cross_section :: (side_0, side_1) of the column's rectangular base
    height :: Height of the column, along 'axis'
    """
    try:
        center = np.array([
            center[terminology.bluebrain.cell.X],
            center[terminology.bluebrain.cell.Y],
            center[terminology.bluebrain.cell.Z]])
    except TypeError:
        pass

    diagonal =\
        np.array([
            cross_section[0], height, cross_section[1]])
    return\
        Cuboid(
            center - diagonal / 2., center + diagonal / 2.)

def random_location(box, n=None, dim=3):
    """Sample random location in the confines of a bounding box.

    Parameters
    ----------------------------------------------------------------------------
    box :: RegionOfInterest or 2-tuple[3D-vector]
    n :: int #number of samples to collect

    Return
    ----------------------------------------------------------------------------
    A single vector (3D array) if n is None.
    A matrix with each row a vector if n is an integer.
    """

    r = np.random.random(dim if n is None else [n, dim])
    try:
        p0, p1 = box.bbox
    except AttributeError:
        p0, p1 = box
    return p0 + r * (p1 - p0) 

def collect_sample(measurement,
            region_to_explore,
            sampled_box_shape=np.array([25.0, 25.0, 25.0]),
            sample_size=100):
    """Collect a sample of a spatial measurement in a given region. A spatial
    measurement measures a spatial phenomenon for a given spatial region. To
    collect a sample for a measurement, start with a sample of spatial regions,
    and measure them!

    Parameters
    ----------------------------------------------------------------------------
    measurement :: Region -> Quantity
    region_to_explore :: Region #where measurements are to be made
    sampled_bbox_shape :: Box #dimensions of the region to be measured
    sampled_size :: Int #number of measurements to make.
    """
    assert(region_to_explore is not None)
    half_box = sampled_box_shape / 2.0
    ms = (measurement(Cuboid(center - half_box, center + half_box))
          for center in random_location(region_to_explore, n=sample_size))
    return (m for m in ms if m is not None)
