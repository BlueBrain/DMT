import os
import sys
import time
import yaml
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dmt.model.interface import Interface

import seaborn
from dmt.vtk.plotting import golden_figure



class MtypeCellDensityValidation:

    def __init__(self,
                 data_path,
                 adapter,
                 *args, **kwargs):
        """..."""
        self.reference_data\
            = pd.read_csv(
                data_path,
                delim_whitespace=True,
                index_col=0)
        self.adapter = adapter

    class AdapterInterface(Interface):
        """Specify the method / attributes required from the model.
        The methods sketched out here will be used in this analyses.
        The model adapter must provide these methods."""

        def filter_interneuron_mtypes(self, circuit):
            """..."""
            pass

        def get_mtype_composition(self, circuit):
            """..."""
            pass

    def __call__(self, circuit):
        """...Call Me..."""
        composition = 1.e2 * self.adapter.get_mtype_composition(circuit)
        filename = self.plot(composition, circuit)
        sys.stdout.write("figure saved at {}\n".format(filename))

    def plot(self, circuit_composition, circuit):
        """..."""
        fig = golden_figure()

        ax0 = plt.subplot2grid((1, 4), (0, 0), colspan=3)
        ax1 = plt.subplot2grid((1, 4), (0, 3))
        INT_mtypes = self.adapter.filter_interneuron_mtypes(circuit_composition)
        width = 0.35

        fig.suptitle('Cell composition', fontsize=16)

        s1 = ax0.bar(
            np.arange(len(INT_mtypes)),
            circuit_composition.loc[INT_mtypes]["mean"].values,
            width,
            yerr=circuit_composition.loc[INT_mtypes]["std"].values)
        s2 = ax0.bar(
            np.arange(len(INT_mtypes)) + width,
            self.reference_data.loc[INT_mtypes]["mean"].values,
            width)

        ax0.set_title('interneurons')
        ax0.set_ylabel('Percentage (%)')
        ax0.set_xlabel('mtype')
        ax0.set_xticks(np.arange(len(INT_mtypes)) + width / 2)
        ax0.set_xticklabels(INT_mtypes, rotation='vertical')

        ax1.bar(
            0, circuit_composition.loc['SP_PC']['mean'],
            width, yerr=circuit_composition.loc['SP_PC']['std'])
        ax1.bar(
            0 + width, self.reference_data.loc['SP_PC']['mean'],
            width)
        ax1.set_title('pyramidal cells')
        ax1.set_ylabel('Percentage (%)')
        ax1.set_xlabel('mtype')
        ax1.set_xticks([0 + width / 2])
        ax1.set_xticklabels(['SP_PC'], rotation='vertical')

        ax0.legend((s1[0], s2[0]), ('Model', 'Experiment'))

        fig.tight_layout()

        plt.subplots_adjust(top=0.84)
        # TODO: this bit here is repeated often: abstract somwhere else
        # TODO: e.g. module-level variable as default for kwarg
        report_path\
            = os.path.join(
                os.path.dirname(__file__),
                "reports")

        if not os.path.exists(report_path):
            os.makedirs(report_path)
        filename\
            = os.path.join(
                report_path,
                "mtype_density_validation_{}.png".format(time.time()))
        plt.savefig(filename)
        return filename


class ByLayerCellDensityValidation:

    def __init__(self, adapter, *args, **kwargs):
        """..."""
        self.adapter = adapter
        self.reference_data\
            = pd.DataFrame(
                data={"mean": [35.2, 1.9, 272.4, 264, 11.3],
                      "sem": [0.5, 0.3, 14.3, 14.6, 0.9]},
                index=pd.Index(['CA1', 'SLM-SR', 'SP', 'PC in SP', 'SO']))

    class AdapterInterface(Interface):

        def get_layer_composition(self, circuit):
            pass

    def __call__(self, circuit):
        composition = self.adapter.get_layer_composition(circuit)
        filename = self.plot(composition)
        sys.stdout.write("figure saved at {}\n".format(filename))

    def plot(self, composition):
        fig, ax = plt.subplots()

        ind = np.arange(self.reference_data.shape[0])
        width = 0.35
        labels = self.reference_data.index
        s1 = ax.bar(ind, composition.loc[labels]['mean'],
                    width, yerr=composition.loc[labels]['std'].values)
        s2 = ax.bar(ind + width, self.reference_data["mean"], width,
                    yerr=self.reference_data["sem"])

        ax.set_ylabel('density (10^3/mm^3)')
        ax.set_title('Neuron density')
        ax.set_xticks(ind + width / 2)
        ax.set_xticklabels(labels)

        ax.legend((s1[0], s2[0]), ('Model', 'Experiment'))

        report_path\
            = os.path.join(
                os.path.dirname(__file__),
                "reports")
        if not os.path.exists(report_path):
            os.makedirs(report_path)
        filename\
            = os.path.join(
                report_path,
                "layer_density_validation_{}.png".format(time.time()))
        plt.savefig(filename)
        return filename

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
                                "bouton_density_validation{}.pdf"
                                .format(time.time()))

        plt.savefig(filename)
        # plt.show()

        return filename

