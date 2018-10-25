"""Brain regions covered by BlueBrain circuits, or the regions that we have
adapters for"""

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

from neuro_dmt.utils.brain_regions import BrainRegion
from neuro_dmt.models.bluebrain.circuit import BlueBrainModelHelper
from neuro_dmt.models.bluebrain.circuit.geometry import \
    Cuboid,  random_location

#@with_logging(Logger.level.STUDY)
class BrainRegionSpecific(
        WithFCA,
        ABC):
    """Brain region specific methods.
    These methods will typcially be abstract in some other code.
    BrainRegionSpecific classes will not be useful on their known.
    They simply provide code specialized to particular brain regions."""

    brain_region = Field(
        __name__="brain_region",
        __type__=BrainRegion,
        __doc__="""A utility class object that contains some generic information
        about the brain region that this BrainRegionSpecific codes for.""")
    
    cell_group_params = Field(
        __name__="cell_group_params",
        __type__=tuple,
        __doc__="""Tuple of cell query fields that group cells, and whose values
        measurements will be (jointly) conditioned on. Use this information to
        create cell queries. You can stick in anything here that a cell
        query will accept. The entries here must be a subset of condition_type
        fields.""",
        __default__=(Cell.LAYER,
                     Cell.REGION,
                     "$target",
                     Cell.SYNAPSE_CLASS,
                     Cell.MORPH_CLASS,
                     Cell.ETYPE,
                     Cell.MTYPE),
        __examples__=[("layer", "target"), ("layer", ), ("mtype", "layer",)])
    
    def __init__(self,
            target=None,
            *args, **kwargs):
        """...

        Parameters
        ------------------------------------------------------------------------
        cell_group_params :: tuple #...
        """
        self._target = target
            
        try:
            super().__init__(
                *args, **kwargs)
        except:
            pass
        
    @property
    def region_label(self):
        """..."""
        return self.brain_region.label

    @property
    def target(self):
        """..."""
        if not self._target:
            self.logger.alert(
                self.logger.get_source_info(),
                "No target set for {} instance."\
                .format(self.__class__.__name__))
        return self._target

    def with_target(self,
            query_dict,
            target_label="$target"):
        """Add target to a condition.

        Note
        ------------------------------------------------------------------------
        We need to find a more elegant solution to sticking target in queries.
        """
        self.logger.devnote(
            self.logger.get_source_info(),
            """{}.with_target is a hack. We stick the target in. We should look
            for a more disciplined and elegant solution."""\
            .format(self.__class__.__name__))
        query_dict[target_label]\
            = self._target
        return query_dict

    def cell_query(self,
            condition,
            *args, **kwargs):
        """A dict that can be passed to circuit.cells.get(...).
        Concrete implementation may override """
        return {
            param: condition.get_value(param)
            for param in self.cell_group_params
            if param in condition}
