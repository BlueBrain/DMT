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
from dmt.vtk.utils.descriptor\
    import Field\
    ,      WithFCA

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
    """Base class that will plot the results of a measurement.
    All common plotting code will be listed here, some methods will
    have default implementations that base-classes may override,
    and the interface explosed by all concrete implementations of Plot
    will be specified here.
    """
    def __init__(self,
            measurement,
            analyzed_quantity="",
            logger_level= Logger.level.PROD,
            *args, **kwargs):
        """Initialize attributes that are common to all Plot concrete
        implementations.

        Parameters
        --------------------
        measurement :: Record[ data  :: DataFrame # may have more fields than
        ~                    , label :: String ]  # data and label.
        label       :: String #Optional
        ~
        """
        self._logger=\
            Logger(
                self,
                level=Logger.level.DEBUG)
        self._measurement=\
            measurement
        self._data=\
            self._measurement.data
        self._analyzed_quantity=\
            analyzed_quantity\
            if analyzed_quantity else\
               self._measurement.label
        self._output_dir_path=\
            os.path.join(
                kwargs.get(
                    "output_dir_path",
                    os.getcwd()),
                "report")
        self._file_name=\
            kwargs.get(
                "file_name", "report")
        self._yvar=\
            kwargs.get(
                "yvar", None)
        self._xvar=\
            kwargs.get(
                "xvar", None)
        self._given=\
            kwargs.get(
                "given", {})
        self.set_customization(
            measurement)

    def set_customization(self,
            measurement,
            *args, **kwargs):
        """Extract plotting customization from a measurement."""
        try:
            self._title=\
                measurement.phenomenon.name
        except:
            self._title=\
                getattr(
                    measurement,
                    "label",
                    kwargs.get(
                        "title",
                        self.__class__.__name__))
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
            self._logger.debug(
                self._logger.get_source_info(),
                "set plot customization {}: {}"\
                .format(key, value))
            if hasattr(self, key):
                try:
                    setattr(self, key, value)
                    self.logger.success(
                        self.logger.get_source_info(),
                        "Attribute {} set to {}".format(key, value))
                except AttributeError as aerr:
                    self._logger.alert(
                        self._logger.get_source_info(),
                        "Caught AttributeError: {}".format(aerr),
                        "while trying to set attribute {}".format(key))

                    _key=\
                        "_{}".format(key)
                    if hasattr(self, _key):
                        self._logger.debug(
                            self._logger.get_source_info(),
                            "instead, try to set {}".format(_key))
                        try:
                            setattr(self, _key, value)
                            self.logger.success(
                                self.logger.get_source_info(),
                                "Attribute {} set to {}".format(_key, value))
                        except AttributeError as aerr:
                            self._logger.alert(
                                self._logger.get_source_info(),
                                "Caught AttributeError: {}".format(aerr),
                                "while trying to set attribute {}"\
                                .format(_key))
                            self._logger.alert(
                                self._logger.get_source_info(),
                                "Neither {} nor {} are attributes "\
                                .format(key, _key))

        return self

    @property
    def title(self):
        """..."""
        return self._title

    @property
    def xlabel(self):
        """..."""
        return self._xvar if self._xvar else self._xlabel

    @property
    def ylabel(self):
        """..."""
        return self._yvar if self._yvar else self._ylabel

    def analyzing(self,
            analyzed_quantity):
        """..."""
        assert\
            analyzed_quantity in self._data
        self._analyzed_quantity=\
            analyzed_quantity
        return self

    def get_plotting_dataframe(self,
            measurement=None,
            allow_multi_indexed=False):
        """Extract a simplified dataframe from the measurement,
        that contains only the data that will be plotted.
        """
        measurement=\
            measurement\
            if measurement is not None else\
               self._measurement
        if not isinstance(measurement.data.columns, pd.MultiIndex):
            dataframe=\
                measurement.data
        else:
            try:
                dataframe=\
                    measurement.data[
                        self._analyzed_quantity]
            except KeyError as e:
                self._logger.error(
                    self._logger.get_source_info(),
                    "Expected {} not found in dataframe columns"\
                    .format(self._yvar))
                raise e
        if not isinstance(dataframe.index, pd.MultiIndex):
            return dataframe
        for level, value in self._given.items():
            dataframe=\
                dataframe.xs(
                    value,
                    level=level)
        if allow_multi_indexed:
            return dataframe
        if isinstance(dataframe.index, pd.MultiIndex):
            raise ValueError(
                """Insufficient conditions to reduce the multi-index {}
                of the measurement dataframe""".format(dataframe.index))
        return dataframe

    def plotting(self,
            quantity):
        """Name of the quantity whose mean is plotted."""
        self._yvar = quantity
        return self

    def with_xvar(self,
            variable):
        """The x-variable to plot against."""
        self._xvar= variable
        try:
            self._xlabel=\
                getattr(variable,
                        "label",
                        str(variable))
        except:
            pass
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
        self._given={
            k: v for k,v in kwargs.items()}
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
            else self._output_dir_path
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
        self._logger.info(
            self._logger.get_source_info(),
            "Generating {}".format(output_file_path))

        figure.savefig(
            output_file_path,
            dpi=100)
        
        return\
            (output_file_path, fname)



