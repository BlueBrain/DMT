"""Test develop cell density validation."""
import os
from neuro_dmt.library.bluebrain.circuit.O1.cortex.sscx import composition

circuit_config_path = os.path.join("/gpfs/bbp.cscs.ch/project/proj64/circuits",
                                   "O1.v6a", "20171212", "CircuitConfig")

def run(validation):
    """..."""
    reference_data_path =  os.path.join("/gpfs/bbp.cscs.ch/home/sood",
                                        "work/validations/dmt",
                                        "examples/datasets/cortex/sscx/rat",
                                        validation)
    cdv = composition.BlueBrainCellDensityValidation()
    cdv(reference_data_path, circuit_config_path)
                                                     
