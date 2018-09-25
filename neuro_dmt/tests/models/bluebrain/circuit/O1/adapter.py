"""Test, (and develop), Blue Brain O1 circuit model adapter. """

import numpy as np
from bluepy.v2.circuit import Circuit
from neuro_dmt.measurement.parameter import CorticalLayer
from neuro_dmt.models.bluebrain.O1.adapter import BlueBrainModelAdapter

cpath = "/gpfs/bbp.cscs.ch/project/proj64/circuits/O1.v6a/20171212/CircuitConfig"
circuit = Circuit(cpath)

bbma = BlueBrainModelAdapter(np.array([50.0, 50.0, 50.0]), 10,
                             model_label="blue_brain_O1")

cd = bbma.get_cell_density(circuit, {CorticalLayer()})



