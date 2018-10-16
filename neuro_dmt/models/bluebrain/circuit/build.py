"""Build of a circuit."""
from abc import ABC, abstractmethod
from dmt.vtk.utils.collections import Record
from dmt.vtk.utils.descriptor import Field, WithFCA
from neuro_dmt.utils.brain_regions import BrainRegion
from neuro_dmt.models.bluebrain.circuit import BlueBrainModelHelper
from neuro_dmt.models.bluebrain.circuit.brain_regions import BrainRegionSpecific

class CircuitBuild(WithFCA, ABC):
    """Build of a circuit! Dump all circuit build dependent method
    definitions here."""

    label = Field(
        __name__="label",
        __type__=str,
        __doc__="A label for the circuit build.",
        __examples__=["O1", "O1.v6a", "Atlas-based", "S1", "S1.v6a"])

    geometry = Field(
        __name__="geometry",
        __type__=Record,
        __doc__="Contains information about O1 geometry")

    specializations = Field(
        __name__="specializations",
        __type__=dict,
        __is_valid_value__=Field.typecheck.mapping(
            BrainRegion,
            BrainRegionSpecific),
        __doc__="""Maps brain region to a code specialization
        for that brain region.""")
    
    def __init__(self, circuit, *args, **kwargs):
        """..."""
        self._circuit = circuit
        self._helper = BlueBrainModelHelper(circuit=circuit)
        super(CircuitBuild, self).__init__(*args, **kwargs)

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

    def brain_region_spec(self,
            brain_region):
        """..."""
        try:
            return self.specializations[
                brain_region]
        except KeyError as e:
            raise NotImplementedError(
                "Brain region specialization for {}"\
            .format(brain_region))
