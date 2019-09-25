"""
A class that represents circuit models developed at the Blue Brain Project.
"""

from dmt.tk.field import Field, lazyfield, WithFields

class BlueBrainCircuitModel(WithFields):
    """
    A circuit model developed at the Blue Brain Project.
    """
    label = Field(
        """
        A label to represent your circuit model instance.
        """,
        __default_value__="BlueBrainCircuitModel")
    path_circuit_data = Field(
        """
        Path to the location of this circuit's data. This data is loaded as a
        BluePy circuit if a Bluepy circuit is not provided at initialization.
        """,
        __required__=False)
    circuit_config = Field(
        """
        Name of the file (under `.path_circuit_data`) that contains the
        circuit's configuration and provides paths to the data containing
        cells and connectome.
        """,
        __default_value__="CircuitConfig")
    circuit_config_base = Field(
        """
        After the first phase of circuit build, that creates a cell collection,
        a basic circuit config file is created in the circuit directory.
        """,
        __default_value__="CircuitConfig_base")

    def __init__(self, circuit=None, *args, **kwargs):
        """
        Initialize with a circuit.

        Arguments
        -------------
        circuit: A BluePy circuit.
        """
        if circuit is not None:
            self._bluepy_circuit = circuit

        super().__init__(*args, **kwargs)

    @lazyfield
    def bluepy_circuit(self):
        """
        An instance of the BluePy circuit object.
        """
        try:
            return BluePyCircuit(
                self.get_path(self.circuit_config))
        except FileNotFoundError:
            return BluePyCircuit(
                self.get_path(self.circuit_config_base))

