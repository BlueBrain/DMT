import os
import sys
import time
import yaml
import pandas as pd
import numpy as np
import scipy
import matplotlib.pyplot as plt
from matplotlib.colors import SymLogNorm
from bluepy.v2.enums import Synapse, Cell
from PyPDF2 import PdfFileMerger, PdfFileReader
import seaborn

from dmt.vtk.plotting import golden_figure
from dmt.model.interface import Interface
from dmt.analysis.comparison import Comparison
from dmt.analysis.comparison.validation.test_case import ValidationTestCase
from dmt.analysis import OfSinglePhenomenon
from dmt.data import ReferenceData
from dmt.vtk.utils.collections import Record
from dmt.vtk.phenomenon import Phenomenon
from dmt.vtk.judgment.verdict import Verdict

from neuro_dmt.analysis.circuit import BrainCircuitAnalysis
from neuro_dmt.analysis.comparison.validation.report.single_phenomenon\
    import ValidationReport


class Validation(
        ValidationTestCase,
        Comparison,
        OfSinglePhenomenon,
        BrainCircuitAnalysis):
    """a mixin of these four"""
    def get_report(self,
                   model_measurement):
        """Create a report."""
        figure = self.plot(model_measurement)
        pval = self.pvalue(model_measurement)
        verdict = self.get_verdict(pval)
        return ValidationReport(
            phenomenon=self.phenomenon,
            author=self.author,
            caption=self.get_caption(model_measurement),
            reference_datasets=dict(armando=Record(uri="somwhere", label="armando", citation="???", what="what?")),
            is_pass=verdict == Verdict.PASS,
            is_fail=verdict == Verdict.FAIL,
            pvalue=pval,
            figure=figure)


output_dir_path=os.path.join(
    os.path.expanduser("~"),
    "reports")


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


class ByLayerCellDensityValidation(Validation):

    def __init__(self, adapter, *args, **kwargs):
        """..."""
        self.reference_data\
            = ReferenceData(
                data=pd.DataFrame(
                    data={"mean": [35.2, 1.9, 272.4, 264, 11.3],
                          "sem": [0.5, 0.3, 14.3, 14.6, 0.9]},
                    index=pd.Index(['CA1', 'SLM-SR', 'SP', 'PC in SP', 'SO'])),
                description="Armando's hippocampus CA1 cell densities",
                uri="somwhere")
        super().__init__(
            phenomenon=Phenomenon("cell_density", description="cell density"),
            animal="rat",
            output_dir_path=output_dir_path,
            adapter=adapter,
            *args, **kwargs)

    class AdapterInterface(Interface):

        def get_cell_density(self, circuit, region, layers, cell_type):
            pass

        def circuit_regions(self, circuit):
            pass

    def get_label(self):
        return "cell density"

    def get_measurement(self, circuit):

        def get_layer_composition(circuit):
            """..."""
            layer_labels = ['CA1', 'SLM-SR', 'SP', 'PC in SP', 'SO']
            scale = 1.e6

            def __get_cell_density_array(
                    layers=[],
                    cell_type={}):
                """..."""
                return np.array([
                    self.adapter.get_cell_density(
                        circuit,
                        region,
                        layers=layers,
                        cell_type=cell_type)
                    for region in self.adapter.circuit_regions(circuit)])

            cell_densities\
                = pd.DataFrame(
                    data={"cell_density": np.concatenate([
                        __get_cell_density_array(),
                        __get_cell_density_array(
                            layers=["SLM", "SR"]),
                        __get_cell_density_array(
                            layers=["SP"]),
                        __get_cell_density_array(
                            layers=["SP"],
                            cell_type={Cell.MORPH_CLASS: "PYR"}),
                        __get_cell_density_array(
                            layers=["SO"])])},
                    index=pd.MultiIndex.from_tuples(
                        [(region, layer_label)
                         for layer_label in layer_labels
                         for region in self.adapter.circuit_regions(circuit)],
                        names=["column", "region"]))

            return cell_densities.groupby("region")\
                                 .agg(["mean", "std"])["cell_density"]
        composition = get_layer_composition(circuit)
        return Record(data=composition,
                      label="in-silico cell density",
                      method="armando's by-layer and cell type densities")




    def plot(self, composition):
        composition = composition.data
        fig, ax = plt.subplots()

        ind = np.arange(self.reference_data.data.shape[0])
        width = 0.35
        labels = self.reference_data.data.index
        s1 = ax.bar(ind, composition.loc[labels]['mean'],
                    width, yerr=composition.loc[labels]['std'].values)
        s2 = ax.bar(ind + width, self.reference_data.data["mean"], width,
                    yerr=self.reference_data.data["sem"])

        ax.set_ylabel('density (10^3/mm^3)')
        ax.set_title('Neuron density')
        ax.set_xticks(ind + width / 2)
        ax.set_xticklabels(labels)

        ax.legend((s1[0], s2[0]), ('Model', 'Experiment'))

        return fig


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

        print(self.plot(data, means, stds, mtypes))
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


