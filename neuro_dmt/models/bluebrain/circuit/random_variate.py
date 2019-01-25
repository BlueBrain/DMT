"""BBP specific random variates, and related utilities."""
from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from bluepy.v2.enums import Cell
from bluepy.geometry.roi import ROI as RegionOfInterest
from dmt.vtk.utils.collections import *
from dmt.vtk.measurement.parameter import Parameter
from dmt.vtk.measurement.parameter.finite\
    import FiniteValuedParameter
from dmt.vtk.measurement.parameter.random\
    import ConditionedRandomVariate
from dmt.vtk.utils.logging import Logger, with_logging
from dmt.vtk.utils.descriptor import Field, WithFCA

from neuro_dmt.utils.brain_regions import BrainRegion
from neuro_dmt.models.bluebrain.circuit.build\
    import CircuitGeometry
from neuro_dmt.models.bluebrain.circuit.geometry\
    import  Cuboid,  random_location
   


@with_logging(Logger.level.STUDY)
class RandomSpatialVariate(
        ConditionedRandomVariate):
    """Generator of random values, for a (blue) brain circuit."""
    circuit_geometry = Field(
        __name__="circuit_geometry",
        __type__=CircuitGeometry,
        __doc__="""Provides circuit build geometry specific attribute specializations.
        Ideally we should be able to get this information from  'circuit'.""")
    
    def __init__(self,
            circuit_geometry,
            condition_type=Record(),
            *args, **kwargs):
        """...
        Parameters
        ------------------------------------------------------------------------
        circuit :: bluepy.v2.Circuit,
        """
        self.circuit_geometry\
            = circuit_geometry
        super().__init__(
            condition_type=condition_type,
            *args, **kwargs)

    def given(self,
            *conditioning_vars):
        """Set the condition type."""
        self.logger.debug(
            self.logger.get_source_info(),
            """RandomSpatialVariate with conditioning vars {}"""\
            .format(conditioning_vars))
        return super().given(
            *conditioning_vars,
            reset_condition_type=True)


class RandomPosition(
        RandomSpatialVariate):
    """Generate random positions in the circuit region."""
    label = "position"
    value_type = np.ndarray #dimension 3

    def __init__(self,
            circuit_geometry,
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
            circuit_geometry,
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
    
    def row(self, condition, value):
        """..."""
        return pd.DataFrame(
            [[value[0], value[1], value[2]]],
            columns=pd.Index(
                ["X", "Y", "Z"],
                name="axis"),
            index=condition.index)


class RandomCrossectionalPoint(
        RandomPosition):
    """..."""
    def __init__(self,
            circuit_geometry,
            offset=50.,
            *args, **kwargs):
        """..."""
        super().__init__(
            circuit_geometry,
            offset=offset,
            *args, **kwargs)

    def __call__(self,
            condition,
            *args, **kwargs):
        """..."""
        return self.circuit_geometry\
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
            circuit_geometry,
            sampled_box_shape=100.*np.ones(3),
            *args, **kwargs):
        """..."""
        self.sampled_box_shape = sampled_box_shape
        self.random_position\
            = RandomPosition(
                circuit_geometry,
                offset=sampled_box_shape/2.,
                *args, **kwargs)
        super().__init__(
            circuit_geometry,
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
        return Cuboid(
            position - half_box,
            position + half_box)
    
    def row(self,
            condition,
            value):
        """..."""
        return pd.DataFrame(
            [value],
            columns=[self.label],
            index=condition.index)


class RandomSpanningColumnOfInterest(
        RandomSpatialVariate):
    """A random column of interest is a random region of interest
    that spans the entire columnar dimension of the circuit.
    While well defined for O1 micro-circuits, we will have to be creative
    to define an equivalent definition for atlas based circuits."""

    value_type = RegionOfInterest
    label = "region_of_interest" 

    def __init__(self,
            circuit_geometry,
            crossection=50.,
            *args, **kwargs):
        """..."""
        self.__crossection\
            = crossection
        super().__init__(
            circuit_geometry,
            *args, **kwargs)

    def __call__(self,
            condition,
            *args, **kwargs):
        """Call Me"""
        return\
            self.circuit_geometry\
                .random_spanning_column(
                    condition,
                    crossection=self.__crossection)

    def row(self,
            condition,
            value):
        """..."""
        return\
            pd.DataFrame(
                [value],
                columns=[self.label],
                index=condition.index)
    

class RandomBoxCorners(
        RandomSpatialVariate):
    """..."""
    value_type = tuple #length 2
    label = "box_corners"
    def __init__(self,
            circuit_geometry,
            sampled_box_shape=50.*np.ones(3),
            *args, **kwargs):
        """..."""
        self.random_region_of_interest\
            = RandomRegionOfInterest(
                circuit_geometry,
                sampled_box_shape=sampled_box_shape,
                *args, **kwargs)
        super().__init__(
            circuit_geometry,
            sampled_box_shape=sampled_box_shape,
            *args, **kwargs)

    def __call__(self,
            condition,
            *args, **kwargs):
        """"..."""
        return\
            self.random_region_of_interest(
                condition,
                *args, **kwargs).bbox

    def row(self,
            condition,
            value):
        """..."""
        columns\
            = pd.MultiIndex.from_tuples(
                [("p0", "X"), ("p0", "Y"), ("p0", "Z"),
                 ("p1", "X"), ("p1", "Y"), ("p1", "Z")],
                names=["box_corners", "axis"])
        return pd.DataFrame(
            [[value[0][0], value[0][1], value[0][2],
              value[1][0], value[1][1], value[1][2]]],
            columns=columns,
            index=condition.index)
