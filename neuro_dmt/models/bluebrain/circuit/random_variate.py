"""BBP specific random variates, and related utilities."""
from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from bluepy.v2.enums\
    import Cell
from bluepy.geometry.roi\
    import ROI as RegionOfInterest
from dmt.vtk.utils.collections\
    import *
from dmt.vtk.measurement.condition\
    import Condition
from dmt.vtk.measurement.parameter\
    import Parameter
from dmt.vtk.measurement.parameter.finite\
    import FiniteValuedParameter
from dmt.vtk.measurement.parameter.random\
    import ConditionedRandomVariate
from dmt.vtk.utils.logging\
    import Logger, with_logging
from dmt.vtk.utils.descriptor\
    import Field, WithFCA
from neuro_dmt.models.bluebrain.circuit.circuit_model\
    import BlueBrainCircuitModel
from neuro_dmt.utils.brain_regions\
    import BrainRegion
from neuro_dmt.models.bluebrain.circuit.build\
    import CircuitGeometry
from neuro_dmt.models.bluebrain.circuit.geometry\
    import  Cuboid,  random_location


@with_logging(Logger.level.STUDY)
class CircuitPropertyRandomVariate(
        ConditionedRandomVariate):
    """A random variate that returns values for a circuit property,
    such as it's cell's gids, or positions in the circuit's physical space."""
    
    circuit_model=\
        Field(
            __name__="circuit_model",
            __type__=BlueBrainCircuitModel,
            __doc__="Blue brain circuit model to compute random variates for.")
    def __init__(self,
            circuit_model,
            *args, **kwargs):
        """...
        Parameters
        ------------------------------------------------------------------------
        circuit :: bluepy.v2.Circuit,
        """
        self.circuit_model\
            = circuit_model
        super().__init__(
            *args, **kwargs)

class RandomSpatialVariate(
        CircuitPropertyRandomVariate):
    """Generator of random values, for a (blue) brain circuit."""

    def __init__(self,
            circuit_model,
            *args, **kwargs):
        """Initialize Me
        Parameters
        ------------------------------------------------------------------------
        circuit :: bluepy.v2.Circuit,
        """
        super().__init__(
            circuit_model,
            reset_condition_type=True,
            *args, **kwargs)

    @property
    def circuit_geometry(self):
        """Provides circuit build geometry specific attribute
            specializations. Ideally we should be able to get this
            information from  'circuit'.
        """
        return self.circuit_model.geometry

class RandomPosition(
        RandomSpatialVariate):
    """Generate random positions in the circuit region."""
    label = "position"
    value_type = np.ndarray #dimension 3

    def __init__(self,
            circuit_model,
            offset=50.,
            *args, **kwargs):
        """...
        Parameters
        ------------------------------------------------------------------------
        circuit :: bluepy.v2.Circuit,
        circuit_geometry :: type #<: CircuitGeometry
        """
        self.offset = offset
        super().__init__(
            circuit_model,
            columns=pd.Index(
                ["X", "Y", "Z"],
                name="axis"),
            *args, **kwargs)

    def __call__(self,
            condition,
            *args, **kwargs):
        """..."""
        self.logger.ignore(
            self.logger.get_source_info(),
            """generate RandomPosition with condition {}"""\
            .format(condition.value))
        return\
            self.circuit_geometry\
                .random_position(
                    condition,
                    *args, **kwargs)


class RandomCrossectionalPoint(
        RandomPosition):
    """..."""
    def __init__(self,
            circuit_model,
            offset=50.,
            *args, **kwargs):
        """..."""
        super().__init__(
            circuit_model,
            offset=offset,
            *args, **kwargs)

    def __call__(self,
            condition,
            *args, **kwargs):
        """..."""
        return self.circuit_model\
                   .midplane_projection(
                       super().__call__(
                           condition,
                           *args, **kwargs) )


class RandomRegionOfInterest(
        RandomSpatialVariate):
    """Random regions of interest"""

    value_type = RegionOfInterest
    label = "region_of_interest"

    def __init__(self,
            circuit_model,
            sampled_box_shape=100.*np.ones(3),
            *args, **kwargs):
        """..."""
        self.sampled_box_shape = sampled_box_shape
        self.random_position\
            = RandomPosition(
                circuit_model,
                offset=sampled_box_shape/2.,
                *args, **kwargs)
        super().__init__(
            circuit_model,
            columns=[self.label],
            *args, **kwargs)

    def __call__(self,
            condition,
            sampled_box_shape=None,
            *args, **kwargs):
        """..."""
        half_box\
            = (sampled_box_shape if sampled_box_shape
               else self.sampled_box_shape / 2.)
        position\
            = self.random_position(
                condition,
                *args, **kwargs)
        if position is None:
            return None
        return Cuboid(
            position - half_box,
            position + half_box)
    

