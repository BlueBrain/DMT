"""Build geometry of a mock circuit."""

import numpy as np
from dmt.vtk.utils.descriptor\
    import Field
from neuro_dmt.models.bluebrain.circuit.specialization\
    import CircuitSpecialization
from neuro_dmt.models.bluebrain.circuit.build\
    import CircuitGeometry
from neuro_dmt.models.bluebrain.circuit\
    import BlueBrainModelHelper
from neuro_dmt.models.bluebrain.circuit.mock\
    import MockCircuit

class MockCircuitSpecialization(
        CircuitSpecialization):
    """Mock circuit specialization --- provides nothing,
    as there is nothing to specialize for."""
    pass

class MockCircuitGeometry(
        CircuitGeometry):
    """Provide random returns from CircuitGeometry's abstractmethods."""

    label=\
        "Mock"
    circuit=\
        Field(
            __name__ = "circuit",
            __type__ = MockCircuit,
            __doc__  = """The circuit that this geometry is for.""")

    def __init__(self,
            circuit,
            *args, **kwargs):
        """..."""
        super().__init__(
            circuit,
            *args, **kwargs)

    def random_position(self,
            condition):
        """"..."""
        return np.random.uniform(0., 1.)

    def spanning_column_parameter(self,
            regions=[],
            *args, **kwargs):
        """..."""
        raise NotImplementedError()
