"""Plotting utils."""
from abc import ABC, abstractmethod
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib\
    import pylab
from matplotlib.font_manager\
    import FontProperties
from dmt.vtk.utils.exceptions\
    import RequiredKeywordArgumentError
from dmt.vtk.utils.utils\
    import get_file_name_base
from dmt.vtk.utils.collections\
    import Record
from dmt.vtk.utils.logging\
    import Logger\
    ,      with_logging

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
            measurement,
            *args, **kwargs):
        """Initialize attributes that are common to all
        Plot concrete implementations.
        """
        self._data_record=\
            Record(
                data=measurement.data,
                label=measurement.label)
        self._data= self._data_record.data
        self._label= self._data_record.label

        self._yvar=\
            kwargs.get(
                "yvar", None)
        self._xvar=\
            kwargs.get(
                "xvar", None)
        self._given=\
            kwargs.get(
                "given", {})
        self._output_dir_path=\
            os.path.join(
                kwargs.get(
                    "output_dir_path",
                    os.getcwd()),
                "report")
        self._file_name=\
            kwargs.get(
                "file_name",
                "report")
        self.set_customization(
            measurement)

    def set_customization(self,
            measurement,
            *args, **kwargs):
        """Extract plotting customization from a measurement."""
        try:
            self._title=\
                measurement.label
        except AttributeError:
            self_title=\
                kwargs.get(
                    "title", self.__class__.__name__)
        try:
            self._xlabel=\
                measurement.parameter
        except AttributeError:
            self._xlabel=\
                kwargs.get("xlabel", "X")
        try:
            self._ylabel=\
                "{} / [{}]".format(
                    "mean {}".format(
                        measurement.phenomenon.name.lower()),
                    measurement.units) 
        except AttributeError:
            self._ylabel=\
                kwargs.get("ylabel", "Y")

        self._legend_loc=\
            kwargs.get(
                'legend_loc',
                'upper left')
        self._height=\
            kwargs.get(
                'height', 10)
        self._width=\
            kwargs.get(
                'width', None)
        self._colors=\
            kwargs.get(
                'colors',
                ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'w'])




    def with_customization(self,
            *args, **kwargs):
        """Update customization to the plot."""
        for key, value in kwargs.items():
            self.logger.debug(
                self.logger.get_source_info(),
                "set plot customization {}: {}"\
                .format(key, value))
            if hasattr(self, key):
                try:
                    setattr(self, key, value)
                except AttributeError as aerr:
                    self.logger.alert(
                        self.logger.get_source_info(),
                        "Caught AttributeError: {}".format(aerr),
                        "while trying to set attribute {}".format(key),
                        "will try to set _{} instead ".format(key))
                    setattr(self, "_{}".format(key), value)
        return self

    @property
    def xlabel(self):
        """..."""
        return self._xvar if self._xvar else self._xlabel

    @property
    def ylabel(self):
        """..."""
        return self._yvar if self._yvar else self._ylabel

    def get_dataframe(self,
            allow_multi_indexed=False):
        """..."""
        data_frame=\
            self._data[self._label]\
            if self._label in self._data\
               else self._data
        if not isinstance(data_frame.index, pd.MultiIndex):
            return data_frame
        for level, value in self._given.items():
            data_frame=\
                data_frame.xs(
                    value,
                    level=level)
            
        if allow_multi_indexed:
            return data_frame

        if isinstance(data_frame.index, pd.MultiIndex):
            raise ValueError(
                """In {} Insufficient conditions to reduce the MultiIndexed
                data to a singly indexed dataframe for plotting."""\
                .format(self))

        return data_frame

    def plotting(self,
            quantity):
        """Name of the quantity whose mean is plotted."""
        self._yvar = quantity
        return self

    def with_xvar(self,
            variable):
        """The x-variable to plot against."""
        self._xvar= variable
        return self

    def versus(self,
            variable):
        """set the xvar"""
        return self.with_xvar(variable)
            
    def given(self,
            **kwargs):
        """The data frame provided as data to Plot (subclass)
        may be a multi-indexed data-frame. For example a cell density
        data-frame that provides mean and std of cell density by cortical
        layer in several regions. This data-frame will be indexed by tuples
        providing values of depth and region.
        The x variable for plotting is set by the method 'versus', but
        you will need to set the remaining index fields using 'given'."""
        self._given = {k: v for k,v in kwargs.items()}
        return self

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
            output_dir_path if output_dir_path\
            else self.output_dir_path
        file_name=\
            file_name if file_name\
            else self.file_name
        if not os.path.exists(output_dir_path):
            os.makedirs(
                output_dir_path)
        fname_base=\
            get_file_name_base(
                file_name if file_name is not None\
                else "report_plot")
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

from dmt.vtk.plotting.bars\
    import BarPlot
from dmt.vtk.plotting.lines\
    import LinePlot
from dmt.vtk.plotting.heatmap\
    import HeatMap