class MultiPlot(
        Plot):
    """Plot several plots (of the same kind),
    in separate figures."""
    BasePlotType=\
        Field(
            __name__="BasePlotType",
            __type__=type,
            __typecheck__=Field.typecheck.subtype(Plot),
            __doc__="type of the individual plots.")

    def __init__(self,
            measurement,
            *args, **kwargs):
        """..."""
        self._measurement_labels=\
            measurement.data.columns.levels[0]
        self._yvar=\
            measurement.phenomenon.label
        self._title_common=\
            measurement.phenomenon.name
        super().__init__(
            measurement,
            *args, **kwargs)
        self.base_plotter=\
            self.BasePlotType(
                self._measurement)

    def get_yvar(self, column_label):
        """..."""
        return "{}_{}".format(
            column_label,
            self._yvar)

    def plot(self,
            *args, **kwargs):
        """..."""
        def __get_plot(column_label):
            """..."""
            return self\
                .base_plotter\
                .analyzing(
                    column_label)\
                .plotting(
                    self._yvar)\
                .versus(
                    self._xvar)\
                .given(
                    **self._given)\
                .with_customization(
                    title="{} {}".format(
                        column_label,
                        self._title_common),
                    **kwargs)\
                .plot()

        return {
            label: __get_plot(label)
            for label in self._measurement_labels}

    def save(self,
            figures,
            output_dir_path=None,
            *args, **kwargs):
        """Save figures in the dict figures,
        each in its own file!"""
        return{
            figure_label: self.base_plotter.save(
                figure,
                output_dir_path=output_dir_path,
                file_name="{}_report.png".format(figure_label))
            for figure_label, figure in figures.items()}
                    
class MultiFigure(
        WithFCA):
    """A plot composed of many."""
    BasePlotType=\
        Field(
            __name__="BasePlotType",
            __type__=type,
            __typecheck__=Field.typecheck.subtype(Plot),
            __doc__="type of the individual plots.")

    def __init__(self,
            measurement,
            *args, **kwargs):
        """..."""
        self._measurement=\
            measurement
        self._yvar= "Y"
        self._xvar= "X"
        self._given_parameter_values={}
        self._customization={}
        super().__init__(
            *args, **kwargs)

    def plotting(self,
            yvar):
        """..."""
        self._yvar= yvar
        return self

    def versus(self,
            xvar):
        """..."""
        self._xvar= xvar
        return self

    def given(self,
            **kwargs):
        self._given_parameter_values={
            k: v for k,v in kwargs.items()}
        return self

    def with_customization(self,
            **kwargs):
        """..."""
        self._customization=\
            kwargs
        return self

    def plot(self,
             **kwargs):
        """..."""
        measurement_labels=\
            self._measurement.data.columns.levels[0]
        yvar=\
            self._measurement.phenomenon.label
        title_common=\
            self._measurement.phenomenon.name

        def __get_plot(column_label):
            """..."""
            return\
                self.BasePlotType(
                    self._measurement)\
                    .analyzing(
                        column_label)\
                    .plotting(
                        self._yvar)\
                    .versus(
                        self._xvar)\
                    .given(
                        **self._given_parameter_values)\
                    .with_customization(
                        title="{} {}".format(column_label, title_common),
                        **kwargs)\
                    .plot()

        return{
            label: __get_plot(label)
            for label in measurement_labels}

    def save(self,
            figures,
            output_dir_path=None,
            **kwargs):
        """..."""
        measurement_labels=\
            self._measurement.data.columns.levels[0]
        yvar=\
            self._measurement.phenomenon.label
        title_common=\
            self._measurement.phenomenon.name

        def __save_plot(figure_label, figure):
            """..."""
            return\
                self.BasePlotType(
                    self._measurement)\
                    .analyzing(
                        figure_label)\
                    .plotting(
                        self._yvar)\
                    .versus(
                        self._xvar)\
                    .given(
                        **self._given_parameter_values)\
                    .with_customization(
                        title="{} {}".format(figure_label, title_common),
                        **kwargs)\
                    .save(
                        figure,
                        output_dir_path=output_dir_path,
                        file_name="{}_report.png".format(figure_label))
        return{
            figure_label: __save_plot(figure_label, figure)
            for figure_label, figure in figures.items()}


from dmt.vtk.plotting.bars\
    import BarPlot
from dmt.vtk.plotting.lines\
    import LinePlot
from dmt.vtk.plotting.heatmap\
    import HeatMap
