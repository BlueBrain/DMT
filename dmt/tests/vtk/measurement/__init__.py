"""Test develop Measurement."""

import numpy as np
from dmt.vtk import measurement
from dmt.vtk.phenomenon import Phenomenon
from dmt.vtk.utils.collections import Record

class CellDensity(measurement.Method):
    """test cell density measurement to test Measurement!"""

    def __init__(self, scale):
        """A scale for cell densities."""
        self.__scale = scale

    label = "cell_density"
    phenomenon = Phenomenon("cell_density", "mock cell density")

    def __call__(self, roi):
        """Random cell density"""
        return self.__scale * np.random.random()/roi.volume



roi_groups = Record(label = "layer",
                    values = [1,2,3,4,5,6])

def roi_sampler(layer):
    return (Record(volume = np.random.random()) for _ in range(10))

cd = CellDensity(10.)

cds = cd.sample(Record(group=roi_groups,
                       sample=roi_sampler))
