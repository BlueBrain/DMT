"""
Code for manipulating geometric features of Blue Brain Project circuits.
"""
import numpy as np
from bluepy.geometry.roi import ROI
from bluepy.v2.enums import Cell

class Cuboid(ROI):
    """
    A box with different side lengths as a region of interest.
    """
    def __init__(self,
            p0, #point_left_bottom_away,
            p1, #point_right_top_towards,
            closed=True):
        """
        A cuboid can be specified by two points, which relative to the center of
        the cuboid are at the negative most axis values and positive most axis
        values. So if the sides of the cuboid are u, v, and w, the points are
        1. np.array((-u/2, -v/2, -w/2))
        2. np.array((u/2, v/2, w/2))
        """
        self.p0 = p0
        self.p1 = p1
        self.center = (p0 + p1) / 2.
        self.closed = closed

    @property
    def volume(self):
        """
        Volumne of this cuboid
        """
        return np.abs(np.product(self.p1 - self.p0))

    @property
    def bbox(self):
        """
        Bounding box.
        """
        return (self.p0, self.p1)

    def contains(self, point):
        """
        Does this Cuboid contain 'point'?
        """
        check = np.less_equal if self.closed else np.less
        return np.all(
            np.logical_and(
                check(self.p0, point),
                check(self.p1, point)))

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
            center[Cell.X], center[Cell.Y], center[Cell.Z]])
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
    box :: bluepy.geometry.ROI / 2-tuple[3D-vector]
    n :: int #number of samples to collect

    Return
    ----------------------------------------------------------------------------
    A single vector (3D array) if n is None.
    A matrix with each row a vector if n is an integer.
    """

    r = np.random.random(dim if n is None else [n, dim])
    p0, p1 = box.bbox if isinstance(box, ROI) else box
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
