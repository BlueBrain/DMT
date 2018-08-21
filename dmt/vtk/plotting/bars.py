"""Class to help plot bars."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import pylab
from matplotlib.font_manager import FontProperties
from dmt.vtk.plotting import golden_figure, Plot



class BarPlot(Plot):
    """Class to help plot bars."""

    def __init__(self, *args, **kwargs):
        """Initialize bar plot specific attributes."""
        super(BarPlot, self).__init__(*args, **kwargs)


    def plot(self, *plotting_datasets, save=True):
        """Make the bar plot.

        Arguments
        -----------------------------------------------------------------------
        You may pass Records as the argument sequence (ArgSeq). Each of these
        arguments must be a Record containing a dataframe as 'data', and a
        string as 'label'. The label will be used to produce a legend.
        plotting_datasets :: ArgSeq(Record(data :: DataFrame["mean", "std"],
        ~                                  label :: String))
        -----------------------------------------------------------------------

        We assume that each data frame has the same order to its index. For
        example, if plotting cell density by layer, each data-frame must then
        have it's mean and stdev ordered either increasing, or decreasing, or
        even a random order (as long as each data-frame is ordered the same
        way).

        Other information relevant for the plot must be initialized at class
        creation.
        """

        if len(plotting_datasets) == 0:
            raise ValueError("Nothing to plot!")

        fig = golden_figure(height=self.height, width=self.width)
        nbar = len(plotting_datasets)
        width = 1.0 / (1.0 + nbar)

        #assume all data-frame indexes have the same order
        xs = list(plotting_datasets[0].data.index)
        x = np.arange(len(xs))
        x0 = x - (nbar / 2) * width

        index = 1
        for pe in plotting_datasets:
            print("plot index {}".format(index))
            df = pe.data.fillna(0.0)
            a_plot = plt.bar(x0 + index * width,
                             df['mean'].values,
                             width,
                             color=self.colors[(index - 1) % len(self.colors)],
                             yerr=df['std'].values,
                             label=pe.label)
            index += 1

        plt.title(self.title, fontsize=24)
        plt.xlabel(self.xlabel, fontsize=20)
        plt.xticks(x - width / 2., xs)

        fontP = FontProperties()
        fontP.set_size('small')
        plt.legend(prop=fontP, loc=self.legend_loc)

        if save:
            return self.save(fig)

        return fig




