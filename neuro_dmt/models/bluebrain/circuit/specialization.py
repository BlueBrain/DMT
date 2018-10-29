"""Circuit instance specific methods and attributes.
BBP circuit building pipeline is under continuous development.
Most volatile parts can be placed here. In addition, the circuit
builder herself may customize circuit attributes, and will require her
circuit adapters to be aware of those customizations. The circuit builder can
subclass the base class provided here and specialize these methods and
attributes to use rest of the validation code."""

from abc import ABC, abstractmethod
from bluepy.v2.enums import Cell
from dmt.vtk.utils.descriptor import Field, WithFCA
from neuro_dmt.utils import brain_regions
from neuro_dmt.utils.brain_regions import BrainRegion

class CircuitSpecialization(
        WithFCA,
        ABC):
    """Abstract Base class that can be subclassed to define Mixins specialized
    for (very) specific BBP circuits."""
    
    brain_region = Field(
        __name__="brain_region",
        __type__=BrainRegion,
        __doc__="""A utility class instance that contains some generic
        information about the brain region that this CircuitSpecialization is
        specialized for.""",
        __default__=brain_regions.whole_brain)

    cell_group_params = Field(
        __name__="cell_group_params",
        __type__=tuple,
        __doc__="""Tuple of (BluePy query) fields that group cells. Measurements
        will be (jointly) conditioned on the values of these fields. Use this
        information to create cell queries. You can stick in anything that a
        cell query will accept. The entries must be a subset of condition_type
        fields.""",
        __default__=(Cell.LAYER,
                     Cell.REGION,
                     "$target",
                     Cell.SYNAPSE_CLASS,
                     Cell.MORPH_CLASS,
                     Cell.ETYPE,
                     Cell.MTYPE))

    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args, **kwargs)


    @property
    def region_label(self):
        """..."""
        return self.brain_region.label

    @property
    @abstractmethod
    def target(self):
        """You can specify a target of cells to study."""
        pass

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

    def query_param(self, param):
        """A parameter such as 'layer' may need to be something else
        in a bluepy query. Override this method if so,"""
        return param

    def cell_query(self,
            condition,
            *args, **kwargs):
        """A dict that can be passed to circuit.cells.get(...).
        Concrete implementation may override """
        return {
            self.query_param(param): condition.get_value(param)
            for param in self.cell_group_params
            if param in condition}
