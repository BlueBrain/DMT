import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from dmt.model.interface import Interface
import yaml

dmt_path = "~/dmt"
data_path = "neuro_dmt/library/users/armando/data/Armando2018_by_mtype.tsv"
reference_data = pd.read_csv(os.path.join(dmt_path, data_path),
                             delim_whitespace=True, index_col=0, skiprows=1,
                             names=['exp_mean'])

class MtypeCellDensityValidation:

    def __init__(self, adapter, *args, **kwargs):
        self.adapter = adapter
        pass


    class AdapterInterface(Interface):

        def get_interneuron_mtypes(self, circuit):
            pass

        def get_mtype_composition(self, circuit):
            pass

    def __call__(self, circuit):
        return self.plot(self.adapter.get_mtype_composition(circuit),
                         circuit)

    def plot(self, composition, circuit):
        fig = plt.figure(figsize=(8, 6))
        ax0 = plt.subplot2grid((1, 4), (0, 0), colspan=3)
        ax1 = plt.subplot2grid((1, 4), (0, 3))
        INT_mtypes = self.adapter.get_interneuron_mtypes(circuit)
        width = 0.35

        composition_concat = pd.concat(
            [composition[['model_mean', 'model_std']], reference_data], axis=1)

        fig.suptitle('Cell composition', fontsize=16)

        s1 = ax0.bar(np.arange(len(INT_mtypes)),
                     composition_concat.loc[INT_mtypes]['model_mean'].values,
                     width,
                     yerr=composition_concat.loc[INT_mtypes]['model_std'].values)
        s2 = ax0.bar(np.arange(len(INT_mtypes)) + width,
                     composition_concat.loc[INT_mtypes]['exp_mean'].values,
                     width)
        ax0.set_title('interneurons')
        ax0.set_ylabel('Percentage (%)')
        ax0.set_xlabel('mtype')
        ax0.set_xticks(np.arange(len(INT_mtypes)) + width / 2)
        ax0.set_xticklabels(INT_mtypes, rotation='vertical')

        ax1.bar(0, composition_concat.loc['SP_PC']['model_mean'],
                width, yerr=composition_concat.loc['SP_PC']['model_std'])
        ax1.bar(0 + width, composition_concat.loc['SP_PC']['exp_mean'], width)
        ax1.set_title('pyramidal cells')
        ax1.set_ylabel('Percentage (%)')
        ax1.set_xlabel('mtype')
        ax1.set_xticks([0 + width / 2])
        ax1.set_xticklabels(['SP_PC'], rotation='vertical')

        ax0.legend((s1[0], s2[0]), ('Model', 'Experiment'))

        fig.tight_layout()

        plt.subplots_adjust(top=0.84)

        filename = os.path.join("neuro_dmt", "library",
                                "users", "armando",
                                "mtype_densities{}.png".format(time.time()))
        plt.savefig(filename)


class ByLayerCellDensityValidation:

    experimental_mean = np.array([35.2, 1.9, 272.4, 264, 11.3])
    experimental_sem = np.array([0.5, 0.3, 14.3, 14.6, 0.9])

    def __init__(self, adapter, *args, **kwargs):
        self.adapter = adapter

    class AdapterInterface(Interface):

        def get_layer_composition(self, circuit):
            pass

    def __call__(self, circuit):
        composition = self.adapter.get_layer_composition(circuit)
        self.plot(composition)

    def plot(self, composition):
        fig, ax = plt.subplots()

        labels = ['CA1', 'SLM-SR', 'SP', 'PC in SP', 'SO']
        ind = np.arange(len(labels))
        width = 0.35

        s1 = ax.bar(ind, composition['mean'],
                    width, yerr=composition['sem'].values)
        s2 = ax.bar(ind + width, self.experimental_mean, width,
                    yerr=self.experimental_sem)

        ax.set_ylabel('density (10^3/mm^3)')
        ax.set_title('Neuron density')
        ax.set_xticks(ind + width / 2)
        ax.set_xticklabels(labels)

        ax.legend((s1[0], s2[0]), ('Model', 'Experiment'))

        filename = os.path.join("neuro_dmt", "library",
                                "users", "armando",
                                "layer_densities{}.png".format(time.time()))
        plt.savefig(filename)
