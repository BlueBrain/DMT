"""Common code for all BBP circuits."""
from abc import ABC, abstractmethod
from bluepy.v2.circuit import Circuit

class BlueBrainModel(Circuit):
    """Base class that provides code common to all brain circuit models from
    the Blue Brain Project."""

    def __init__(self, *args, **kwargs):
        """Initialize common BBP Circuit stuff.

        Keyword Arguments
        ------------------------------------------------------------------------
        circuit :: bluepy.v2.Circuit #optional
        config :: String #path to a CircuitConfig
        """
        circuit = kwargs.get('circuit')
        if circuit is not None:
            self._circuit = circuit
        else:
            config = kwargs.get('config')
            if config is None:
                raise Exception(
                    "Provide a circuit or a path to a CircuitConfig"
                )
            self._circuit = Circuit(config)

        self.label = kwargs.get("label", "BlueBrainProjectCircuit")
