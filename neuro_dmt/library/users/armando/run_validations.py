import bluepy
from bluepy.v2.enums import Cell
from neuro_dmt.library.users.armando.validations.hippocampus import\
    MtypeCellDensityValidation, ByLayerCellDensityValidation
from neuro_dmt.library.users.armando.models.hippocampus import\
    HippocampusAdapter

circuit_path = '/gpfs/bbp.cscs.ch/project/proj42/circuits/O1/20180904/CircuitConfig'

circuit = bluepy.v2.circuit.Circuit(circuit_path)

mtype_cell_density = MtypeCellDensityValidation(adapter=HippocampusAdapter())
mtype_cell_density(circuit)

layer_cell_density = ByLayerCellDensityValidation(adapter=HippocampusAdapter())
layer_cell_density(circuit)
