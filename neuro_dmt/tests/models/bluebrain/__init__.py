"""Test BlueBrainModelHelper"""

import numpy as np
from bluepy.v2.circuit import Circuit
from neuro_dmt.models.bluebrain import BlueBrainModelHelper, geometry
from neuro_dmt.models.bluebrain.measurements.circuit.composition import \
    CellDensityMeasurement, \
    CellRatioMeasurement, \
    InhibitorySynapseDensityMeasurement, \
    ExtrinsicIntrinsicSynapseDensityMeasurement


cpath = "/gpfs/bbp.cscs.ch/project/proj64/circuits/O1.v6a/20171212/CircuitConfig"
circuit = Circuit(cpath)
circuit_helper = BlueBrainModelHelper(circuit = circuit)

roi_L1 = circuit_helper.geometric_bounds({'layer': 1})
roi_L2 = circuit_helper.geometric_bounds({'layer': 2})
roi_L3 = circuit_helper.geometric_bounds({'layer': 3})
roi_L4 = circuit_helper.geometric_bounds({'layer': 4})
roi_L5 = circuit_helper.geometric_bounds({'layer': 5})
roi_L6 = circuit_helper.geometric_bounds({'layer': 6})

box_shape = np.array([50., 50., 50.])
half_box = box_shape / 2.

center_L1 = np.mean(roi_L1.bbox)
center_L2 = np.mean(roi_L2.bbox)
center_L3 = np.mean(roi_L3.bbox)
center_L4 = np.mean(roi_L4.bbox)
center_L5 = np.mean(roi_L5.bbox)
center_L6 = np.mean(roi_L6.bbox)

roi = geometry.Cuboid(center_L3 - half_box, center_L3 + half_box)

cdm = CellDensityMeasurement(circuit)
crm = CellRatioMeasurement(circuit)
isdm = InhibitorySynapseDensityMeasurement(circuit)
sdm = ExtrinsicIntrinsicSynapseDensityMeasurement(circuit)
