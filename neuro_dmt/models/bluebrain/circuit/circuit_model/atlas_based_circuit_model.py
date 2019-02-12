"""Blue brain circuit models based on an Atlas."""

from bluepy.v2.circuit\
    import Circuit
from voxcell.nexus.voxelbrain\
    import LocalAtlas
from dmt.vtk.utils.descriptor\
    import Field
from neuro_dmt.models.bluebrain.circuit.atlas.build\
    import AtlasCircuitGeometry
from neuro_dmt.models.bluebrain.circuit.atlas.fake.build\
    import  FakeAtlasCircuitGeometry
from neuro_dmt.models.bluebrain.circuit.circuit_model\
    import BlueBrainCircuitModel


class AtlasBasedCircuitModel(
        BlueBrainCircuitModel):
    """..."""

    label=\
        "BlueBrainAtlasBasedCircuitModel"
    geometry_type=\
        Field(
            __name__ = "geometry_type",
            __typecheck__ = Field.typecheck.subtype(AtlasCircuitGeometry),
            __doc__ = """A plugin that provides methods for a circuit's
            geometry.""")
    atlas_path=\
        Field.Optional(
            __name__ = "atlas_path",
            __type__ = str,
            __doc__ = """Path to the cirucit's atlas. Provide this path if an
            atlas attribute has not been defined for the cirucit.""")

    @property
    def bluepy_circuit(self):
        """Override to check, and set the circuit's atlas."""
        if not self._implied_circuit:
            circuit=\
                Circuit(self.circuit_config)
            try:
                circuit_atlas=\
                    circuit.atlas
            except KeyError as err:
                if not hasattr(self, "atlas_path"):
                    raise TypeError(
                    """Circuit model {} has neither a (working)
                    'atlas' attribute, nor an 'atlas_path' attribute
                    to load the atlas from.""".format(self))
                circuit.atlas=\
                    LocalAtlas(self.atlas_path)
            self._implied_circuit= circuit
        return self._implied_circuit


class FakeAtlasBasedCircuitModel(
        AtlasBasedCircuitModel):
    """..."""
    label=\
        "BlueBrainO1v6CircuitModel"
    geometry_type=\
        Field(
            __name__ = "geometry_type",
            __typecheck__ = Field.typecheck.subtype(FakeAtlasCircuitGeometry),
            __doc__ = """A plugin that provides methods for a circuit's
            geometry.""")
    pass
                
            
