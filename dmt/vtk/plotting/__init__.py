"""Plotting utils."""
from abc import ABC, abstractmethod
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import pylab
from matplotlib.font_manager import FontProperties
from dmt.vtk.utils.exceptions import RequiredKeywordArgumentError
from dmt.vtk.utils.utils import get_file_name_base

def golden_figure(width=None, height=None):
    """A figure with golden ration as it's aspect ratio,
    if both height and width have not been provided.
    Parameters
    ----------
    @width :: Float #optional argument
    @height :: Float #optional argument"""
    golden_height = 10. if width is None else 2. * width / (1. + np.sqrt(5))
    height = golden_height if height is None else height
    width =  0.5 * (1. + np.sqrt(5)) * height if width is None else width

    fig = plt.figure()
    fig.set_size_inches(width, height)
    return fig


class Plot(ABC):
    """Base class for classes that will plot data.
    All common plotting code will be listed here, as well as
    the interface explosed by all concrete implementations of Plot."""

    def __init__(self, *args, **kwargs):
        """Initialize attributes that are common to all
        Plot concrete implementations.
        """
        self.title = kwargs.get('title', self.__class__.__name__)
        self.xlabel = kwargs.get('xlabel', 'X')
        self.ylabel = kwargs.get('ylabel', 'Y')
        self.output_dir_path = kwargs.get('output_dir_path', ".")
        self.legend_loc = kwargs.get('legend_loc', 'upper left')
        self.height = kwargs.get('height', 10)
        self.width = kwargs.get('width', None)
        self.colors = kwargs.get('colors', ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'w'])
        self.file_name = kwargs.get('file_name', "report")



    @abstractmethod
    def plot(self, *args, **kwargs):
        """Make the plot"""
        pass

    def save(self, fig, output_dir_path=None, file_name=None):
        opd = output_dir_path if output_dir_path is not None \
              else self.output_dir_path
        fname  = file_name if file_name is not None else self.file_name
        if opd:
            print("Save plot at {} with file name {}".format(opd, fname))
            if not os.path.exists(opd):
                os.makedirs(opd)
            fname_base = get_file_name_base(fname if fname is not None
                                            else "report_plot")
            print("file name base {}".format(fname_base))
            output_file_path = os.path.join(opd, "{}.png".format(fname_base))
            print("Generating {}".format(output_file_path))
            fig.savefig(output_file_path, dpi=100)

            print("figure has been saved")
            return output_file_path
        else:
            print("WARNING! No output directory provided. Not saving.")
            return fig
