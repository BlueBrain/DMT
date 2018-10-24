import numpy as np
import pandas as pd
from dmt.model import interface, adapter
from neuro_dmt.library.users.armando.validations.hippocampus import\
    MtypeCellDensityValidation
from bluepy.v2.enums import Cell
from bluepy.v2.circuit import Circuit

@adapter.adapter(Circuit)
@interface.implementation(MtypeCellDensityValidation.AdapterInterface)
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

    def get_layer_composition(self, circuit):
        atlas = circuit.atlas
        brain_regions = atlas.load_data('brain_regions')
        hierarchy = atlas.load_hierarchy()
        labels = ['CA1', 'SLM-SR', 'SP', 'PC in SP', 'SO']
        df = pd.DataFrame(index=labels, columns=np.arange(7))
        scale = 1000000

        for idx in range(7):
            mod = []
            ids1 = hierarchy.collect('acronym', 'mc'+str(idx), 'id')
            gids1 = circuit.cells.ids({Cell.REGION: '@mc'+str(idx)+'.*'})

            # Neurons in CA1
            mod.append(len(gids1) * scale / brain_regions.volume(ids1))

            # SLM-SR neurons in SLM-SR
            ids2 = hierarchy.collect('acronym', 'mc'+str(idx)+';SLM', 'id')\
                            .union(
                                hierarchy.collect(
                                    'acronym',
                                    'mc'+str(idx)+';SR',
                                    'id'))
            ids = ids1.intersection(ids2)
            gids2 = np.append(circuit.cells.ids({'$target': 'SLM'}),
                              circuit.cells.ids({'$target': 'SR'}))
            gids = np.intersect1d(gids1, gids2)
            mod.append(len(gids) * scale / brain_regions.volume(ids))

            # SP neurons in SP
            ids2 = hierarchy.collect('acronym', 'mc'+str(idx)+';SP', 'id')
            ids = ids1.intersection(ids2)
            gids2 = circuit.cells.ids({'$target': 'SP'})
            gids = np.intersect1d(gids1, gids2)
            mod.append(len(gids) * scale / brain_regions.volume(ids))

            # SP_PC in SP
            ids2 = hierarchy.collect('acronym', 'mc'+str(idx)+';SP', 'id')
            ids = ids1.intersection(ids2)
            gids2 = circuit.cells.ids({'$target': 'SP_PC'})
            gids = np.intersect1d(gids1, gids2)
            mod.append(len(gids) * scale / brain_regions.volume(ids))

            # SO neurons in SP
            ids2 = hierarchy.collect('acronym', 'mc'+str(idx)+';SO', 'id')
            ids = ids1.intersection(ids2)
            gids2 = circuit.cells.ids({'$target': 'SO'})
            gids = np.intersect1d(gids1, gids2)
            mod.append(len(gids) * scale / brain_regions.volume(ids))

            df[idx] = mod
            means = df.mean(axis=1)
            stds = df.std(axis=1)
            df['mean'] = means
            df['std'] = stds
            df['sem'] = stds / means

            return df

    def get_bouton_density(self, circuit, sample):
        """get bouton density"""
        mtypes = circuit.cells.mtypes
        data = pd.DataFrame(index=mtypes, columns=np.arange(sample)+1)
        for mtype in mtypes:
            gids = circuit.cells.ids(group={Cell.MTYPE: mtype,
                                               Cell.REGION: '@mc2.*'},
                                        limit=sample)

            data.loc[mtype][:len(gids)]\
                = circuit.stats.sample_bouton_density(
                    sample, group=gids, synapses_per_bouton=1.2)
        return data, mtypes
