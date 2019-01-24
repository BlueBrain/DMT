"""Plotting utils."""
from abc import ABC, abstractmethod
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import pylab
from matplotlib.font_manager import FontProperties
from dmt.vtk.utils.exceptions import RequiredKeywordArgumentError
from dmt.vtk.utils.utils import get_file_name_base
from dmt.vtk.utils.logging import Logger, with_logging

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


@with_logging(Logger.level.STUDY)
class Plot(ABC):
    """Base class for classes that will plot data.
    All common plotting code will be listed here, as well as
    the interface explosed by all concrete implementations of Plot."""

    def __init__(self,
            data,
            *args, **kwargs):
        """Initialize attributes that are common to all
        Plot concrete implementations.
        """
        self._data_record= data
        self._data= data.data
        self._label= data.label
        self.title=\
            kwargs.get(
                'title',
                self.__class__.__name__)
        self.xlabel=\
            kwargs.get(
                'xlabel', 'X')
        self.ylabel=\
            kwargs.get(
                'ylabel', 'Y')
        self.output_dir_path=\
            os.path.join(
                kwargs.get(
                    "output_dir_path",
                    os.getcwd()),
                "report")
        self.legend_loc=\
            kwargs.get(
                'legend_loc',
                'upper left')
        self.height=\
            kwargs.get(
                'height', 10)
        self.width=\
            kwargs.get(
                'width', None)
        self.colors=\
            kwargs.get(
                'colors',
                ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'w'])
        self.file_name=\
            kwargs.get(
                "file_name",
                "report")

    def with_customization(self,
            *args, **kwargs):
        """Update customization to the plot."""
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self

    @property
    def dataframe(self):
        """..."""
        return\
            self._data[self._label]\
            if self._label in self._data\
               else self._data

    @abstractmethod
    def plot(self,
            *args, **kwargs):
        """Make the plot"""
        pass

    def save(self,
        figure,
        output_dir_path=None,
        file_name="report.png"):
        """..."""
        output_dir_path=\
            output_dir_path if output_dir_path else self.output_dir_path
        file_name=\
            file_name if file_name else self.file_name
        if not os.path.exists(output_dir_path):
            os.makedirs(
                output_dir_path)
        fname_base=\
            get_file_name_base(
                file_name if file_name is not None else "report_plot")
        fname=\
            "{}.png".format(fname_base)
        output_file_path=\
            os.path.join(
                output_dir_path,
                fname)
        self.logger.info(
            self.logger.get_source_info(),
            "Generating {}".format(output_file_path))

        figure.savefig(
            output_file_path,
            dpi=100)
        
        return\
            (output_file_path, fname)
