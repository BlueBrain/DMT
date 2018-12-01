"""O1 circuit build geometry"""
import numpy as np
from bluepy.v2.enums import Cell
from dmt.vtk.measurement.condition import Condition
from dmt.vtk.utils.collections import Record
from dmt.vtk.utils.descriptor import Field
from neuro_dmt.utils import brain_regions
from neuro_dmt.measurement.parameter\
    import BrainCircuitSpatialParameter
from neuro_dmt.measurement.parameter\
    import Column
from neuro_dmt.models.bluebrain.circuit.specialization\
    import CircuitSpecialization
from neuro_dmt.models.bluebrain.circuit.build\
    import CircuitGeometry
from neuro_dmt.models.bluebrain.circuit.geometry import \
    Cuboid,  random_location
from neuro_dmt.models.bluebrain.circuit.O1.parameters\
    import HyperColumn

XYZ = [Cell.X, Cell.Y, Cell.Z]

class O1LayeredCircuitSpecialization(
        CircuitSpecialization):
    """Mixin class that provides
    abstract and concrete methods that should be common to all O1.v6a circuits
    --- circuits that have a fake Atlas holding their O1 geometry."""

    central_meso_column\
        = Field(
            __name__="central_meso_column",
            __type__=str,
            __default__="mc2_Column",
            __doc__="""There are seven meso-columns. Column 2 ('mc2_Column') 
            is the central column, but in a particular hippocampus CA1 circuit
            it has been called 'mc2'...""")

    lattice_vector\
        = Field(
            __name__="lattice_vector",
            __type__=Record,
            __is_valid__=lambda instance, value: "a1" in value and "a2" in value)

    layer_thickness\
        = Field(
            __name__="layer_thickness",
            __type__=np.ndarray,
            __is_valid__=lambda instance, value: len(value.shape) == 1,
            __doc__="""Array of layer thicknesses.""")

    layer_bottom\
        = Field(
            __name__="layer_bottom",
            __type__=float,
            __doc__="""Min value of the circuit layers' y-axis. This should
            be where L1 starts.""")

    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            cell_group_params=(
                Cell.LAYER,
                Cell.REGION,
                "$target",
                Cell.SYNAPSE_CLASS,
                Cell.MORPH_CLASS,
                Cell.ETYPE,
                Cell.MTYPE,
                "meso_column",),
            *args, **kwargs)
        
    @property
    def layer_top(self):
        """..."""
        return self.layer_bottom  + np.sum(self.layer_thickness)

    @property
    def target(self):
        """..."""
        return self.central_meso_column

   
class O1CircuitGeometry(
        CircuitGeometry):
    """Specializations of methods for the O1.v6a circuits."""

    label = "O1"

    def __init__(self,
            circuit,
            *args, **kwargs):
        self.__midplane = None
        super().__init__(
            circuit,
            *args, **kwargs)

    @property
    def thickness(self):
        """..."""
        return np.sum(
            self.circuit_specialization\
            .layer_thickness)

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
        cells = self.circuit.cells
        return np.array(
            cells.get(query, properties=XYZ).mean()
            if query else
            cells.get(properties=XYZ).mean())

    def midplane_projection(self, point):
        """Project the given point on to the circuit's mid plane."""
        return np.array([
            point[0],
            self.midplane.point[1],
            point[2]])

    def random_position(self,
            condition = Record(),
            offset = 50. * np.ones(3),
            *args, **kwargs):
        """...
        Handle empty ("Record()") condition by returning
        a point at the center of the columns"""
        target\
            = kwargs.get(
                "target",
                self.circuit_specialization.target)

        query\
            = self.circuit_specialization.cell_query(
                condition,
                *args, **kwargs)
        self.logger.debug(
            self.logger.get_source_info(),
            "query: {}".format(query),
            "condition: {}".format(condition.value))
        bounds\
            = self.helper\
                  .geometric_bounds(
                      query,
                      target=target)
        if bounds is None:
            return None
        box\
            = Cuboid(
                bounds.bbox[0] + offset,
                bounds.bbox[1] - offset)
        return random_location(box)

    def random_crossectional_point(self,
            meso_column=None):
        """Get a random point orthogonal to the layer axis"""
        if not meso_column:
            meso_column\
                = self.circuit_specialization\
                      .central_meso_column
        cells\
            = self.circuit.cells.get(
                {"$target": meso_column},
                properties=XYZ)
        random_pos\
            = np.array(
                cells.iloc[
                    np.random.randint(
                        cells.shape[0])])
        random_pos[1] = 0.0
        return random_pos

    @property
    def meso_column_bottom(self):
        """..."""
        return self.circuit_specialization.layer_bottom

    def __random_column(self,
            meso_column=None,
            crossection=50.):
        """Get a random column, spanning all the layers."""
        random_pos\
            = self.random_crossectional_point(
                meso_column)
        square\
            = (crossection *
               np.array([
                   1.0, 0.0, 1.0 ]))
        bottom\
            = np.array([
                0.0,
                self.meso_column_bottom,
                0.0 ])
        top\
            = np.array([
                0.0,
                self.meso_column_bottom + self.thickness,
                0.0])
        return Cuboid(
            random_pos - square + bottom,
            random_pos + square + top)

    def random_spanning_column(self,
            condition=Condition([]),
            crossection=50.):
        """..."""
        return\
            self.__random_column(
                meso_column=condition.get_value(
                    self.spanning_column_parameter().label),
                crossection=crossection)

    def spanning_column_parameter(self,
            meso_columns=[2]):
        """Spatial parameter representing a column that spans all the layers
        (or another sub-region) of a brain region. Unlike sub-region (layer),
        this spatial parameter Column depends on the (geometric) build of the
        circuit."""
        return self.circuit_specialization\
                   .get_spanning_column_parameter(
                       column_values=meso_columns)

