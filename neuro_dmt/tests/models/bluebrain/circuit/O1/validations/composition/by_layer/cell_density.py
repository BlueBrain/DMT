"""Test develop cell density validation."""
import os
import numpy as np
from bluepy.v2.circuit import Circuit
from neuro_dmt.validations.circuit.composition.by_layer.cell_density \
    import CellDensityValidation
from neuro_dmt.models.bluebrain.circuit.O1.adapter import BlueBrainModelAdapter
from neuro_dmt.data.circuit.composition.by_layer.cell_density \
    import get_reference_datasets

data_path = os.path.join("/gpfs/bbp.cscs.ch/home/sood",
                         "work/validations/dmt",
                         "examples/datasets/cortex/sscx/rat")
validation_data \
    = get_reference_datasets(os.path.join(data_path, "cell_density"))
bb_adapter \
    = BlueBrainModelAdapter(np.array([50.0, 50.0, 50.0]), 10,
                            model_label="blue_brain_O1")


bluebrain_cell_density_validation = CellDensityValidation(validation_data,
                                                          adapter=bb_adapter)


circuit_config = os.path.join("/gpfs/bbp.cscs.ch/project/proj64/circuits",
                            "O1.v6a", "20171212", "CircuitConfig")

circuit = Circuit(circuit_config)

bluebrain_cell_density_report = bluebrain_cell_density_validation(circuit)

bluebrain_cell_density_report.save()
