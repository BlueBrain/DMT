"""Extension to geometry utils provided by bluepy.geometry."""
import numpy as np
from bluepy.v2.enums import Cell
from bluepy.geometry.roi import ROI


class Cuboid(ROI):
    """A box with different side lengths as a region of interest."""
    def __init__(self, p0, p1, closed=True):
        self.p0 = p0
        self.p1 = p1
        self.center = (p0 + p1) / 2.
        self.closed = closed

    @property
    def volume(self):
        """Volume of a Cuboid"""
        return np.abs(np.product(self.p1 - self.p0))

    @property
    def bbox(self):
        """Bounding box of a Cuboid"""
        return (self.p0, self.p1)

    def contains(self, p):
        """Check if this Cuboid contains  point p."""
        pred = np.less_equal if self.closed else np.less
        return np.all(np.logical_and(pred(self.p0, p), pred(p, self.p1)), axis=-1)


def flat_bbox(center, cross_section, thickness):
    """A flat box that is not a uniform cube.

    Parameters
    ----------------------------------------------------------------------------
    center :: list or dict #geometric center of the box
    cross_section :: 2-tuple #largest cross-section as two [X, Z] lists
    thickness :: float #smallest of the three axis, assumed to be long the Y axis

    Notes
    ----------------------------------------------------------------------------
    Flat boxes are appropriate for cortical areas where depth is much smaller
    than the other two dimensions.
    """
    is_list_type = isinstance(center, list) or isinstance(center, np.ndarray)
    carray = center if is_list_type else \
             np.array([center[Cell.X], center[Cell.Y], center[Cell.X]])

    p0 = np.array([cross_section[0][0], -thickness / 2., cross_section[0][1]])
    p1 = np.array([cross_section[1][0], -thickness / 2., cross_section[1][1]])

    return Cuboid(carray + p0, carray - p1)

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
