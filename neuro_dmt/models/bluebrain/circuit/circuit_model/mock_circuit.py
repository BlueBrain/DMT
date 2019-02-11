"""A mock circuit mimicking Blue Brain Project's circuit ---
that may be used for developing circuit analyses."""

from dmt.vtk.utils.descriptor\
    import Field
from neuro_dmt.models.bluebrain.circuit.circuit_model\
    import BlueBrainCircuitModel
from neuro_dmt.models.bluebrain.circuit.mock.build\
    import MockCircuitGeometry

class MockCircuitModel(
        BlueBrainCircuitModel):
    label=\
        "BlueBrainMockCircuitModel"
    geometry_type=\
        Field(
            __name__ = "geometry_type",
            __typecheck__ = Field.typecheck.subtype(MockCircuitGeometry),
            __doc__ = """A plugin that provides methods for a circuit's
            geometry""")
    pass
