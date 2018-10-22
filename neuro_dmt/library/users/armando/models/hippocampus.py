import pandas as pd
from dmt.model import interface, adapter
from neuro_dmt.library.users.armando.validations.hippocampus import\
    CellDensityValidation
from bluepy.v2.enums import Cell
from bluepy.v2.circuit import Circuit

@adapter.adapter(Circuit)
@interface.implementation(CellDensityValidation.AdapterInterface)
class HippocampusAdapter:

    def __init__(self, *args, **kwargs):
        pass

    def get_interneuron_mtypes(self, circuit):
        mtypes = set(circuit.cells.mtypes)
        mtypes.remove('SP_PC')  # (sic)
        return mtypes

    def get_mtype_composition(self, circuit):
        mtypes = circuit.cells.mtypes
        # targets = ['mc'+str(idx)+'_Column' for idx in range(7)]
        targets = ['mc'+str(idx) for idx in range(7)]
        # targets = ['cylinder', 'cylinder1', 'cylinder2']
        composition = pd.DataFrame(index=mtypes, columns=targets)
        for target in targets:
            for mtype in mtypes:
                composition[target][mtype]\
                    = len(circuit.cells.ids(
                        group={Cell.MTYPE: mtype, Cell.REGION: '@'+target+'.*'}))

        for target in targets:
            composition[target]\
                = composition[target]*100 / composition[target].sum()
        means = composition.mean(axis=1)
        stds = composition.std(axis=1)
        composition['model_mean'] = means
        composition['model_std'] = stds
        return composition
