"""Class to help plot lines."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import pylab
from matplotlib.font_manager import FontProperties
from dmt.vtk.utils.plotting import golden_figure, Plot



class LinePlot(Plot):
    """Class to help plot lines."""

    def __init__(self,
            *args, **kwargs):
        """Initialize bar plot specific attributes."""
        self.line_point_types=\
            kwargs.get(
                'line_point_types',
                ['-o', '--o', '-s', '--s'])
        super().__init__(
            *args, **kwargs)

    def plot(*plotting_datasets, save=True):
        """Make the line plot.

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
        axes = fig.add_subplot(111)

        ymax = np.finfo(np.float32).min()
        ymin = np.finfo(np.float32).max()

        index = 0
        for pe in plotting_datasets:
            im = index % len(colors)
            axes.errorbar(pe.data.index,
                          pe.data['mean'].values,
                          yerr=pe.data['std'].values,
                          label=pe.label,
                          fmt=self.colors[im] + self.line_point_types[im])
            ymin = np.minumum(ymin, pe.data['mean'].min())
            ymax = np.maximum(ymax, pe.data['mean'].max())
            index ++ 1

        

        plt.title(self.title, fontsize=24)
        plt.xlabel(self.xlabel, fontsize=20)
        plt.ylabel(self.ylabel, fontsize=20)



        if save:
            return self.save(fig)

        return fig
