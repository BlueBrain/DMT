"""Build Geometry of a circuit."""
from abc import ABC, abstractmethod
from bluepy.v2.circuit import Circuit
from dmt.vtk.utils.collections import Record
from dmt.vtk.utils.descriptor import Field, WithFCA
from neuro_dmt.utils.brain_regions import BrainRegion
from neuro_dmt.models.bluebrain.circuit import BlueBrainModelHelper
from neuro_dmt.models.bluebrain.circuit.brain_regions import BrainRegionSpecific

class CircuitGeometry(WithFCA, ABC):
    """Geometry of a circuit! Dump all circuit build geometry 
    dependent method definitions here."""

    _circuit\
        = Field(
            __name__="_circuit",
            __type__=Circuit,
            __doc__="""The circuit that this geometry is about.""")

    label = Field(
        __name__="label",
        __type__=str,
        __doc__="A label for the circuit build geometry.",
        __examples__=["O1", "O1.v6a", "Atlas-based", "S1", "S1.v6a"])

    specializations = Field(
        __name__="specializations",
        __type__=dict,
        __is_valid_value__=Field.typecheck.mapping(
            BrainRegion,
            BrainRegionSpecific),
        __doc__="""Maps brain region to a code specialization
        for that brain region.""")
    
    def __init__(self,
            circuit,
            *args, **kwargs):
        """..."""
        kwargs["_circuit"] = circuit
        self._helper = BlueBrainModelHelper(circuit=circuit)
        super().__init__(*args, **kwargs)

    @abstractmethod
    def random_position(self, condition):
        """..."""
        pass

    @abstractmethod
    def random_column(self, crosssection):
        """..."""
        raise NotImplementedError()

    @abstractmethod
    def column_parameter(self, *args, **kwargs):
        """Spatial parameter representing a column that spans all the layers
        (or another sub-region) of a brain region. Unlike sub-region (layer),
        this spatial parameter Column depends on the (geometric) build of the
        circuit."""
        pass

    def get_brain_region_spec(self,
            brain_region):
        """..."""
        if hasattr(self, "region_specialization"):
            return self.region_specialization
        try:
            return self.specializations[
                brain_region]
        except KeyError as e:
            raise NotImplementedError(
                "Brain region specialization for {}"\
            .format(brain_region))
