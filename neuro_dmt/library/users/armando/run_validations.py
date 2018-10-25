import os
import sys
import bluepy
from bluepy.v2.enums import Cell
from neuro_dmt.library.users.armando.validations.hippocampus import\
    MtypeCellDensityValidation, ByLayerCellDensityValidation,\
    BoutonDensityValidation
from neuro_dmt.library.users.armando.models.hippocampus import\
    HippocampusAdapter

circuit_path = '/gpfs/bbp.cscs.ch/project/proj42/circuits/O1/20180904/CircuitConfig'

circuit = bluepy.v2.circuit.Circuit(circuit_path)

# <<<<<<< HEAD
# =======
# sys.stdout.write(
#     "Load data from current location: {}\n".format(
#         os.path.dirname(__file__)))

# mtype_cell_density\
#     = MtypeCellDensityValidation(
#         data_path=os.path.join(
#             os.path.dirname(__file__),
#             "data", "Armando2018_by_mtype.tsv"),
#         adapter=HippocampusAdapter())
# mtype_cell_density(circuit)
# >>>>>>> d5c7b1a48308b9cfec0d46c6ff05049eb99ddcb6

def run_valid(validation):
    valid = validation(adapter=HippocampusAdapter())
    return valid(circuit)


run_valid(MtypeCellDensityValidation)
run_valid(ByLayerCellDensityValidation)
run_valid(BoutonDensityValidation)
