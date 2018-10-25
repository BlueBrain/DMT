import os
import bluepy
import neuro_dmt.library.users.armando.validations.hippocampus\
    as validations_module
# from neuro_dmt.library.users.armando.validations.hippocampus import\
#     MtypeCellDensityValidation, ByLayerCellDensityValidation,\
#     BoutonDensityValidation
from neuro_dmt.library.users.armando.models.hippocampus import\
    HippocampusAdapter
import neuro_dmt.library.users.armando as armando

armando_rootdir = os.path.dirname(armando.__file__)


validations = {n.split(".")[-1]: v
               for n, v in validations_module.__dict__.items()
               if ("Validation" in n)}

dpaths = {validations_module.MtypeCellDensityValidation:
          os.path.join(
              armando_rootdir,
              "data", "Armando2018_by_mtype.tsv")}

circs = {
    'O1_20180904':
    '/gpfs/bbp.cscs.ch/project/proj42/circuits/O1/20180904.temp/CircuitConfig',

    # 'O1_20180821':
    # '/gpfs/bbp.cscs.ch/project/proj42/circuits/O1/20180821.temp/CircuitConfig',

    # 'O1_20180821_struct':
    # '/gpfs/bbp.cscs.ch/project/proj42/circuits/'
    # 'O1/20180821/CircuitConfig_struct',

    'CA1_20180506':
    '/gpfs/bbp.cscs.ch/project/proj42/circuits/rat.CA1/20180506/CircuitConfig',

    # 'CA1_20180506_struct':
    # '/gpfs/bbp.cscs.ch/project/proj42/circuits/rat.CA1/'
    # '20180506.temp/CircuitConfig_struct',


}


def run_valid(validation, circuit):
    kwargs = {"adapter": HippocampusAdapter()}

    if validation in dpaths.keys():
        kwargs["data_path"] = dpaths[validation]
        print("using data: ", dpaths[validation])
    valid = validation(**kwargs)
    return valid(circuit)


def test():
    for name, cpath in circs.items():
        circ = bluepy.v2.circuit.Circuit(cpath)
        for n, v in validations.items():
            print('running', n, "for", name)
            run_valid(v, circ)

test()
