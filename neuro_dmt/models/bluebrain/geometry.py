"""Extension to geometry utils provided by bluepy.geometry."""
import numpy as np

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


def sample_location(box, n=1):
    """Sample a random location in the confines of a bounding box.

    Parameters
    ----------------------------------------------------------------------------
    box :: bluepy.geometry.ROI / 2-tuple[3D-vector]
    n :: int #number of samples to collect
    """
    def sample_from_interval(interval):
        """..."""
        return interval[0] + (interval[1] - interval[0]) * np.random.random()

    if n == 1:
        p0, p1 = box.bbox if isinstance(box, bluepy.geometry.ROI) else box
        return np.array([sample_from_interval((p0[0], p1[0])),
                         sample_from_interval((p0[1], p1[1])),
                         sample_from_interval((p0[2], p1[2]))])

    return (sample_location(box, 1) for i in range(n))
