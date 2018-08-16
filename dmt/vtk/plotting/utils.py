"""Plotting utils."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import pylab
from matplotlib.font_manager import FontProperties
from dmt.vtk.utils.exceptions import RequiredKeywordArgumentError

def plot_bars(plotting_datas, *args, **kwargs):
    """A method to plot data. Bars will be plotted in order passed
    in list 'plotting_data'.

    Parameters
    ------------------------------------------------------------------------
    plotting_datas :: [Measurement] #list of measurements to be plotted

    Return
    ------------------------------------------------------------------------
    Directory path where plots are saved.

    Implementation Note
    ------------------------------------------------------------------------
    For now we let 'Measurement' be a record:

    Measurement = Record(measurement_label :: String,
    ~                    region_label :: String,
    ~                    data :: DataFrame["region", "mean", "std"])

    We assume that each Measurement.data has the same columns,
    and the same index.
    For example, if we are analyzing composition by cortical layer, each
    Measurement.data should have the index
    ['L1', 'L2', 'L3', 'L4', 'L5', 'L6']. The DataFrame may bave NaNs.
    """
    if len(plotting_datas) == 0:
        raise ValueError("Cannot plot without data, len(plotting_datas) == 0 ")

    output_dir_path = kwargs.get('output_dir_path', None)
    legend_loc = kwargs.get('legend_loc', 'upper_left')
    fheight = kwargs.get('fheight', 10)
    fwidth = kwargs.get('fwidth', None)
    colors = kwargs.get('colors',
                                    ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'w'])
    file_name = kwargs.get('file_name', None)

    try:
        title = kwargs['title']
    except:
        raise RequiredKeywordArgumentError("title")
    fig = golden_figure(height=fheight, width=fwidth)

    nbar = len(plotting_datas)
    width = 1.0 / (1.0 + nbar)
    #expecting region_label to be same for all plotting_datas
    region_label = plotting_datas[0].region_label
    region_names = list(plotting_datas[0].index)
    x = np.arange(len(region_names))
    x0 = x - (nbar / 2) * width

    plot_index = 1
    for pe in plotting_datas:
        df = pe.data.fillna(0.0)
        a_plot = plt.bar(x0 + plot_index * width,
                         df['mean'].values,
                         width,
                         color=color[(plot_index - 1) % len(colors)],
                         yerr=df['std'].values,
                         label=pe.label)
        plot_index += 1

    plt.title(title, fontsize=24)
    plt.xlabel(region_label, fontsize=20)
    plt.xticks(x - width / 2., region_names)

    fontP = FontProperties()
    fontP.set_size('small')
    plt.legend(prop=fontP, loc=legend_loc)

    if output_dir_path and file_name:
        if not os.path.exists(output_dir_path):
            os.makedirs(output_dir_path)
        output_file = os.path.join(output_dir_path, file_name + ".png")
        print("Generating {}".format(output_file))
        pylab.savefig(output_file, dpi=100)
        return output_file

    return None


def plot_lines(plotting_datas, *args, **kwargs):
    """plot lines for self.circuit's measurement and
    other circuits' measurements
    @args plotting_datas :: list[PlottingData]
    PlottingData: dict {'data': DataFrame<Mean, Error>, 'label': str}
    @return :: Path where the plot will be saved"""

    if len(plotting_datas) == 0:
        raise InvalidArgumentError('plotting_datas')

    output_dir_path = kwargs.get('output_dir_path', None)
    context = kwargs.get('context', None)
    legend_loc = kwargs.get('legend_loc', 'upper_left')
    fheight = kwargs.get('fheight', 10)
    fwidth = kwargs.get('fwidth', None)
    colors = kwargs.get('colors', ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'w'])
    line_point_types = kwargs.get('line_point_types',
                                  ['-o', '--o', '-s', '--s'])
    layer_names = kwargs.get("layer_names",
                             ['I', 'II', 'III', 'IV', 'V', 'VI'])
    layer_starts = kwargs.get("layer_starts", [])
    layer_ends = kwargs.get("layer_ends", [])

    fig = putils.golden_figure(fwidth, fheight)
    axes = fig.add_subplot(111)

    ymax = np.iinfo(np.int32(10)).min
    ymin = np.iinfo(np.int32(10)).max
    pidx = 0
    for plotting_data in plotting_datas:
        data_frame = self.anatomically_ordered(plotting_data['data'])
        for component in self.measurement_components:
            cdf = data_frame[data_frame['component'] == component]
            axes.errorbar(cdf[self.location_label].values,
                          cdf['mean'].values,
                          yerr=cdf['error'].values,
                          label=plotting_data['label'],
                          fmt=colors[component]+line_point_types[pidx])
            ymin = np.minimum(ymin, cdf['mean'].min())
            ymax = np.maximum(ymax, cdf['mean'].max())
        pidx += 1

    plt.title(self.title, fontsize=24)
    plt.xlabel("Depth", fontsize=20)
    plt.ylabel(self.measurement_label)

    if len(layer_starts) > 0 and len(layer_ends) > 0:
        for d in list(layer_starts) + [layer_ends[-1]]:
            plt.plot((d, d), (ymin, ymax), 'k-', linewidth=4)

        plt.xticks((layer_starts + layer_ends) / 2.0,
                   layer_names, fontsize=20)

    fontP = FontProperties()
    fontP.set_size('small')
    plt.legend(prop=fontP, loc=legend_loc)

    if output_dir_path:
        if not os.path.exists(output_dir_path):
            os.makedirs(output_dir_path)
        output_file_path = os.path.join(output_dir_path,
                                        "comparison_report.png")
        print("Generating %s " % output_file_path)
        pylab.savefig(output_file_path, dpi=100)
        return output_file_path
    else:
        return ""