class SynsPerConnValidation(Validation):
    """validate number of synapses per connection"""

    bio_path = '/gpfs/bbp.cscs.ch/project/proj42/circuits/O1/20180219/'\
               'bioname/nsyn_per_connection_20180125.tsv'

    def __init__(self, adapter):
        super().__init__(adapter=adapter,
                         reference_data=ReferenceData(
                             data=pd.read_csv(
                                 self.bio_path, skiprows=1,
                                 names=['pre', 'post', 'bio_mean', 'bio_std'],
                                 usecols=[0, 1, 2, 3], delim_whitespace=True)),
                         phenomenon=Phenomenon(
                             'synapses per connection',
                             'the number of synapses for'
                             'each connection between cells'),
                         animal='rat',
                         output_dir_path=output_dir_path)
        # NOTE: is 'animal' really a property of a validation?
        # NOTE: it strikes me as a property of the model and data
        # I guess it is uniform for any validation, just not
        # necessarily for any comparison

    def get_label(self):
        # we can make this general practice?
        return self.__doc__

    # NOTE: this whole 'primary dataset' thing is both limiting and complicating
    # NOTE: is phenomenon really necessary?
    # NOTE: I think I've done this inelegantly
    def get_measurement(self, circuit):
        df = self.reference_data.data
        pre_mtypes = []
        post_mtypes = []
        model_mean = []
        model_std = []
        bio_mean = []
        bio_std = []
        mtypes = self.adapter.get_mtypes(circuit)
        for pre in mtypes:
            for post in mtypes:
                nsyns_conn = self.adapter.get_syns_per_conn(
                    circuit,
                    {Cell.REGION: "@mc2.*", Cell.MTYPE: pre},
                    {Cell.MTYPE: post})

                model_mean.append(np.mean(nsyns_conn))
                model_std.append(np.std(nsyns_conn))
                mask = np.logical_and(df['pre'] == pre, df['post'] == post)
                if np.any(mask):
                    bm = df[mask]['bio_mean'].values[0]
                    bs = df[mask]['bio_std'].values[0]
                else:
                    bm = np.nan
                    bs = np.nan
                bio_mean.append(bm)
                bio_std.append(bs)
                pre_mtypes.append(pre)
                post_mtypes.append(post)

        newdf = pd.DataFrame(
            {'pre_mtype': pre_mtypes, 'post_mtype': post_mtypes,
             'model_mean': model_mean, 'model_std': model_std,
             'bio_mean': bio_mean, 'bio_std': bio_std})
        # what does method represent?
        return Record(data=newdf,
                      label='model',
                      method='???')

    class AdapterInterface(Interface):

        def get_syns_per_conn(self, pre_query, post_query):
            pass

    def plot(self, data_record):
        """
        makes a heatplot out of model mean
        and a crossplot of model mean/std and data mean/stdev
        """
        df = data_record.data
        # put both plots in A4 page
        plt.close('all')
        fig, axs = plt.subplots(2, 1, figsize=(8.27, 11.69))

        fig.suptitle('synapses per connection', fontsize=16)

        seaborn.heatmap(df.pivot(index='pre_mtype',
                                 columns='post_mtype')['model_mean'],
                        ax=axs[0])
        axs[0].set_xlabel('post mtype')
        axs[0].set_ylabel('pre mtype')

        x = df['model_mean'].values
        y = df['bio_mean'].values

        xerr = df['model_std'].values
        yerr = df['bio_std'].values

        axs[1].plot(x, y, 'o')
        axs[1].errorbar(x, y,
                        xerr=xerr, yerr=yerr,
                        fmt='o', ecolor='g', capthick=2)
        maximum = max(max(x + xerr), max(y + yerr))
        axs[1].plot((0, maximum), (0, maximum), 'k--')
        axs[1].set_xlabel('Model (#)')
        axs[1].set_ylabel('Experiment (#)')

        fig.tight_layout()

        plt.subplots_adjust(hspace=0.4, top=0.92)
        return fig
        # report_path\
        #     = os.path.join(
        #         os.path.dirname(__file__),
        #         "reports")

        # filename1\
        #     = os.path.join(
        #         report_path,
        #         "syns_per_conn_validation{}.pdf".format(time.time()))
