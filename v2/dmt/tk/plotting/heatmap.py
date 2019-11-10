"""
Plot heat maps.
"""
import pandas
import matplotlib.pyplot as plt
import seaborn
from dmt.tk.plotting.utils import pivot_table
from dmt.tk.field import Field, LambdaField, WithFields
from dmt.data.observation import measurement
from . import golden_aspect_ratio
from .figure import Figure

class HeatMap(WithFields):
    """
    Define the requirements and behavior of a heatmap.
    """
    xvar = Field(
        """
        Variable (column in the data-frame to plot) that should vary along the
        x-axis of the heat-map.
        """)
    yvar = Field(
        """
        Variable (column in the data-frame to plot) that should vary along the
        y-axis of the heat-map.
        """)
    vvar = Field(
        """
        Variable (column in the data-frame to plot) that provides the intensity
        value of the heat-map cells.
        """)
    xlabel = LambdaField(
        """
        The label to be displayed along the y-axis.
        Default value of an empty string will cause `xvar` to be displayed
        as `xlabel`.
        """,
        lambda self: self.xvar)
    ylabel = LambdaField(
        """
        The label to be displayed along the y-axis.
        Default value of an empty string will cause `yvar` to be displayed
        as `ylabel`.
        """,
        lambda self: self.yvar)
    height_figure = Field(
        """
        Height of the figure.
        """,
        __default_value__ = 8.)
    aspect_ratio_figure = Field(
        """
        Aspect ratio width / height for the figure.
        """,
        __default_value__=1.)
    fill_missing_value = Field(
        """
        Some values in the heatmap matrix (which should be a square matrix)
        may be missing. This field provides the default value to impute
        the missing.
        """,
        __default_value__=0.)
    get_dataframe = LambdaField(
        """
        Call back to get a dataframe from the measurement.
        """,
        lambda self: self._get_dataframe_default)

    @staticmethod
    def _flattened(variable):
        """
        Flatten a possibly tuple variable.
        """
        if isinstance(variable, str):
            return variable
        if isinstance(variable, tuple):
            return '_'.join(variable)
        raise TypeError(
            """
            HeatMap dataframe variables should be:
            1. either a string
            2. or a tuple of strings
            Not: {}
            """.format(variable))

    @staticmethod
    def _get_dataframe_default(data):
        """..."""
        assert isinstance(data, pandas.DataFrame) or len(data) == 1,\
            """
            Cannot decide which one to plot among more than one dataset:
            \t{}
            """.format(list(data.keys()))
        dataframe = measurement\
            .get_summary(
                data if isinstance(data, pandas.DataFrame)\
                else list(data.values())[0])\
            .reset_index()
        if not isinstance(dataframe.columns, pandas.MultiIndex):
            return dataframe
        return pandas\
            .DataFrame(
                dataframe.values,
                columns=pandas.Index([
                    HeatMap._flattened(t) for t in dataframe.columns.values]))

    def get_figure(self,
            data,
            *args,
            caption="Caption not provided",
            **kwargs):
        """
        Plot the figure.

        Arguments
        --------------
        `data`: A single pandas dataframe with an index of length 2, and only
        1 column (only the zeroth column will be plotted.)
        """
        matrix = pandas\
            .pivot(
                self.get_dataframe(data),
                values=self._flattened(self.vvar),
                index=self._flattened(self.xvar),
                columns=self._flattened(self.yvar))\
            .fillna(self.fill_missing_value)
        graphic = seaborn\
            .heatmap(
                matrix,
                cbar=True,
                cmap="rainbow",
                xticklabels=True,
                yticklabels=True)
        plt.yticks(rotation=0)
        plt.ylabel(self.ylabel)
        plt.xticks(rotation=90)
        plt.xlabel(self.xlabel)
        return Figure(
            graphic,
            caption=caption)
