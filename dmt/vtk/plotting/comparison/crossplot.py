"""Crosses to compare two equivalent data."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import pylab
from matplotlib.font_manager import FontProperties
from dmt.vtk.plotting import golden_figure
from dmt.vtk.plotting.comparison import ComparisonPlot
from dmt.vtk.utils.logging import Logger, with_logging
from dmt.vtk.utils.collections import Record

@with_logging(Logger.level.STUDY)
class CrossPlotComparison(ComparisonPlot):
    """Compare two datasets with cross plot.
    A ComparisonPlot will hold data that it will be plot against one or more
    other datasets.
    """

    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args, **kwargs)

    @property
    def compared_datasets(self):
        """..."""
        cv = self.compared_values[0]
        try:
            data=\
                self.comparison_data.xs(
                    cv.name,
                    level=self.comparison_level)
            return [Record(data=data, label=cv.label)]
        except Exception as e:
            self._logger.error(
                self._logger.get_source_info(),
                """Could not get comparison data with
                name and level. Exception {}""".format(e))

    def with_xvar(self,
            variable):
        """Moved here, because it's super definition was creating
            some problems. This method was to be used to set the variable
            along the x-axis, which we assumed would be one of the levels
            in the index. However, that is not the case in a cross-plot."""
        self._xvar=\
            getattr(
                variable,
                "label",
                variable)
        return self

    def plot(self,
            with_customization={}):
        """
        Compare this ComparisonPlot's data against those in datasets.

        Parameters
        ------------------------------------------------------------------------
        datasets  :: Either[ DataFrame[mean :: Double, std  :: Double],
        ~                    DataFrame[mean :: Double]] ]#with Multindex
        comparison_level  :: Either[String, Integer], #Level in datasets to be compared
        compared_values :: List[Record[ label :: T,     #values to be compared,
        ~                               name :: String]]#can be any non-Nonetype
        ~                      
        given :: List[Either[Integer, String]] #other levels to show the result for
        """
        self.logger.debug(
            self.logger.get_source_info(),
            "plot customization: {}".format(with_customization))

        figure=\
                golden_figure(
                    height=self._height,
                    width=self._width)
        ydata=\
            self.get_plotting_dataframe(
                allow_multi_indexed=True)
        self.logger.debug(
            self.logger.get_source_info(),
            """Plot cross plot comparison with ydata: {}"""\
            .format(ydata),
            """and comparison data {}"""\
            .format(self.compared_datasets[0].data))

        def __get_nan_removed(axis_data):
            """..."""
            axis_means=\
                axis_data["mean"].values
            mean_nan_index=\
                np.isnan(axis_means)
            mean_no_nan=\
                axis_means[
                    np.logical_not(mean_nan_index)]
            if len(mean_no_nan) == 0:
                raise ValueError(
                    "All mean values are NaN!")
            axis_err=\
                axis_data["std"].values
            err_nan_index=\
                np.isnan(axis_err)
            err_no_nan=\
                axis_err[
                    np.logical_not(err_nan_index)]
            return(
                mean_no_nan,
                err_no_nan)

        def __get_axis_min(axis_data):
            """..."""
            mean_values_no_nan, error_values_no_nan=\
                __get_nan_removed(axis_data)
            return\
                0. if np.min(mean_values_no_nan) >= 0. else\
                (np.nanmin(mean_values_no_nan) + (
                    0. if len(error_values_no_nan) == 0.
                    else np.min(error_values_no_nan)))

            
        def __get_axis_max(axis_data):
            """..."""
            mean_values_no_nan, error_values_no_nan=\
                __get_nan_removed(axis_data)
            return\
                np.max(mean_values_no_nan) +\
                (0. if len(error_values_no_nan) == 0\
                 else np.max(error_values_no_nan))

        ys=\
            ydata["mean"].values
        yerr=\
            ydata["std"].values
        ymax=\
            with_customization\
            .get("axis", {})\
            .get("ymax", __get_axis_max(ydata))
        ymin=\
            with_customization\
            .get("axis", {})\
            .get("ymin", __get_axis_min(ydata))
        xdata=\
            self.compared_datasets[0]\
                .data.loc[
                    ydata.index]
        xs=\
            xdata["mean"].values
        xerr=\
            xdata["std"].values
        xmax=\
            with_customization\
            .get("axis", {})\
            .get("xmax", __get_axis_max(xdata))
        xmin=\
            with_customization\
            .get("axis", {})\
            .get("xmin", __get_axis_min(xdata))
        color=\
            with_customization.get(
                "color", "blue")
        self.logger.debug(
            self.logger.get_source_info(),
            "customization colors {}".format(color))
        plt.errorbar(
            xs, ys,
            fmt="o",
            xerr=xerr, yerr=yerr)
        colors=\
            color if isinstance(color, list)\
            else len(xs) * ["blue"]
        for x, y, c in zip(xs, ys, colors):
            plt.scatter([x], [y], c=c, s=160)
        min_val=\
            min(xmin,  ymin)
        max_val=\
            max(xmax, ymax)
        self.logger.debug(
            self.logger.get_source_info(),
            "plot a diagonal from min {} to max {}"\
            .format(
                min_val,
                max_val))
        plt.plot(
            [min_val, max_val],
            [min_val, max_val],
            "-")
        plt.axis([
            xmin, xmax, ymin, ymax])
        plt.title(
            self._title,
            fontsize=24)
        plt.ylabel(
            self._ylabel,
            fontsize=20)
        plt.xlabel(
            self.compared_datasets[0].label,
            fontsize=20)
        legend=\
            with_customization\
            .get("legend", None)
        if legend:
            plt.legend(**legend)

        fontP = FontProperties()
        fontP.set_size('small')

        return figure