# class ByCclassSynsPerConnValidation(Validation):

#     def __init__(self, adapter):
#         super().__init__(adapter=adapter,
#                         reference_data=ReferenceData(
#                             data=pd.read_csv(
#                                 self.bio_path, skiprows=1,
#                                 names=['pre', 'post', 'bio_mean', 'bio_std'],
#                                 usecols=[0, 1, 2, 3], delim_whitespace=True)),
#                         phenomenon=Phenomenon(
#                             'synapses per connection',
#                             'the number of synapses for'
#                             'each connection between cells'),
#                          animal='rat',
#                          output_dir_path=output_dir_path)

#     def get_measurement(self, circuit):
#         """..."""
#         # we should only compare to the ref. data mtypes
#         pre_mtypes = self.reference_data.data['pre']
#         post_mtypes = self.reference_data.data['post']

#         pre_sclasses = {'INH': set(pre_mtypes) - set('SP_PC'),
#                         'EXC': 'SP_PC'}
#         post_sclasses = {'INH': set(post_mtypes) - set('SP_PC'),
#                          'EXC': 'SP_PC'}

#         conn_classes = []
#         model_means = []
#         model_stds = []
#         data_means = []
#         data_stds = []
#         for pre_sclass, pre_mtypes in pre_sclasses.items():
#             for post_sclass, post_mtypes in post_sclasses.items():
#                 conn_classes.append((pre_sclass[0] + post_sclass[0])
#                                     .lower())
#                 nsyns_conn = self.adapter.get_syns_per_conn(
#                     circuit,
#                     # NOTE: why restrict to mc2?
#                     {Cell.MTYPE: pre_mtypes, Cell.REGION: "@mc2.*"},
#                     {Cell.MTYPE: post_mtypes})
#                 model_means.append(np.mean(nsyns_conn))
#                 model_stds.append(np.std(nsyns_conn))
#                 datapoints

        # def conn_class(pre, post):
        #     if (pre=='SP_PC')&(post=='SP_PC'):
        #         return 'ee'
        #     if (pre=='SP_PC')&(post!='SP_PC'):
        #         return 'ei'
        #     if (pre!='SP_PC')&(post=='SP_PC'):
        #         return 'ie'
        #     else:
        #         return 'ii'

        # df['connection_class'] = [conn_class(pre, post)
        #                           for pre, post in zip(df['pre'].values,
        #                                                df['post'].values)]

        # plt.close('')
        # fig, ax = plt.subplots()

        # x = df['model_mean'].values
        # y = df['bio_mean'].values
        # l = np.linspace(0, max(x.max(), y.max()), 50)
        # ax.plot(l, l, 'k--', label='diagonal')

        # x_ee = df[df['connection_class']=='ee']['model_mean'].values
        # y_ee = df[df['connection_class']=='ee']['bio_mean'].values
        # ax.plot(x_ee, y_ee, 'ro', label='EE')

        # x_ei = df[df['connection_class']=='ei']['model_mean'].values
        # y_ei = df[df['connection_class']=='ei']['bio_mean'].values
        # ax.plot(x_ei, y_ei, 'go', label='EI')

        # x_ie = df[df['connection_class']=='ie']['model_mean'].values
        # y_ie = df[df['connection_class']=='ie']['bio_mean'].values
        # ax.plot(x_ie, y_ie, 'bo', label='IE')

        # x_ii = df[df['connection_class']=='ii']['model_mean'].values
        # y_ii = df[df['connection_class']=='ii']['bio_mean'].values
        # ax.plot(x_ii, y_ii, 'mo', label='II')

        # m,b = np.polyfit(x, y, 1)
        # x_fit = np.arange(0, x.max(), 1)
        # y_fit = m*x_fit + b
        # ax.plot(x_fit, y_fit, 'r', label='fit')

        # ax.legend(loc=2)

        # fig.suptitle('Number of appositions per connection')

        # ax.set_xlabel('Structural circuit (#)')
        # ax.set_ylabel('Bio data (#)')

        # filename2\
        #     = os.path.join(
        #         report_path,
        #         "apps_per_conn_classes_fitting{}.pdf".format(time.time()))

        # fig.savefig(filename2)

        # return (filename1, filename2)


