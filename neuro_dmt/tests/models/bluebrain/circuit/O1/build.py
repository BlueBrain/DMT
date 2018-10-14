"""Test develop O1Circuit Build"""

import numpy as np
from bluepy.v2.circuit import Circuit
from bluepy.v2.enums import Cell
from neuro_dmt.models.bluebrain.circuit.O1.build import O1Circuit
from neuro_dmt.models.bluebrain.circuit import BlueBrainModelHelper

cpath = "/gpfs/bbp.cscs.ch/project/proj64/circuits/O1.v6a/20171212/CircuitConfig"
circuit = Circuit(cpath)

helper = BlueBrainModelHelper(circuit=circuit)
o1b = O1Circuit(circuit)


