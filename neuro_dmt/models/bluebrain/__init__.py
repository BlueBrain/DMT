"""Brain models developed at the Blue Brain Project, EPFL."""

from abc import ABC, abstractmethod
from bluepy.v2.circuit import Circuit
import geometry

class BlueBrainModel(Circuit):
    """Brain circuit models developed at the Blue Brain Project (BBP) can be 
    studied with the bluepy API, also developed at the BBP. This class extends
    'bluepy.v2.circuit.Circuit'."""

    def __init__(self, *args, **kwargs):
        """initialize common stuff"""
        super(BlueBrainModel, self).__init__(*args, **kwargs)

    def geometric_bounds(self, cell_query, target=None):
        "Geometric bounds of this circuit, determined by a bounding box around
        the queried cells contained in this circuit within the specified
        'target'."
        def with_target(cell_query):
            if isinstance(target, str):
                cell_query['$target'] = target
            elif isinstance(target, Cell.HYPERCOLUMN):
                cell_query[Cell.HYPERCOLUMN] = target
            else:
                raise TypeError("Unhandled target type: {}"\
                                .format(type(target)))
            return cell_query

        return geometry.bounds(
            self.cells.position() if target is None \
            else self.cells.get(with_target(cell_query))
        )

    def collect_sample(self, measurement,
                       sampled_bbox_shape=np.array([25.0, 25.0, 25.0]),
                       sample_size=100,
                       region_to_explore=None,
                       cell_query=None,
                       target=None):
        """Collect samples of a measurement.

        Parameters
        ------------------------------------------------------------------------
        measurement :: FunctionType
        sampled_bbox_shape :: numpy.ndarray [x, y, z] #to create ROIs around sampled locations
        sample_size :: int
        region_to_explore :: region in the circuit to explore random locations in
        cell_query :: dict
        """
        if region_to_explore is None:
            if cell_query is None:
                raise Exception(
                    "Neither a region to explore, nor a cell query provided."
                )
            region_to_explore = self.geometric_bounds(cell_query, target)

        points = (geometry.sample_location(region_to_explore)
                  for i in range(sample_size))

        def sampled_bbox(center):
            """..."""
            half_box = sampled_bbox_shape / 2.0
            return Cuboid(center - half_box, center + half_box)

        ms = (measurement(self, sampled_bbox(center)) for center in points)

        return (m for m in ms if m is not None)