class RandomSpanningColumnOfInterest(
        RandomSpatialVariate):
    """A random column of interest is a random region of interest
    that spans the entire columnar dimension of the circuit.
    While well defined for O1 micro-circuits, we will have to be creative
    to define an equivalent definition for atlas based circuits."""

    value_type = RegionOfInterest
    label = "region_of_interest" 

    def __init__(self,
            circuit_model,
            crossection=50.,
            *args, **kwargs):
        """..."""
        self.__crossection\
            = crossection
        super().__init__(
            circuit_model,
            columns=[self.label],
            *args, **kwargs)

    def __call__(self,
            condition,
            *args, **kwargs):
        """Call Me"""
        return\
            self.circuit_model\
                .random_spanning_column(
                    condition,
                    crossection=self.__crossection)


class RandomBoxCorners(
        RandomSpatialVariate):
    """..."""
    value_type = tuple #length 2
    label = "box_corners"

    def __init__(self,
            circuit_model,
            sampled_box_shape=50.*np.ones(3),
            *args, **kwargs):
        """..."""
        self.random_region_of_interest\
            = RandomRegionOfInterest(
                circuit_model,
                sampled_box_shape=sampled_box_shape,
                *args, **kwargs)
        super().__init__(
            circuit_model,
            columns=pd.MultiIndex.from_tuples(
                [("lower_corner", "X"),
                 ("lower_corner", "Y"),
                 ("lower_corner", "Z"),
                 ("upper_corner", "X"),
                 ("upper_corner", "Y"),
                 ("upper_corner", "Z")],
                names=["box_corners", "axis"]),
            sampled_box_shape=sampled_box_shape,
            *args, **kwargs)

    def __call__(self,
            condition,
            *args, **kwargs):
        """"..."""
        region_of_interest=\
            self.random_region_of_interest(
                condition,
                *args, **kwargs)
        if region_of_interest is None:
            return None
        lower_corner, upper_corner=\
            region_of_interest.bbox
        return list(lower_corner) + list(upper_corner)


@with_logging(Logger.level.STUDY)
class RandomCellVariate(
        CircuitPropertyRandomVariate):
    """Generates random cell gids..."""
    value_type = int
    label = "gid"
    circuit_model=\
        Field(
            __name__="circuit_model",
            __type__=BlueBrainCircuitModel,
            __doc__="The circuit model in which to generate random cells.")

    def __init__(self,
            circuit_model,
            *args, **kwargs):
        """..."""

        self.__gid_cache__ = {}
        super().__init__(
            circuit_model=circuit_model,
            reset_condition_type=True,
            columns=["gid"],
            *args, **kwargs)

    def __call__(self,
            condition,
            *args, **kwargs):
        """...Call Me..."""
        if not condition.hash_id in self.__gid_cache__:
            self.__gid_cache__[condition.hash_id]=\
                self.circuit_model\
                    .get_cell_group(
                        condition.as_dict)
        if "size" in kwargs:
            return np.random.choice(
                self.__gid_cache__[condition.hash_id],
                kwargs["size"])
        return np.random.choice(
            self.__gid_cache__[condition.hash_id])


class RandomConnectionVariate(
        CircuitPropertyRandomVariate):
    """Generate random pair of cell gids..."""
    label = "connection"
    value_type = tuple

    def __init__(self,
            circuit_model,
            *args, **kwargs):
        """Initialize Me"""
        self.random_cell=\
            RandomCellVariate(
                circuit_model,
                *args, **kwargs)
        super().__init__(
            circuit_model,
            reset_condition_type=True,
            columns=["pre_gid", "post_gid"],
            *args, **kwargs)

    def __call__(self,
            condition,
            *args, **kwargs):
        """Call Me"""
        pre_mtype=\
            condition.get_value(
                "pre_mtype")
        post_mtype=\
            condition.get_value(
                "post_mtype")
        return (
            self.random_cell(
                Condition([
                    ("mtype", pre_mtype)])),
            self.random_cell(
                Condition([
                    ("mtype", post_mtype) ])))


class RandomPathwayConnectionVariate(
        CircuitPropertyRandomVariate):
    """Generate random pair of cell gids..."""
    label = "connection"
    value_type = tuple
    condition_type=\
        Record(mtype_pathway=tuple) #(int, int)

    def __init__(self,
            circuit_model,
            *args, **kwargs):
        """..."""
        self.random_pre_cell=\
            RandomCellVariate(
                circuit_model,
                *args, **kwargs)
        self.random_post_cell=\
            RandomCellVariate(
                circuit_model,
                *args, **kwargs)
        #self.__conn_cache__ = {}
        super().__init__(
            circuit_model=circuit_model,
            reset_condition_type=False,
            columns=["pre_gid", "post_gid"],
            *args, **kwargs)

    def __call__(self,
            condition,
            *args, **kwargs):
        """...Call Me..."""
        pathway=\
            condition.get_value(
                "mtype_pathway")
        return (
            self.random_pre_cell(
                Condition([
                    ("mtype", pathway[0])])),
            self.random_post_cell(
                 Condition([
                    ("mtype", pathway[1])])))