class DivergenceValidation0:

    conn_exp_data_path = '/gpfs/bbp.cscs.ch/project/proj42/circuits/O1'\
                         '/20180219/bioname/connections.txt'

    exp_data_path = '/gpfs/bbp.cscs.ch/project/proj42/circuits/O1/'\
                    '20180219/bioname/divergence.txt'

    def __init__(self, adapter):
        self.adapter = adapter

    class AdapterInterface(Interface):

        def get_number_connections(self, circuit):
            pass

        def get_conn_to_PC_INT(self, means, mtypes):
            pass

    def __call__(self, circuit):

        self.report_path\
            = os.path.join(
                os.path.dirname(__file__),
                "reports")

        means, stds, mtypes = self.adapter.get_number_connections(circuit)
        print(self.heatmap(means, stds))
        # TODO should this really be in adappter?
        connections = self.adapter.get_conn_to_PC_INT(means, mtypes)

        conn_exp_data = pd.read_csv(self.conn_exp_data_path,
                                    delim_whitespace=True,
                                    index_col=0, skiprows=1,
                                    names=['exp_PC', 'exp_INT', 'exp_UN'])
        conn_result = pd.concat([connections, conn_exp_data], axis=1)
        indices = ['AA', 'BP', 'BS', 'CCKBC', 'Ivy', 'OLM',
                   'PC', 'PPA', 'PVBC', 'SCA']
        conn_result2 = conn_result.loc[indices]
        print(self.stacked(conn_result2))
        # TODO conn_result2 gets modified more later
        # TODO result2
        conn_result2['model_tot'] = conn_result2['model_PC']\
                                    + conn_result2['model_INT']
        conn_result2['exp_tot'] = conn_result2['exp_PC']\
                                  + conn_result2['exp_INT']\
                                  + conn_result2['exp_UN']
        print(self.comparison_bars(conn_result2))
        div_pc = means.SP_PC / means.sum(axis=1)
        div_int = (means.sum(axis=1) - means.SP_PC) / means.sum(axis=1)
        divergence = pd.DataFrame(index=mtypes)
        divergence['model_PC'] = div_pc.values
        divergence['model_INT'] = div_int.values
        divergence['model_UN'] = 0.0
        divergence.loc['S_BS'] = divergence.loc[['SP_BS', 'SO_BS']].mean()
        divergence.drop(['SP_BS', 'SO_BS'], inplace=True)

        exp_data = pd.read_csv(self.exp_data_path, delim_whitespace=True,
                               index_col=0, skiprows=1,
                               names=['exp_PC', 'exp_INT', 'exp_UN'])
        result = pd.concat([divergence, exp_data], axis=1)
        indices = ['AA', 'BP', 'BS', 'CCKBC', 'Ivy',
                   'OLM', 'PC', 'PPA', 'PVBC', 'SCA']
        result2 = result.loc[indices]
        print(self.percentage_bars(result2))

    def heatmap(self, means, stds):
        fig, ax = plt.subplots()

        # for heatmap with logarithmic scale
        seaborn.heatmap(means, norm=SymLogNorm(linthresh=0.1), ax=ax)

        fig.suptitle('Average number of connections')
        ax.set_xlabel('Postsynaptic mtype')
        ax.set_ylabel('Presynaptic mtype')

        filename0\
            = os.path.join(
                self.report_path,
                "number_connections{}.pdf".format(time.time()))

        plt.savefig(filename0, bbox_inches='tight')
        plt.close('all')
        return filename0

    def stacked(self, conn_result2):
        fig, axs = plt.subplots(2, 1, figsize=(8.27, 11.69))

        fig.suptitle('Divergence', fontsize=16)

        axs[0].set_title('Model')
        conn_result2.loc[:, ['model_PC', 'model_INT']]\
                    .plot(kind='bar', stacked=True, legend=False, ax=axs[0])
        axs[0].legend(['PC', 'INT'], loc='lower right', frameon=True)
        axs[0].set_xlabel('mtype')
        axs[0].set_ylabel('Number of synapses')

        axs[1].set_title('Experiment')
        conn_result2.loc[:, ['exp_PC', 'exp_INT', 'exp_UN']]\
                    .plot(kind='bar', stacked=True, legend=False, ax=axs[1])
        axs[1].legend(['PC', 'INT', 'UN'], loc='lower right', frameon=True)
        axs[1].set_xlabel('mtype')
        axs[1].set_ylabel('Number of synapses')

        fig.tight_layout()

        plt.subplots_adjust(hspace=0.4, top=0.92)

        filename1\
            = os.path.join(
                self.report_path,
                "divergence_absolute{}.pdf".format(time.time()))
        plt.savefig(filename1)

        plt.close('all')
        return filename1

    def comparison_bars(self, conn_result2):

        fig, axs = plt.subplots(3, 1, figsize=(8.27, 11.69))

        fig.suptitle('Number of efferent synapses', fontsize=16)

        axs[0].set_title('Total number of efferent synapses')
        conn_result2.loc[:, ['model_tot', 'exp_tot']]\
                    .plot(kind='bar', stacked=False, legend=False, ax=axs[0])
        axs[0].legend(['Model', 'Experiment'], loc='upper left', frameon=True)
        axs[0].set_xlabel('mtype')
        axs[0].set_ylabel('Number of synapses')

        axs[1].set_title('Number of synapses to PCs')
        conn_result2.loc[:, ['model_PC', 'exp_PC']]\
                    .plot(kind='bar', stacked=False, legend=False, ax=axs[1])

        axs[1].set_xlabel('mtype')
        axs[1].set_ylabel('Number of synapses')

        axs[2].set_title('Number of synapses to INTs')
        conn_result2.loc[:, ['model_INT', 'exp_INT']]\
                    .plot(kind='bar', stacked=False, legend=False, ax=axs[2])

        axs[2].set_xlabel('mtype')
        axs[2].set_ylabel('Number of synapses')

        fig.tight_layout()

        plt.subplots_adjust(hspace=0.6, top=0.92)

        filename2\
            = os.path.join(
                self.report_path,
                "n_efferent_synapses{}.pdf".format(time.time()))

        plt.savefig(filename2)

        plt.close('all')
        return filename2

    def percentage_bars(self, result2):
        fig, axs = plt.subplots(2, 1, figsize=(8.27, 11.69))

        fig.suptitle('Divergence', fontsize=16)

        axs[0].set_title('Model')
        result2.loc[:, ['model_PC', 'model_INT']]\
               .plot(kind='bar', stacked=True, legend=False, ax=axs[0])
        axs[0].legend(['PC', 'INT'], loc='lower right', frameon=True)
        axs[0].set_xlabel('mtype')
        axs[0].set_ylabel('Percentage (%)')

        axs[1].set_title('Experiment')
        result2.loc[:, ['exp_PC', 'exp_INT', 'exp_UN']]\
               .plot(kind='bar', stacked=True, legend=False, ax=axs[1])
        axs[1].legend(['PC', 'INT', 'UN'], loc='lower right', frameon=True)
        axs[1].set_xlabel('mtype')
        axs[1].set_ylabel('Percentage (%)')

        fig.tight_layout()

        plt.subplots_adjust(hspace=0.4, top=0.92)

        filename3\
            = os.path.join(
                self.report_path,
                "divergence_percent{}.pdf".format(time.time()))

        plt.savefig(filename3)

        return filename3


