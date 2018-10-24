import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from dmt.model.interface import Interface
import yaml
import seaborn

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
                     yerr=composition_concat.loc[INT_mtypes]['model_std']
                     .values)
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


class BoutonDensityValidation:

    bio_path = '/gpfs/bbp.cscs.ch/project/proj42/circuits/O1/20180219/'\
               'bioname/bouton_density_20180125.tsv'

    def __init__(self, adapter, *args, **kwargs):
        self.adapter = adapter
        return

    class AdapterInterface(Interface):

        def get_bouton_density(self, circuit, sample):
            pass

    def __call__(self, circuit):
        df, mtypes = self.adapter.get_bouton_density(circuit, 10)
        means = df.mean(axis=1)
        stds = df.std(axis=1)
        df['mean'] = means
        df['std'] = stds

        data = pd.read_csv(self.bio_path,
                           names=['mtype', 'bio_mean', 'bio_std'],
                           skiprows=2,
                           usecols=[0, 1, 2],
                           delim_whitespace=True)

        selected = data['mtype'].values
        data['mod_mean'] = means[selected].values
        data['mod_std'] = stds[selected].values

        self.plot(data, means, stds, mtypes)
        return

    def plot(self, data, means, stds, mtypes):
        plt.close('all')

        fig, axs = plt.subplots(2, 1, figsize=(8.27, 11.69))

        fig.suptitle('Bouton density', fontsize=16)

        labels = mtypes
        ind = np.arange(len(labels))
        width = 0.75
        axs[0].bar(ind, means, width, yerr=stds)
        axs[0].set_xlabel('mtype')
        axs[0].set_ylabel('density (um^-1)')
        axs[0].set_xticks(ind)
        axs[0].set_xticklabels(labels, rotation='vertical')

        x = data['mod_mean'].values
        y = data['bio_mean'].values
        l = np.linspace(0, max(x[~np.isnan(x)].max(), y.max()), 50)
        axs[1].plot(x, y, 'o')
        axs[1].errorbar(x, y,
                        xerr=data['mod_std'].values,
                        yerr=data['bio_std'].values,
                        fmt='o', ecolor='g', capthick=2)
        axs[1].plot(l, l, 'k--')
        axs[1].set_xlabel('Model (um^-1)')
        axs[1].set_ylabel('Experiment (um^-1)')

        fig.tight_layout()

        plt.subplots_adjust(hspace=0.4, top=0.92)

        filename = os.path.join("neuro_dmt", "library",
                                "users", "armando",
                                "bouton_density{}.pdf".format(time.time()))

        plt.savefig(filename)
        # plt.show()


class SynapsesPerConnectionValidation:

    bio_path = '/gpfs/bbp.cscs.ch/project/proj42/circuits/O1/20180219'\
               '/bioname/nsyn_per_connection_20180125.tsv'

    def __init__(self, adapter):
        self.adapter = adapter

    class AdapterInterface(Interface):
        pass

    def plot(df, model_mean):
        plt.close('all')
        fig, axs = plt.subplots(2, 1, figsize=(8.27, 11.69))

        fig.suptitle('synapses per connection', fontsize=16)

        seaborn.heatmap(model_mean, ax=axs[0])
        axs[0].set_xlabel('post mtype')
        axs[0].set_ylabel('pre mtype')

        x = df['mod_mean'].values
        y = df['bio_mean'].values
        l = np.linspace(0, max(x.max(), y.max()), 50)
        axs[1].plot(x, y, 'o')
        axs[1].errorbar(x, y, xerr=df['mod_std'].values,
                        yerr=df['bio_std'].values,
                        fmt='o', ecolor='g', capthick=2)
        axs[1].plot(l, l, 'k--')
        axs[1].set_xlabel('Model (#)')
        axs[1].set_ylabel('Experiment (#)')

        fig.tight_layout()

        plt.subplots_adjust(hspace=0.4, top=0.92)
        filename = os.path.join("neuro_dmt", "library",
                                "users", "armando",
                                "syns_per_conn{}.png"
                                .format(time.time()))

        plt.savefig(filename)

        plt.show()
