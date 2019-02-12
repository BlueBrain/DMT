"""Circuit models from the Blue Brain Project"""
import sys
import bluepy
from bluepy.v2.circuit\
    import Circuit
from dmt.vtk.utils.descriptor\
    import Field\
    ,      WithFCA
from neuro_dmt.utils\
    import brain_regions
from neuro_dmt.models.bluebrain.circuit.build\
    import CircuitGeometry


class BlueBrainCircuitModel(
        WithFCA):
    """Wrap a bluepy circuit to provide its associated geometry,
    along with other information such as it's release data..."""

    label=\
        "BlueBrainCircuitModel"
    circuit_config=\
        Field(
            __name__ = "circuit_config",
            __type__ = str,
            __doc__ = """Path tot he circuit config that can be loaded as a
            bluepy circuit.""")
    geometry_type=\
        Field(
            __name__ = "geometry_type",
            __type__ = type,
            __typecheck__ = Field.typecheck.subtype(CircuitGeometry),
            __doc__ = """A plugin that provides methods for a circuit's
            geometry. A subtype of 'class CircuitGeometry' is expected.""")
    animal=\
        Field(
            __name__="animal",
            __type__=str,
            __doc__="Animal for which this circuit was built.")
    brain_region=\
        Field(
            __name__ = "brain_region",
            __type__ = brain_regions.BrainRegion,
            __doc__ = "The brain region modeled.")

    def __init__(self,
            *args, **kwargs):
        super().__init__(
            *args, **kwargs)
        self._implied_circuit = None #the implied bluepy circuit
        self._geometry = None

    @property
    def bluepy_circuit(self):
        """..."""
        if not self._implied_circuit:
            self._implied_circuit=\
                Circuit(self.circuit_config)
        return self._implied_circuit
                    
    @property
    def circuit(self):
        """..."""
        return self.bluepy_circuit

    @property
    def geometry(self):
        """..."""
        if not self._geometry:
            self._geometry=\
                self.geometry_type(
                    self.circuit)
        return\
            self._geometry

    @property
    def connectome(self):
        """..."""
        try:
            return self.bluepy_circuit.connectome
        except bluepy.exceptions.BluePyError as e:
            self.logger.alert(
                self.logger.get_source_info(), 
                "circuit does not have a connectome",
                "Caught Exception :\n  {}".format(e))
            return None

    def get_cell_group(self,
            cell_group):
        """
        Arguments
        ------------
        cell_group :: dict #accepted by bluepy.v2.circuit.cell

        Return
        ------------
        List[GIDs]

        Improvement
        -----------
        Add a validation to check that 'cell_group' has keys acceptable to
        bluepy.v2.circuit.cells.get, and to filter out invalid keys.
        """
        return list(self\
                    .bluepy_circuit\
                    .cells\
                    .get(
                        cell_group,
                        properties=[]
                    ).index)


from neuro_dmt.models.bluebrain.circuit.circuit_model.o1_circuit_model\
    import O1CircuitModel
from neuro_dmt.models.bluebrain.circuit.circuit_model.atlas_based_circuit_model\
    import AtlasBasedCircuitModel\
    ,      FakeAtlasBasedCircuitModel


