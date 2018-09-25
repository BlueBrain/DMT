"""Build of a circuit."""
from abc import ABC, abstractmethod
from dmt.vtk.utils.descriptor import Field, WithFCA
from neuro_dmt.models.bluebrain.circuit import BlueBrainModelHelper

class CircuitBuild(WithFCA, ABC):
    """Build of a circuit! Dump all circuit build dependent method
    definitions here."""

    def __init__(self, circuit, *args, **kwargs):
        """..."""
        self._circuit = circuit
        self._helper = BlueBrainModelHelper(circuit=circuit)
        super(CircuitBuild, self).__init__(*args, **kwargs)

    @abstractmethod
    def random_position(self, condition):
        """..."""
        pass
