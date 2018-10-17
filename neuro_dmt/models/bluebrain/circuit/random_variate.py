"""BBP specific random variates, and related utilities."""
from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from bluepy.v2.enums import Cell
from bluepy.geometry.roi import ROI
from dmt.vtk.utils.collections import *
from dmt.vtk.measurement.parameter import Parameter
from dmt.vtk.measurement.parameter.finite import FiniteValuedParameter
from dmt.vtk.measurement.parameter.random import ConditionedRandomVariate
from dmt.vtk.utils.logging import Logger, with_logging
from dmt.vtk.utils.descriptor import Field, WithFCA

from neuro_dmt.utils import brain_regions
from neuro_dmt.utils.brain_regions import BrainRegion

from neuro_dmt.models.bluebrain.circuit.brain_regions import BrainRegionSpecific
from neuro_dmt.models.bluebrain.circuit import BlueBrainModelHelper
from neuro_dmt.models.bluebrain.circuit.build import CircuitGeometry
from neuro_dmt.models.bluebrain.circuit.geometry import \
    Cuboid,  random_location


@with_logging(Logger.level.STUDY)
class CircuitRandomVariate(
        ConditionedRandomVariate):
    """Generator of random values, for a (blue) brain circuit."""
    brain_region = Field.Optional(
        __name__="brain_region",
        __type__=BrainRegion,
        __doc__="Provides brain region specializations of some attributes.")
    
    circuit_geometry = Field(
        __name__="circuit_geometry",
        __type__=CircuitGeometry,
        __doc__="""Provides circuit build geometry specific attribute specializations.
        Ideally we should be able to get this information from  'circuit'.""")
    
    def __init__(self,
            circuit,
            circuit_geometry,
            brain_region,
            condition_type=Record(),
            *args, **kwargs):
        """...
        Parameters
        ------------------------------------------------------------------------
        circuit :: bluepy.v2.Circuit,
        brain_region :: BrainRegion #for brain region specific methods
        """
        self._circuit\
            = circuit
        self.circuit_geometry\
            = circuit_geometry(
                circuit)
        self.brain_region\
            = brain_region
        self._helper\
            = BlueBrainModelHelper(
                circuit=circuit)
        super().__init__(
            condition_type=condition_type,
            *args, **kwargs)

    def given(self,
            *conditioning_vars):
        """Set the condition type."""
        self.__class__.logger.debug(
            self.__class__.logger.get_source_info(),
            """CircuitRandomVariate with conditioning vars {}"""\
            .format(conditioning_vars))
        return super().given(
            *conditioning_vars,
            reset_condition_type=True)

    @property
    def circuit(self):
        """..."""
        return self._circuit

    @property
    def helper(self):
        """..."""
        return self._helper

    def cell_query(self,
            condition,
            *args, **kwargs):
        """...redirect to brain region.
        This allows us to not have to subclass from RandomPosition and 
        BrainRegionSpecific mixins. We can redirect to 'self.brain_region'.
        We could """
        query.update(
            self.brain_region.cell_query(
                condition,
                *args, **kwargs))
        return query


class RandomPosition(
        CircuitRandomVariate):
    """Generate random positions in the circuit region."""
    label = "position"
    value_type = np.ndarray #dimension 3

    def __init__(self,
            circuit,
            circuit_geometry,
            brain_region,
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
            circuit,
            circuit_geometry,
            brain_region,
            *args, **kwargs)

    def __call__(self,
            condition,
            *args, **kwargs):
        """..."""
        self.logger.debug(
            self.logger.get_source_info(),
            """generate RandomPosition with condition {}"""\
            .format(condition.value))

        return self.circuit_geometry\
                   .random_position(
                       self.brain_region,
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


class RandomCrossection(
        RandomPosition):
    """..."""
    def __init__(self,
            cicuit,
            circuit_geometry,
            brain_region,
            offset=50.,
            *args, **kwargs):
        """..."""
        super().__init__(
            circuit,
            circuit_geometry,
            brain_region,
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
        CircuitRandomVariate):
    """Random ROIs"""
    value_type = ROI
    label = "roi"

    def __init__(self,
            circuit,
            circuit_geometry,
            brain_region,
            sampled_box_shape=100.*np.ones(3),
            *args, **kwargs):
        """..."""
        self.logger.debug(
            self.logger.get_source_info(),
            """Init RandomRegionOfInterest for brain region {}"""\
            .format(brain_region.label))
        self.sampled_box_shape = sampled_box_shape
        self.random_position\
            = RandomPosition(
                circuit,
                circuit_geometry,
                brain_region,
                offset=sampled_box_shape/2.,
                *args, **kwargs)
        super().__init__(
            circuit,
            circuit_geometry,
            brain_region,
            *args, **kwargs)

    def __call__(self,
            condition,
            *args, **kwargs):
        """..."""
        half_box\
            = self.sampled_box_shape / 2.
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


class RandomColumnOfInterest(
        RandomRegionOfInterest):
    """A random column of interest is a random region of interest
    that spans the entire columnar dimension of the circuit.
    While well defined for O1 micro-circuits, we will have to be creative
    to define an equivalent definition for atlas based circuits."""

    def __init__(self,
            circuit,
            circuit_geometry,
            brain_region,
            crossection = 100.,
            *args, **kwargs):
        """..."""
        self.crossection\
            = crossection
        self.random_position\
            = RandomCrossection(
                circuit,
                circuit_geometry,
                brain_region,
                offset=crossection/2.,
                *args, **kwargs)
        super().__init__(
            circuit,
            circuit_geometry,
            brain_region,
            sampled_box_shape=np.array([
                crossection,
                circuit_geometry.thickness,
                crossection]),
            *args, **kwargs)


class RandomBoxCorners(
        CircuitRandomVariate):
    """..."""
    value_type = tuple #length 2
    label = "box_corners"
    def __init__(self,
            circuit,
            circuit_geometry,
            brain_region,
            sampled_box_shape=50.*np.ones(3),
            *args, **kwargs):
        """..."""
        self.random_roi\
            = RandomRegionOfInterest(
                circuit,
                circuit_geometry,
                brain_region,
                sampled_box_shape=sampled_box_shape,
                *args, **kwargs)
        super().__init__(
            circuit,
            circuit_geometry,
            brain_region,
            sampled_box_shape=sampled_box_shape,
            *args, **kwargs)

    def __call__(self,
            condition,
            *args, **kwargs):
        """"..."""
        return self.random_roi(
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