class ConvergenceValidation:

    def __init__(self, adapter):
        self.adapter = adapter

    class AdapterInterface(Interface):

        def get_n_eff_syns(self, circuit):
            pass

    def __call__(self, circuit):
        connections = self.adapter.get_n_eff_syns(circuit)
        print(self.plot(connections))
        return

    def plot(self, connections):
        """..."""
        fig, ax = plt.subplots()

        fig.suptitle('Number of afferent synapses', fontsize=16)

        connections.loc[:, ['model_PC', 'model_INT']]\
                   .plot(kind='bar', stacked=True, legend=False, ax=ax)
        ax.legend(['PC', 'INT'], loc='upper left', frameon=True)
        ax.set_xlabel('mtype')
        ax.set_ylabel('Number of synapses')

        fig.tight_layout()

        plt.subplots_adjust(hspace=0.6, top=0.92)

        report_path\
            = os.path.join(
                os.path.dirname(__file__),
                "reports")

        filename\
            = os.path.join(
                report_path,
                "n_afferent_synapses{}.pdf".format(time.time()))

        plt.savefig(filename)

        return filename


# TODO get working, Synapse.PRE_MTYPE doesn't exist?
class LaminarDistributionSynapsesValidation:

    exp_data_path = '/gpfs/bbp.cscs.ch/project/proj42/circuits/O1/'\
                    '20180219/bioname/laminar_distribution.txt'

    def __init__(self, adapter):
        self.adapter = adapter

    class AdapterInterface(Interface):

        def get_laminar_distribution(self, circuit):
            pass

    def __call__(self, circuit):

        exp_data = pd.read_csv(self.exp_data_path, delim_whitespace=True,
                               index_col=0, skiprows=1,
                               names=['SO', 'SP', 'SR', 'SLM'])
        result2 = self.adapter.get_laminar_distribution(circuit)
        concatenated = pd.concat([result2, exp_data], axis=1,
                                 keys=['model', 'experiment'])
        indices = ['AA', 'BP', 'BS', 'CCKBC',
                   'Ivy', 'OLM', 'PC', 'PPA', 'SCA', 'Tri']
        concatenated2 = concatenated.loc[indices]
        self.plot(concatenated2)
        pass

    def plot(self, concatenated2):
        plt.close('all')
        fig, axs = plt.subplots(2, 1, figsize=(8.27, 11.69))

        fig.suptitle('Laminar distribution of synapses', fontsize=16)

        axs[0].set_title('Model')
        concatenated2['model'].plot(kind='bar', stacked=True,
                                    sort_columns=True, legend=False,
                                    ax=axs[0])
        handles, labels = axs[0].get_legend_handles_labels()
        axs[0].legend(handles[::-1], labels[::-1],
                      loc='center left', frameon=True)
        axs[0].set_xlabel('mtype')
        axs[0].set_ylabel('%')

        axs[1].set_title('Experiment')
        concatenated2['experiment'].plot(kind='bar', stacked=True,
                                         sort_columns=True,
                                         legend='reverse',
                                         ax=axs[1])
        handles, labels = axs[1].get_legend_handles_labels()
        axs[1].legend(handles[::-1], labels[::-1],
                      loc='center left', frameon=True)
        axs[1].set_xlabel('mtype')
        axs[1].set_ylabel('%')

        fig.tight_layout()

        plt.subplots_adjust(hspace=0.4, top=0.92)
        report_path\
            = os.path.join(
                os.path.dirname(__file__),
                "reports")

        if not os.path.exists(report_path):
            os.makedirs(report_path)
        filename\
            = os.path.join(
                report_path,
                "laminar_distribution{}.png".format(time.time()))

        plt.savefig(filename)

        plt.show()
        return filename


