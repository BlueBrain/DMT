"""O1 circuit build geometry"""
import numpy as np
from bluepy.v2.enums import Cell
from dmt.vtk.utils.collections import Record
from dmt.vtk.utils.descriptor import Field
from neuro_dmt.utils import brain_regions
from neuro_dmt.models.bluebrain.circuit.brain_regions\
    import BrainRegionSpecific
from neuro_dmt.models.bluebrain.circuit.build import CircuitGeometry
from neuro_dmt.models.bluebrain.circuit.geometry import \
    Cuboid,  random_location
from neuro_dmt.models.bluebrain.circuit.O1.parameters import HyperColumn

XYZ = [Cell.X, Cell.Y, Cell.Z]

class Cortical(
        BrainRegionSpecific):
    """..."""

    def __init__(self,
            target="mc2_Column",
            *args, **kwargs):
        """..."""
        super().__init__(
            brain_region=brain_regions.cortex,
            target=target,
            *args, **kwargs)


class Hippocampal(
        BrainRegionSpecific):
    """..."""

    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            brain_region=brain_regions.hippocampus,
            *args, **kwargs)


class O1CircuitGeometry(
        CircuitGeometry):
    """Specializations of methods for the O1.v6a circuits."""

    specializations = {
        brain_regions.cortex: Cortical(),
        brain_regions.hippocampus: Hippocampal() }

    def __init__(self,
            circuit,
            *args, **kwargs):
        self.label = "O1"
        self.layer_thickness\
            = kwargs.get(
                "layer_thickness",
                np.array([
                    164.94915873,
                    148.87602025,
                    352.92508322,
                    189.57183895,
                    525.05585701,
                    700.37845971]))
        self.lattice_vector\
            = kwargs.get(
                "lattice_vector",
                Record(a1=np.array([0.0, 0.0, 230.92]),
                       a2=np.array([199.98, 0.0, -115.46])))
        self.layer_start\
            = kwargs.get(
                "layer_start",
                10.)
        self.__midplane = None
        super().__init__(
            circuit,
            *args, **kwargs)

    @property
    def thickness(self):
        """..."""
        return np.sum(self.layer_thickness)

    @property
    def midplane(self):
        """..."""
        if not self.__midplane:
            self.__midplane\
                = Record(
                    point=self.__center(),
                    orthogonal=np.array([0., 1., 0.]))
        return self.__midplane

    def __center(self, query={}):
        """Center of the circuit.
        This could be computed from the geometry,
        if only we new the position of the central column."""
        cells = self._circuit.cells
        return np.array(
            cells.get(query, properties=XYZ).mean()
            if query else
            cells.get(properties=XYZ).mean())

    def midplane_projection(self, point):
        """Project the given point on to the circuit's mid plane."""
        point[1] = self.midplane.point[1]
        return np.array([
            point[0],
            self.midplane.point[1],
            point[2]])

    def random_position(self,
            brain_region,
            condition = Record(),
            offset = 50. * np.ones(3),
            *args, **kwargs):
        """...
        Handle empty ("Record()") condition by returning
        a point at the center of the columns"""
        self.logger.debug(
            self.logger.get_source_info(),
            "find random position with condition {}"\
            .format(condition.value),
            "for brain region {}".format(brain_region.label))
        brain_region_spec\
            = self.get_brain_region_spec(
                brain_region)
        target\
            = kwargs.get(
                "target",
                brain_region_spec.target)
        self.logger.debug(
            self.logger.get_source_info(),
            "with target {}".format(target))
        self.logger.debug(
            self.logger.get_source_info(),
            """brain region specific cell group params {}"""\
            .format(brain_region_spec.cell_group_params))
        query\
            = brain_region_spec.cell_query(
                condition,
                *args, **kwargs)
        self.logger.debug(
            self.logger.get_source_info(),
            "with query {}".format(query))
        bounds\
            = self._helper\
                  .geometric_bounds(
                      query,
                      target=target)
        self.logger.debug(
            self.logger.get_source_info(),
            "with bounds {}".format(bounds.bbox))
        if bounds is None:
            return None
        box\
            = Cuboid(
                bounds.bbox[0] + offset,
                bounds.bbox[1] - offset)
        return random_location(box)

    def central_column(self,
            column_index = 2,
            crossection=50.):
        """..."""
        mean_position\
            = self._center(
                {"$target": "mc{}_Column".format(column_index)})\
                  .mean()
        square\
            = crossection * np.array([1., 0., 1.])
        point_0\
            = np.array(mean_position - square)
        point_0[1]\
            = self.layer_start

        point_1\
            = np.array(mean_position + square)
        point_1[1]\
            = self.thickness
        return Cuboid(point_0, point_1)

    def random_crossectional_point(self):
        """Get a random point orthogonal to the layer axis"""
        cells\
            = self._circuit.cells.get(
                {"$target": "mc2_Column"},
                properties=XYZ)
        random_pos\
            = np.array(
                cells.iloc[
                    np.random.randint(
                        cells.shape[0])])
        random_pos[1] = 0.0
        return random_pos

    @property
    def column_start(self):
        """..."""
        return self.layer_start

    def random_column(self,
            crossection=50.):
        """Get a random column, spanning all the layers."""
        random_pos = self.random_crossectional_point()
        square\
            = (crossection *
               np.array([
                   1.0, 0.0, 1.0 ]))
        bottom\
            = np.array([
                0.0,
                self.column_start,
                0.0 ])
        top\
            = np.array([
                0.0,
                self.column_start + self.thickness,
                0.0])
        return Cuboid(
            random_pos - square + bottom,
            random_pos + square + top)

    @classmethod
    def column_parameter(cls,
            values=[2],
            *args, **kwargs):
        """Spatial parameter representing a column that spans all the layers
        (or another sub-region) of a brain region. Unlike sub-region (layer),
        this spatial parameter Column depends on the (geometric) build of the
        circuit."""
        return HyperColumn(
            values=values,
            *args, **kwargs)
