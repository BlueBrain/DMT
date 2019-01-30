from bluepy.v2.circuit import Circuit
from voxcell.nexus.voxelbrain import LocalAtlas
from dmt.vtk.utils.descriptor import Field, WithFCA
from neuro_dmt.utils import brain_regions 
from neuro_dmt.models.bluebrain.circuit.build\
    import CircuitGeometry
from neuro_dmt.models.bluebrain.circuit.O1.build\
    import O1CircuitGeometry
from neuro_dmt.models.bluebrain.circuit.atlas.fake.build\
    import FakeAtlasCircuitGeometry
from neuro_dmt.models.bluebrain.circuit.atlas.build\
    import AtlasCircuitGeometry

class BlueBrainCircuitModel(
        WithFCA):
    """Wrap a BluePy circuit to provide its associated geometry,
    along with other information such as it's release date..."""
    label=\
        "BlueBrainCircuitModel"
    circuit_config=\
        Field(
            __name__="circuit_config",
            __type__=str,
            __doc__="""Path to the circuit config that can be loaded
            as a BluePy Circuit.""")
    geometry_type=\
        Field(
            __name__="geometry_type",
            __type__=type,
            __typecheck__=Field.typecheck.subtype(CircuitGeometry),
            __doc__="""A plugin that provides methods for a circuit's
            geometry. A subtype of 'class CircuitGeometry' is expected
            --- that uses keyword arguments for initialization,
            and will be initialized by passing circuit as a keyword
            argument.""")
    animal=\
        Field(
            __name__="animal",
            __type__=str,
            __doc__="Animal for which this circuit was built.")
    brain_region=\
        Field(
            __name__="brain_region",
            __type__=brain_regions.BrainRegion,
            __doc__="The brain region modeled.")

    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args, **kwargs)
        self._impl = None #the implied bluepy circuit
        self.__geometry = None

    @property
    def circuit(self):
        """..."""
        return self.bluepy_circuit

    @property
    def geometry(self):
        """..."""
        if not self.__geometry:
            self.__geometry=\
                self.geometry_type(
                    self.circuit)
        return\
            self.__geometry

    @property
    def bluepy_circuit(self):
        """..."""
        if not self._impl:
            self._impl=\
                Circuit(
                    self.circuit_config)
        return\
            self._impl

    @property
    def connectome(self):
        """"..."""
        raise NotImplementedError


class O1CircuitModel(
        BlueBrainCircuitModel):
    """..."""
    label = "BlueBrainO1CircuitModel"
    geometry_type\
        = Field(
            __name__="geometry_type",
            __type__=type,
            __typecheck__=Field.typecheck.subtype(O1CircuitGeometry),
            __doc__="""A plugin that provides methods for a circuit's
            geometry. A subtype of 'class CircuitGeometry' is expected
            --- that uses keyword arguments for initialization,
            and will be initialized by passing circuit as a keyword
            argument.""")

    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args, **kwargs)


class AtlasBasedCircuitModel(
        BlueBrainCircuitModel):
    """..."""
    label=\
        "BlueBrainAtlasBasedCircuitModel"
    geometry_type=\
        Field(
            __name__="geometry_type",
            __type__=type,
            __typecheck__=Field.typecheck.subtype(AtlasCircuitGeometry),
            __doc__="""A plugin that provides methods for a circuit's
            geometry. A subtype of 'class CircuitGeometry' is expected
            --- that uses keyword arguments for initialization,
            and will be initialized by passing circuit as a keyword
            argument.""")
    atlas_path=\
        Field.Optional(
            __name__="atlas_path",
            __type__=str,
            __doc__="""Path to the circuit's atlas. Provide this
            if atlas attribute has not been defined for the circuit.""")
    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args, **kwargs)

    @property
    def bluepy_circuit(self):
        """Over-ride to check, and set the circuit's atlas."""
        if not self._impl:
            c = Circuit(self.circuit_config)
            try:
                circuit_atlas=\
                    c.atlas
            except KeyError as e:
                if not hasattr(self, "atlas_path"):
                    raise TypeError(
                        """Circuit model {} has neither a (working) 'atlas',
                        nor an 'atlas_path' attribute.""".format(self))
                c.atlas=\
                    LocalAtlas(
                        self.atlas_path)
            self._impl = c
        return self._impl


class FakeAtlasBasedCircuitModel(
        AtlasBasedCircuitModel):
    """..."""
    label = "BlueBrainO1v6CircuitModel"
    geometry_type\
        = Field(
            __name__="geometry_type",
            __type__=type,
            __typecheck__=Field.typecheck.subtype(FakeAtlasCircuitGeometry),
            __doc__="""A plugin that provides methods for a circuit's
            geometry. A subtype of 'class CircuitGeometry' is expected
            --- that uses keyword arguments for initialization,
            and will be initialized by passing circuit as a keyword
            argument.""")

    def __init__(__init__,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args, **kwargs)