class SynsConnDistributionValidation:

    def __init__(self, adapter):
        self.adapter = adapter

    class AdapterInterface(Interface):

        def get_syns_conn_dist(self, circuit, pre, post):
            pass

        def get_mtypes():
            pass

    def __call__(self, circuit):

        mtypes = list(self.adapter.get_mtypes(circuit))
        max_nsample = 100
        filenames = []
        for pre in mtypes:
            for post in mtypes:
                print(pre, post)
                nsample, nsyns_conn, table\
                    = self.adapter.get_syns_conn_dist(
                        circuit, pre, post, max_nsample)
                filenames.append(self.plot(pre, post, table,
                                           nsyns_conn, max_nsample))
        merger = PdfFileMerger()
        for filename in filenames:
            print(filename)
            merger.append(PdfFileReader(filename))
        report_path\
            = os.path.join(
                os.path.dirname(__file__),
                "reports")

        merger.write(os.path.join(report_path,
                                  "nsyn_conn_dist{}.pdf"
                                  .format(time.time())))
        return

    def plot(self, pre, post, table, nsyns_conn,
             nsample):
        plt.close('all')
        fig, ax = plt.subplots(3, 2, figsize=(8.27, 11.69))

        plt.figtext(0.1, 0.95, pre + '->' + post,
                    fontsize=20, fontweight='bold')
        plt.figtext(0.1, 0.9, 'sample size = ' + str(nsample),
                    fontsize=14)

        post_bo = table[Synapse.POST_BRANCH_ORDER].values
        post_path = table[Synapse.POST_NEURITE_DISTANCE].values
        pre_bo = table[Synapse.PRE_BRANCH_ORDER].values
        pre_path = table[Synapse.PRE_NEURITE_DISTANCE].values

        fig.delaxes(ax[0, 0])
        ax[0, 1].hist(nsyns_conn)
        ax[0, 1].set_title('number of syns per conn')
        ax[0, 1].set_xlabel('#')
        ax[0, 1].set_ylabel('#')
        ax[1, 0].hist(post_bo)
        ax[1, 0].set_title('postsynaptic branch order')
        ax[1, 0].set_xlabel('#')
        ax[1, 0].set_ylabel('#')
        ax[1, 1].hist(post_path)
        ax[1, 1].set_title('postsynaptic path length')
        ax[1, 1].set_xlabel('um')
        ax[1, 1].set_ylabel('#')
        ax[2, 0].hist(pre_bo)
        ax[2, 0].set_title('presynaptic branch order')
        ax[2, 0].set_xlabel('#')
        ax[2, 0].set_ylabel('#')
        ax[2, 1].hist(pre_path)
        ax[2, 1].set_title('presynaptic path length')
        ax[2, 1].set_xlabel('um')
        ax[2, 1].set_ylabel('#')

        fig.tight_layout()

        report_path\
            = os.path.join(
                os.path.dirname(__file__),
                "reports")

        tmp = os.path.join(report_path, 'tmp')
        if not os.path.exists(tmp):
            os.makedirs(tmp)

        filename\
            = os.path.join(
                tmp,
                "{}-{}_scdistr.pdf".format(pre, post))

        fig.savefig(filename)
        print(filename)
        return filename


