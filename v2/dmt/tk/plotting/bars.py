"""
Bar plot.
"""

import pandas
import seaborn
from dmt.data.observation import measurement
from dmt.tk.field import Field, lazyfield, WithFields
from .import golden_aspect_ratio
from .figure import Figure


class Bars(WithFields):
    """
    Specifies a plotting method, and all its required attributes.
    """
    title = Field(
        """
        Title to be displayed.
        If not provided phenomenon for the data will be used.
        """,
        __default_value__="")
    xvar = Field(
        """
        Column in the data-frame to be plotted along the x-axis.
        """)
    yvar = Field(
        """
        Column in the data-frame to be plotted along the y-axis.
        """)
    gvar = Field(
        """
        Column in the data-frame that will be plotted as different colored
        bars (at the same value of `yvar`).
        A default of empty string will be interpreted as not set, and hence
        no column in the data-frame to use as a grouping variable.
        """,
        __default_value__="")
    xlabel=Field(
        """
        The label to be displayed along the y-axis.
        Default value of an empty string will cause `xvar` to be displayed
        as `xlabel`.
        """,
        __default_value__="")
    ylabel=Field(
        """
        The label to be displayed along the y-axis.
        Default value of an empty string will cause `yvar` to be displayed
        as `ylabel`.
        """,
        __default_value__="")
    height_figure = Field(
        """
        Height of the figure.
        """,
        __default_value__ = 8.)
    aspect_ratio_figure = Field(
        """
        Aspect ratio width / height for the figure.
        """,
        __default_value__=golden_aspect_ratio)
    confidence_interval = Field(
        """
        float or “sd” or None, optional
        Size of confidence intervals to draw around estimated values.
        If “sd”, skip bootstrapping and draw the standard deviation of the
        observations. If None, no bootstrapping will be performed,
        and error bars will not be drawn.
        """,
        __default_value__="sd")

    @staticmethod
    def _get_phenomenon(dataframe_long):
        """
        Get phenomenon to be plotted.
        """
        return dataframe_long.columns[0]

    def _get_title(self, dataframe_long):
        """
        Get a title to display.
        """
        if self.title:
            return self.title
        phenomenon = self._get_phenomenon(dataframe_long)
        return ' '.join(word.capitalize() for word in phenomenon.split('_'))

    @staticmethod
    def _get_plotting_data(data, **kwargs):
        """
        Get a single long-form dataframe
        """
        return measurement.concat_as_samples(data, **kwargs)

    def get_figure(self,
            data,
            *args,
            caption="Caption not provided",
            **kwargs):
        """
        Plot the dataframe.
        """
        dataframe_long = self._get_plotting_data(data, **kwargs)
        graphic =\
            seaborn.catplot(
                data=dataframe_long.reset_index(),
                x=self.xvar,
                y=self.yvar,
                kind="bar",
                ci=self.confidence_interval,
                hue=self.gvar if self.gvar else None,
                height=self.height_figure,
                aspect=self.aspect_ratio_figure)
        return Figure(
            graphic.set(
                xlabel=self.xlabel if self.xlabel else self.xvar,
                ylabel=self.ylabel if self.ylabel else self.yvar,
                title=self._get_title(dataframe_long)),
            caption=caption)

    def plot(self,
            dataframe,
            *args, **kwargs):
        """
        Plot the dataframe
        """
        return self\
            .get_figure(
                dataframe,
                *args, **kwargs)

    def __call__(self,
            dataframe):
        """
        Make this class a callable,
        so that it can masquerade as a function!
        """
        return self.plot(dataframe)
