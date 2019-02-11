"""Blue Brain (micro) circuit models based on the O1 geometry."""

from dmt.vtk.utils.descriptor\
    import Field
from neuro_dmt.models.bluebrain.circuit.O1.build\
    import O1CircuitGeometry
from neuro_dmt.models.bluebrain.circuit.circuit_model\
    import BlueBrainCircuitModel

class O1CircuitModel(
        BlueBrainCircuitModel):
    """..."""

    label=\
        "BlueBrainO1CircuitModel"
    geometry_type=\
        Field(
            __name__ = "geometry_type",
            __typecheck__ = Field.typecheck.subtype(O1CircuitGeometry),
            __doc__ = """A plugin that provides methods for a circuit's
            geometry.""")
    pass