class SynsPerConnValidation():
    """validate number of synapses per connection"""

    bio_path = '/gpfs/bbp.cscs.ch/project/proj42/circuits/O1/20180219/'\
               'bioname/nsyn_per_connection_20180125.tsv'

    def __init__(self, adapter):
        self.adapter = adapter
        pass

    def __call__(self, circuit):
        df = pd.read_csv(self.bio_path, skiprows=1,
                         names=['pre', 'post', 'bio_mean', 'bio_std'],
                         usecols=[0, 1, 2, 3], delim_whitespace=True)
        model_mean, model_std = self.adapter.get_syns_per_conn(circuit)
        df['model_mean'] = np.NAN
        df['model_std'] = np.NAN
        for idx in df.index:
            pre = df.loc[idx, 'pre']
            post = df.loc[idx, 'post']
            df.loc[idx, 'model_mean'] = model_mean[post][pre]
            df.loc[idx, 'model_std'] = model_std[post][pre]

        filenames = self.plot(df, model_mean, model_std)

        sys.stdout.write("figure saved at {}\n".format(filenames))

        return

    class AdapterInterface(Interface):

        def get_syns_per_conn(self, circuit):
            pass

    def plot(self, df, model_mean, model_std):

        # put both plots in A4 page
        plt.close('all')
        fig, axs = plt.subplots(2, 1, figsize=(8.27, 11.69))

        fig.suptitle('synapses per connection', fontsize=16)

        seaborn.heatmap(model_mean, ax=axs[0])
        axs[0].set_xlabel('post mtype')
        axs[0].set_ylabel('pre mtype')

        x = df['model_mean'].values
        y = df['bio_mean'].values
        l = np.linspace(0, max(x.max(), y.max()), 50)
        axs[1].plot(x, y, 'o')
        axs[1].errorbar(x, y,
                        xerr=df['model_std'].values, yerr=df['bio_std'].values,
                        fmt='o', ecolor='g', capthick=2)
        axs[1].plot(l, l, 'k--')
        axs[1].set_xlabel('Model (#)')
        axs[1].set_ylabel('Experiment (#)')

        fig.tight_layout()

        plt.subplots_adjust(hspace=0.4, top=0.92)

        report_path\
            = os.path.join(
                os.path.dirname(__file__),
                "reports")

        filename1\
            = os.path.join(
                report_path,
                "syns_per_conn_validation{}.pdf".format(time.time()))

        plt.savefig(filename1)

        def conn_class(pre, post):
            if (pre=='SP_PC')&(post=='SP_PC'):
                return 'ee'
            if (pre=='SP_PC')&(post!='SP_PC'):
                return 'ei'
            if (pre!='SP_PC')&(post=='SP_PC'):
                return 'ie'
            else:
                return 'ii'

        df['connection_class'] = [conn_class(pre, post)
                                  for pre, post in zip(df['pre'].values,
                                                       df['post'].values)]

        plt.close('')
        fig, ax = plt.subplots()

        x = df['model_mean'].values
        y = df['bio_mean'].values
        l = np.linspace(0, max(x.max(), y.max()), 50)
        ax.plot(l, l, 'k--', label='diagonal')

        x_ee = df[df['connection_class']=='ee']['model_mean'].values
        y_ee = df[df['connection_class']=='ee']['bio_mean'].values
        ax.plot(x_ee, y_ee, 'ro', label='EE')

        x_ei = df[df['connection_class']=='ei']['model_mean'].values
        y_ei = df[df['connection_class']=='ei']['bio_mean'].values
        ax.plot(x_ei, y_ei, 'go', label='EI')

        x_ie = df[df['connection_class']=='ie']['model_mean'].values
        y_ie = df[df['connection_class']=='ie']['bio_mean'].values
        ax.plot(x_ie, y_ie, 'bo', label='IE')

        x_ii = df[df['connection_class']=='ii']['model_mean'].values
        y_ii = df[df['connection_class']=='ii']['bio_mean'].values
        ax.plot(x_ii, y_ii, 'mo', label='II')

        m,b = np.polyfit(x, y, 1)
        x_fit = np.arange(0, x.max(), 1)
        y_fit = m*x_fit + b
        ax.plot(x_fit, y_fit, 'r', label='fit')

        ax.legend(loc=2)

        fig.suptitle('Number of appositions per connection')

        ax.set_xlabel('Structural circuit (#)')
        ax.set_ylabel('Bio data (#)')

        filename2\
            = os.path.join(
                report_path,
                "apps_per_conn_classes_fitting{}.pdf".format(time.time()))

        fig.savefig(filename2)
        plt.show()

        return (filename1, filename2)
