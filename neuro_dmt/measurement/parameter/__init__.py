"""Parameters relevant for neuroscience measurements ---
these can be used as base classes by model adapters, and required and coded
against by validation authors. The author of a model adapter then has to just
look up the documentation to write an appropriate base class."""

from dmt.vtk.measurement.parameter.finite import FiniteValuedParameter
from dmt.vtk.utils.descriptor import Field
from neuro_dmt.utils import brain_regions
from neuro_dmt.utils.brain_regions import BrainRegion


class BrainCircuitMeasurementParameter(
        FiniteValuedParameter):
    """..."""

    brain_region = Field(
        __name__="brain_region",
        __type__=BrainRegion,
        __doc__="""A utility class object that contains some generic information
        about the brain region that this BrainCircuitMeasurementParameter
        is for. You can always us brain_regions.whole_brain!""")
    
    def __init__(self,
            *args, **kwargs):
        """..."""
        if "brain_region" not in kwargs:
            super().__init__(
                brain_region=brain_regions.whole_brain,
                *args, **kwargs)
        else:
            super().__init__(
                *args, **kwargs)


class BrainCircuitSpatialParameter(
        BrainCircuitMeasurementParameter):
    """This class exists to define a type of parameters for measurements
    of the brain. We will add useful features as we discover common behavior
    of various spatial parameters that we will implement.
    """
    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args, **kwargs)
        self.brain_region\
            .add_spatial_parameter(
                self.__class__)


class LayerIndex(
        BrainCircuitSpatialParameter):
    """An abstract base class to represent a generic layer in any brain region.
    Model Adaptors must implement the interface presented here to use
    validations from our library. We will specialize a Layer's attributes
    in several stages of sub-classing.

    Notes
    ----------------------------------------------------------------------------
    If we want the two ends of a validation to work independently, then
    Parameter should be a mechanism of communication. Parameter can be used to
    set the protocol."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        if "label" not in kwargs:
            super().__init__(
                label="layer",
                *args, **kwargs)
        else:
            super().__init__(
                *args, **kwargs)


class CorticalLayer(
        LayerIndex):
    """A layer in the cortex."""

    def __init__(self,
            *args, **kwargs):
        """Default cortical layer will have int values 1, 2, 3, 4, 5, and 6.
        The user may override this initializer."""
        super().__init__(
            brain_region=brain_regions.cortex,
            value_type=int,
            values=[1, 2, 3, 4, 5, 6],
            value_repr={1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI"},
            *args, **kwargs)
        

class CorticalLayer23Fused(
        LayerIndex):
    """Represents cortical layers, when layers 2 and 3 are fused into one."""

    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(
            brain_region=brain_regions.cortex,
            value_type=str,
            values=["L1", "L23", "L4", "L5", "L6"],
            value_repr={"L1": "I", "L23": "II/III", 
                        "L4":"IV", "L5": "V", "L6": "VI"},
            *args, **kwargs)


class CorticalLayer5abSplit(
        LayerIndex):
    """Represents cortical layers when layer 5 is split into 5a, and 5b."""

    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            value_type=str,
            brain_region=brain_regions.cortex,
            values=["L1", "L2", "L3", "L4", "L5a", "L5b", "L6"],
            value_repr={"L1": "I", "L2": "II", "L3": "III",
                        "L4": "IV", "L5a": "Va", "L5b": "Vb", "L6": "VI"},
            *args, **kwargs)


class HippocampalLayer(
        LayerIndex):
    """Layer in the hippocampus."""

    def __init__(self,
            *args, **kwargs):
        """Default hippocampal layer will have int values 'SLM', 'SR', 'SP',
        and 'SO'. The user may override this initializer."""
        super().__init__(
            value_type=str,
            brain_region=brain_regions.hippocampus,
            values=["SLM", "SR", "SP", "SO"],
            *args, **kwargs)


class HippocampalLayerSLM_SR_Fused(
        LayerIndex):
    """..."""

    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(
            value_type=str,
            brain_region=brain_regions.hippocampus,
            values=["SLM-SR", "SP", "SO"],
            *args, **kwargs)


class Column(
        BrainCircuitSpatialParameter):
    """A column covers the entire region,
    orthogonally to the layers --- as much as possible."""

    def __init__(self,
            *args, **kwargs):
        """..."""
        if "label" not in kwargs:
            super().__init__(
                label="column",
                *args, **kwargs)
        else:
            super().__init__(
                *args, **kwargs)
