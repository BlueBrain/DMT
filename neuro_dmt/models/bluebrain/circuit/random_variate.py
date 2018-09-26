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
from neuro_dmt.models.bluebrain.circuit.build import CircuitBuild
from neuro_dmt.models.bluebrain.circuit.geometry import \
    Cuboid,  random_location


class CircuitRandomVariate(ConditionedRandomVariate):
    """Generator of random values, for a (blue) brain circuit."""
    brain_region = Field(
        __name__="brain_region",
        __type__=BrainRegion,
        __doc__="Provides brain region specializations of some attributes."
    )
    circuit_build = Field(
        __name__="circuit_build",
        __type__=CircuitBuild,
        __doc__="""Provides circuit build specific attribute specializations.
        Ideally we should be able to get this information from  'circuit'."""
    )
    def __init__(self, circuit, circuit_build, brain_region,
                 condition_type=Record(),
                 *args, **kwargs):
        """...
        Parameters
        ------------------------------------------------------------------------
        circuit :: bluepy.v2.Circuit,
        brain_region :: BrainRegion #for brain region specific methods
        """
        self._circuit = circuit
        self.circuit_build = circuit_build(circuit)
        self.brain_region = brain_region
        self._helper = BlueBrainModelHelper(circuit=circuit)
        super(CircuitRandomVariate, self)\
            .__init__(condition_type=condition_type,
                      *args, **kwargs)

    def given(self, *conditioning_vars):
        """Set the condition type."""
        return super(CircuitRandomVariate, self)\
            .given(*conditioning_vars, reset_condition_type=True)

    @property
    def circuit(self):
        """..."""
        return self._circuit

    @property
    def helper(self):
        """..."""
        return self._helper


class RandomPosition(CircuitRandomVariate):
    """Generate random positions in the circuit region."""
    label = "position"
    value_type = np.ndarray #dimension 3

    def __init__(self, circuit, circuit_build, brain_region,
                 offset=50., *args, **kwargs):
        """...
        Parameters
        ------------------------------------------------------------------------
        circuit :: bluepy.v2.Circuit,
        circuit_build :: type #<: CircuitBuild
        """
        self.offset = offset
        super(RandomPosition, self)\
            .__init__(circuit, circuit_build, brain_region, *args, **kwargs)

    def cell_query(self, condition, *args, **kwargs):
        """...redirect to brain region.
        This allows us to not have to subclass from RandomPosition and 
        BrainRegionSpecific mixins. We can redirect to 'self.brain_region'.
        We could """
        return self.brain_region.cell_query(condition, *args, **kwargs)

    def __call__(self, condition, *args, **kwargs):
        """..."""
        return self.circuit_build.random_position(self.brain_region, condition,
                                                  *args, **kwargs)
                                                  

    def row(self, condition, value):
        """..."""
        return pd.DataFrame(
            [[value[0], value[1], value[2]]],
            columns=pd.Index(["X", "Y", "Z"], name="axis"),
            index=condition.index
        )


class RandomRegionOfInterest(RandomPosition):
    """Random ROIs"""
    value_type = ROI
    label = "roi"

    def __init__(self, circuit, circuit_build, brain_region,
                 sampled_box_shape=100.*np.ones(3),
                 *args, **kwargs):
        """..."""
        self.sampled_box_shape = sampled_box_shape
        super(RandomRegionOfInterest, self)\
            .__init__(circuit, circuit_build, brain_region,
                      offset=sampled_box_shape/2.,
                      *args, **kwargs)

    def __call__(self, condition, *args, **kwargs):
        """..."""
        half_box = self.sampled_box_shape / 2.
        position = super(RandomRegionOfInterest, self)\
                    .__call__(condition, *args, **kwargs)
        return Cuboid(position - half_box, position + half_box)

    def row(self, condition, value):
        """..."""
        return pd.DataFrame(
            [value],
            columns=[self.label],
            index=condition.index
        )


class RandomBoxCorners(RandomRegionOfInterest):
    """..."""
    value_type = tuple #length 2
    label = "box_corners"
    def __init__(self, circuit, circuit_build, brain_region,
                 sampled_box_shape=50.*np.ones(3),
                 *args, **kwargs):
        """..."""
        super(RandomBoxCorners, self)\
            .__init__(circuit, circuit_build, brain_region,
                      sampled_box_shape=sampled_box_shape,
                      *args, **kwargs)

    def __call__(self, condition, *args, **kwargs):
        """"..."""
        roi = super(RandomBoxCorners, self)\
              .__call__(condition, *args, **kwargs)
              
        return roi.bbox

    def row(self, condition, value):
        """..."""
        columns = pd.MultiIndex.from_tuples(
            [("p0", "X"), ("p0", "Y"), ("p0", "Z"),
             ("p1", "X"), ("p1", "Y"), ("p1", "Z")],
            names=["box_corners", "axis"]
        )
        return pd.DataFrame(
            [[value[0][0], value[0][1], value[0][2],
              value[1][0], value[1][1], value[1][2]]],
            columns=columns,
            index=condition.index
        )



