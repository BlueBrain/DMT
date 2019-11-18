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
    Specifies a plotting method, and the all the variables that can be set 
    """
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

    def __plotting_parameters(self,
            **kwargs):
        """
        Extract plotting parameters from keyword arguments.
        """
        pass

    def get_dataframe(self, data):
        """..."""
        return data
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
                ylabel=self.ylabel)
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
