"""Test develop cell density validation."""
import os
from neuro_dmt.library.bluebrain.circuit.O1.cortex.sscx import composition
from dmt.vtk.plotting.comparison.crossplot import CrossPlotComparison

circuit_config_path = os.path.join("/gpfs/bbp.cscs.ch/project/proj64/circuits",
                                   "O1.v6a", "20171212", "CircuitConfig")

def run(validation_name):
    """..."""
    print("Will run validation {}".format(validation_name))
    reference_data_path =  os.path.join("/gpfs/bbp.cscs.ch/home/sood",
                                        "work/validations/dmt",
                                        "examples/datasets/cortex/sscx/rat",
                                        validation_name)
    print("Data will load from {}".format(reference_data_path))
    validation = composition.validation[validation_name](
        with_plotter=CrossPlotComparison
    )
    #cdv.plotter_type = CrossPlotComparison
    print("Loaded {}".format(validation))
    validation(reference_data_path, circuit_config_path)