class PCPCConnProbValidation:

    def __init__(self, adapter):
        self.adapter = adapter

    class AdapterInterface:

        def connection_probability(circuit,
                                   pre_mtype, post_mtype,
                                   distance, nsample):
            pass

    def __call__(self, circuit):
        distance = 450  # um
        nsample = 1000
        target_probability = 11.0/989
        pre_mtype = 'SP_PC'
        post_mtype = pre_mtype

        nrepetitions = 10
        model_probability = np.zeros(nrepetitions)

        for idx in range(nrepetitions):
            model_probability[idx]\
                = self.adapter.connection_probability(circuit,
                                                      pre_mtype,
                                                      post_mtype,
                                                      distance, nsample)
        print(self.plot_conn_prob(model_probability, target_probability))
        binsize = 100
        nbins = 10
        dists = [(idx+1)*binsize for idx in range(nbins)]
        post_mtype = "Inhibitory"
        model_probability = [
            self.adapter.connection_probability(circuit,
                                                pre_mtype, post_mtype,
                                                dists[idx], nsample)
            for idx in range(nbins)]
        print(self.plot_conn_prob_vs_distance(dists, model_probability,
                                        pre_mtype, post_mtype))

    def plot_conn_prob(self, model_probability, target_probability):
        fig, ax = plt.subplots()
        ind = 1
        width = 0.75
        ax.bar(ind, model_probability.mean(), width,
               yerr=model_probability.std(), label='model')
        ax.bar(ind+width, target_probability, width, yerr=0,
               label='experiment')
        fig.suptitle('Connection probability')
        plt.tick_params(
            axis='x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom='off',      # ticks along the bottom edge are off
            top='off',         # ticks along the top edge are off
            labelbottom='off')
        ax.set_ylabel('Probability')
        plt.legend(loc='upper right')
        timestamp = str(time.time())
        filename = os.path.join(os.path.dirname(__file__), "reports")\
                   + '/connection_probability_PC-PC_'\
                   + timestamp + '.png'
        fig.savefig(filename)
        return filename

    def plot_conn_prob_vs_distance(self, dists, model_probability,
                                   pre_mtype, post_mtype):
        fig, ax = plt.subplots()
        width = 90

        ax.bar(dists, model_probability, width, label='model')
        title = pre_mtype + '->' + post_mtype + ' connection probability'
        fig.suptitle(title)
        ax.set_xlabel('Distance (um)')
        ax.set_ylabel('Probability')
        plt.legend(loc='upper right')
        timestamp = str(time.time())
        filename = os.path.join(os.path.dirname(__file__), "reports")\
                   + '/connection_probability_'\
                   + timestamp + '.png'
        fig.savefig(filename)
        return(filename)


