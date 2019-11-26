"""
Bar plot.
"""

import pandas
import seaborn
from dmt.data.observation import measurement
from dmt.data.observation.measurement import get_samples
from dmt.tk.field import Field, LambdaField, lazyproperty, WithFields
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

    @classmethod
    def get_dataframe(cls, data):
        """..."""
        return data.reset_index()\
            if isinstance(data, (pandas.Series, pandas.DataFrame)) else\
               measurement.concat_as_samples(data).reset_index()\

    def get_figure(self,
            data,
            *args,
            caption="Caption not provided",
            **kwargs):
        """
        Plot the dataframe.
        """
        graphic = seaborn\
            .catplot(
                data=self.get_dataframe(data),
                x=self.xvar,
                y=self.yvar,
                kind="bar",
                hue=self.gvar if self.gvar else None,
                height=self.height_figure,
                aspect=self.aspect_ratio_figure)\
            .set(
                xlabel=self.xlabel,
                ylabel=self.ylabel,
                title=kwargs.pop("title", ""))
        return Figure(
            graphic,
            caption=caption)

    def plot(self,
            *args, **kwargs):
        """
        Plot the dataframe
         """
        return self.get_figure(*args, **kwargs)

    def __call__(self,
            *args, **kwargs):
        """
        Make this class a callable,
        so that it can masquerade as a function!
        """
        return self.get_figure(*args, **kwargs)
