from bluepy.v2.circuit import Circuit
from dmt.vtk.utils.descriptor import Field, WithFCA
from neuro_dmt.models.bluebrain.build import CircuitGeometry
from neuro_dmt.models.bluebrain.atlas.build\
    import AtlasCircuitGeometry, IsoCortexAtlasBasedSpecialization

class CircuitModel(
        WithFCA):
    """Wrap a BluePy circuit to provide its associated geometry,
    along with other information such as it's release date..."""
    circuit_config\
        = Field(
            __name__="circuit_config",
            __type__=str,
            __doc__="""Path to the circuit config that can be loaded
            as a BluePy Circuit.""")
    geometry_type\
        = Field(
            __name__="geometry_type",
            __type__=type,
            __typecheck__=Field.typecheck.subtype(CircuitGeometry),
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
        self.__impl = None #the implied bluepy circuit
        self.__geometry = None

    @property
    def circuit(self):
        """..."""
        if not self.__impl:
            self.__impl = Circuit(self.circuit_config)
        return self.__impl

    @property
    def geometry(self):
        """..."""
        if not self.__geometry:
            self.__geometry = self.geometry_type(self.__impl)
        return self.__geometry

    @property
    def bluepy_circuit(self):
        """..."""
        if not self.__impl:
            self.__impl = Circuit(self.circuit_config)
        return self.__impl


class AtlasBasedCircuitModel(
        CircuitModel):
    """..."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            geometry_type=AtlasCircuitGeometry)


class IsoCortexAtlasBasedCircuitModel(
        CircuitModel):
    """..."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            geometry_type=IsoCortexAtlasBasedCircuitModel)

