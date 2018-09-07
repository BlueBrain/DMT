"""Test develop cell density validation."""
import os
from neuro_dmt.library.bluebrain.circuit.O1.hippocampus.ca1 import composition

circuit_config_path = os.path.join("/gpfs/bbp.cscs.ch/project/proj42/circuits",
                                   "O1", "20180821", "CircuitConfig")

def run(validation_name):
    """..."""
    print("Will run validation {}".format(validation_name))
    reference_data_path =  os.path.join("/gpfs/bbp.cscs.ch/home/sood",
                                        "work/validations/dmt",
                                        "examples/datasets/hippocampus/ca1/mouse",
                                        validation_name)
    print("Data will load from {}".format(reference_data_path))
    cdv = composition.validation[validation_name]()
    print("Loaded {}".format(cdv))
    cdv(reference_data_path, circuit_config_path)
