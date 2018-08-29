"""Specify a Blue Brain Circuit for testing."""

import os
import numpy as np
from bluepy.v2.circuit import Circuit
from neuro_dmt.tests.spec import CircuitSpec

class BlueBrainCircuitSpec(CircuitSpec):
    """Base class to specify a circuit."""

    def __init__(self, circuit_config_path, animal, brain_region,
                 brain_sub_region=None,
                 geometry=None, version=None):
        self._circuit_config_path = circuit_config_path
        self._geometry = geometry
        self._version = version
        super(BlueBrainCircuitSpec, self)\
            .__init__(Circuit(circuit_config_path), animal,
                      brain_region, brain_sub_region)
                     

    


