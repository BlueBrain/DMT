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

# TODO change to nose/unittest based tests
## test class for each validation, test method for each circuit
print(os.getcwd())

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
    '/gpfs/bbp.cscs.ch/project/proj42/circuits/O1/20180904/CircuitConfig',

    'O1_20180904_struct':
    '/gpfs/bbp.cscs.ch/project/proj42/circuits/O1/20180904/'
    'CircuitConfig_struct',

    # 'O1_20180821':
    # '/gpfs/bbp.cscs.ch/project/proj42/circuits/O1/20180821/CircuitConfig',

    # 'O1_20180821_struct':
    # '/gpfs/bbp.cscs.ch/project/proj42/circuits/'
    # 'O1/20180821/CircuitConfig_struct',

    # 'CA1_20180506':
    # '/gpfs/bbp.cscs.ch/project/proj42/circuits/rat.CA1/20180506/CircuitConfig',

    # 'CA1_20180506_struct':
    # '/gpfs/bbp.cscs.ch/project/proj42/circuits/rat.CA1/'
    # '20180506/CircuitConfig_struct',


}


def run_valid(validation, circuit):
    kwargs = {"adapter": HippocampusAdapter()}
    circuit = bluepy.v2.circuit.Circuit(circuit)
    if validation in dpaths.keys():
        kwargs["data_path"] = dpaths[validation]
        print("using data: ", dpaths[validation])
    valid = validation(**kwargs)
    return valid(circuit)


def test():
    for n, v in validations.items():
        for name, cpath in circs.items():

            print('------------',
                  '\nrunning:', n, "for", name)
            run_valid(v, cpath)
            print('------------\n\n')


test()
