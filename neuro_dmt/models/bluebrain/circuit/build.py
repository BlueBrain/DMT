"""Build of a circuit."""
from abc import ABC, abstractmethod
from dmt.vtk.utils.descriptor import Field, WithFCA
from neuro_dmt.utils.brain_regions import BrainRegion
from neuro_dmt.models.bluebrain.circuit import BlueBrainModelHelper
from neuro_dmt.models.bluebrain.circuit.brain_regions import BrainRegionSpecific

class CircuitBuild(WithFCA, ABC):
    """Build of a circuit! Dump all circuit build dependent method
    definitions here."""

    specializations = Field(
        __name__="specializations",
        __type__=dict,
        __is_valid_value__=Field.typecheck.mapping(BrainRegion, BrainRegionSpecific),
        __doc__="""Maps brain region to a code specialization for that brain region."""
    )
    def __init__(self, circuit, *args, **kwargs):
        """..."""
        self._circuit = circuit
        self._helper = BlueBrainModelHelper(circuit=circuit)
        super(CircuitBuild, self).__init__(*args, **kwargs)

    @abstractmethod
    def random_position(self, condition):
        """..."""
        pass
