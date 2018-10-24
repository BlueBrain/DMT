import os
import sys
import time
import yaml
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dmt.model.interface import Interface
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
