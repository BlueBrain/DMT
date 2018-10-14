"""O1 circuit build"""
import numpy as np
from bluepy.v2.enums import Cell
from dmt.vtk.utils.collections import Record
from dmt.vtk.utils.descriptor import Field
from neuro_dmt.utils import brain_regions
from neuro_dmt.models.bluebrain.circuit.brain_regions import BrainRegionSpecific
from neuro_dmt.models.bluebrain.circuit.build import CircuitBuild
from neuro_dmt.models.bluebrain.circuit.geometry import \
    Cuboid,  random_location
from neuro_dmt.models.bluebrain.circuit.O1.parameters import HyperColumn

XYZ = [Cell.X, Cell.Y, Cell.Z]

class Cortical(
        BrainRegionSpecific):
    """..."""
    brain_region = brain_regions.cortex

    def __init__(self,
            by=tuple(),
            target="mc2_Column",
            *args, **kwargs):
        """..."""
        cell_group_params\
            = by if by else ("layer",
                             "$target",
                             Cell.SYNAPSE_CLASS,
                             Cell.MORPH_CLASS)
        super().__init__(
            cell_group_params,
            target=target,
            *args, **kwargs)

    def cell_query(self,
            condition,
            *args, **kwargs):
        """A dict that can be passed to circuit.cells.get(...).
        Concrete implementation may override """
        param_values = {
            param: condition.get_value(param)
            for param in self.cell_group_params}
        return {
            param: value
            for param, value in param_values.items()
            if value}
            

class Hippocampal(
        BrainRegionSpecific):
    """..."""
    brain_region = brain_regions.hippocampus

    def __init__(self,
            by=None,
            *args, **kwargs):
        """..."""
        cell_group_params\
            = by if by else ("layer",)
        super().__init__(
            cell_group_params,
            *args, **kwargs)

    def cell_query(self,
            condition,
            *args, **kwargs):
        """A dict that can be passed to circuit.cells.get(...).
        Concrete implementation may override """
        return {
            p: condition.get_value(p)
            for p in self.cell_group_params}


class O1Circuit(
        CircuitBuild):
    """Specializations of methods for the O1.v6a circuits."""

    specializations = {
        brain_regions.cortex: Cortical(),
        brain_regions.hippocampus: Hippocampal() }

    geometry = Field(
        __name__="geometry",
        __type__=Record,
        __doc__="Contains information about O1 geometry")

    def __init__(self, *args, **kwargs):
        self.label = "O1"
        self.geometry\
            = kwargs.get(
                "geometry",
                Record(
                    layer_thickness=np.array(
                        [164.94915873,
                         148.87602025,
                         352.92508322,
                         189.57183895,
                         525.05585701,
                         700.37845971]),
                    lattice_vector=Record(
                        a1=np.array([0.0, 0.0, 230.92]),
                        a2=np.array([199.98, 0.0, -115.46])),
                    min_cortical_depth=10))
        self.__midplane = None
        super().__init__(
            *args, **kwargs)

    @property
    def thickness(self):
        """..."""
        return np.sum(self.geometry.layer_thicknesss)

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
        return np.array(
            point[0],
            self.midplane.point[1],
            point[2])

    def random_position(self,
            brain_region,
            condition = Record(),
            offset = 50. * np.ones(3),
            *args, **kwargs):
        """...
        Handle the an empty ("Record()") condition by returning
        a point at the center of the columns"""
        self.logger.debug(
            self.logger.get_source_info(),
            "find random position with condition {}".format(condition.value))
        try:
            brain_region_spec\
                = self.specializations[
                    brain_region]
        except KeyError as e:
            raise NotImplementedError(
                "Brain region specialization for {}"\
                .format(brain_region))
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
        """...Current implementation does not use a brain_region."""
        mean_position\
            = self._center(
                {"$target": "mc{}_Column".format(column_index)})\
                  .mean()
        square\
            = crossection * np.array([1., 0., 1.])
        point_0\
            = np.array(mean_position - square)
        point_0[1]\
            = self.geometry.min_cortical_depth

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
        return self.geometry.min_cortical_depth

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