class DivergenceValidation(Validation):

    bio_connections_path = '/gpfs/bbp.cscs.ch/project/proj42/circuits/O1'\
                         '/20180219/bioname/connections.txt'

    bio_divergence_path = '/gpfs/bbp.cscs.ch/project/proj42/circuits/O1/'\
                          '20180219/bioname/divergence.txt'

    def __init__(self, adapter, syn_or_conn='conn'):
        self.syn_or_conn = syn_or_conn
        super().__init__(
            adapter=adapter,
            reference_data=[
                ReferenceData(
                    data=pd.read_csv(self.bio_connections_path,
                                     delim_whitespace=True,
                                     index_col=0, skiprows=1,
                                     names=['exp_PC', 'exp_INT', 'exp_UN'])
                    label="connections from cell by Sclass"),
                ReferenceData(
                    data=pd.read_csv(self.exp_data_path, delim_whitespace=True,
                               index_col=0, skiprows=1,
                               names=['exp_PC', 'exp_INT', 'exp_UN'])
                    label="proportions of connections from EXC vs INH neurons")])

    def get_measurement(self, circuit):
        mtypes = circuit.cells.mtypes

        div_mtype_to_mtype =\
            self.adapter.get_diverging(self.syn_or_conn,
                                       from='mtype', to="mtype")
        div_sclass_to_sclass =\
            self.adapter.get_diverging(self.syn_or_conn,
                                       from='sclass', to='sclass')


        return df

    def plot(self, df):

        ax = plt.subplots((3, 1))
        # seaborn.heatmap(df.pivot(index='pre_sclass',
        #                          column='post_sclass')['model_mean'], ax=ax[0])
        df['
