"""Build Geometry of a circuit."""
from abc import ABC, abstractmethod
from bluepy.v2.circuit import Circuit
from dmt.vtk.utils.collections import Record
from dmt.vtk.utils.descriptor import Field, WithFCA
from dmt.vtk.measurement.condition import Condition
from neuro_dmt.utils.brain_regions import BrainRegion
from neuro_dmt.models.bluebrain.circuit\
    import BlueBrainModelHelper
from neuro_dmt.models.bluebrain.circuit.specialization\
    import CircuitSpecialization


class CircuitGeometry(
        WithFCA,
        ABC):
    """Geometry of a circuit! Dump all circuit build geometry 
    dependent method definitions here."""

    circuit=\
        Field(
            __name__="circuit",
            __type__=Circuit,
            __doc__="""The circuit that this geometry is about.""")
    helper=\
        Field(
            __name__="helper",
            __type__=BlueBrainModelHelper,
            __doc__="""Provides methods for the circuit.""")
    label=\
        Field(
            __name__="label",
            __type__=str,
            __doc__="""A label for the circuit build geometry. Provide this
            is as a class-attribute.""",
            __examples__=["O1", "O1.v6a", "Atlas-based", "S1", "S1.v6a"])
    circuit_specialization=\
        Field(
            __name__="circuit_specialization",
            __type__=CircuitSpecialization,
            __doc__="""Provides circuit instance specific code.""")
    def __init__(self,
            circuit,
            *args, **kwargs):
        """..."""
        self.circuit\
            = circuit
        self.helper\
            = BlueBrainModelHelper(
                circuit=circuit)
        super().__init__(
            *args, **kwargs)

    @abstractmethod
    def random_position(self,
            condition):
        """..."""
        pass

    @abstractmethod
    def random_spanning_column(self,
            condition=Condition([]),
            crossection=50.):
        """A square faced column spanning all the sub-regions of the circuit.
        Ideally this column should be orthogonal to any layered sub-regions. As
        a first implementation we will use rectilinear colulmns."""
        raise NotImplementedError()
    
    @abstractmethod
    def spanning_column_parameter(self,
            regions=[],
            *args, **kwargs):
        """Spatial parameter representing a column that spans all the layers
        (or another sub-region) of a brain region. Unlike sub-region (layer),
        this spatial parameter Column depends on the (geometric) build of the
        circuit."""
        pass
