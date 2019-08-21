"""
Brain circuit models from the Blue Brain project
"""

import os
from pathlib import Path
from bluepy.v2.circuit import Circuit
from dmt.tk.field import Field, lazyfield, WithFields

class BlueBrainCircuitModel(WithFields):
    """
    A wrapper around bluepy circuit.
    """
    label = Field(
        """
        A label for this circuit instance.
        """,
        __default_value__="BlueBrainCircuitModel")
    circuit_config = Field(
        """
        Path to the circuit's config file.
        """)
    animal = Field(
        """
        Animal species whose brain region was modeled.
        """,
        __default_value__="NA")
    brain_region = Field(
        """
        Name of the brain region that was modeled.
        """,
        __default_value__="NA")

    @lazyfield
    def uri(self):
        """
        Universal Resource Identifier.
        Where can we find this circuit?
        """
        return Path(self.circuit_config).parent

    @lazyfield
    def bluepy_circuit(self):
        """
        The circuit, as BluePy sees it.
        """
        return Circuit(self.circuit_config)
    @lazyproperty
    def cell(self):
        """
        
        """
