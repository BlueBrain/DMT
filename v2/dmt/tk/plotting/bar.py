"""
Bar plot.
"""

import seaborn
from . import golden_aspect_ratio
from dmt.tk.field import Field, lazyproperty, WithFields

class BarPlotter(WithFields):
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

    def plot(self,
            dataframe):
        """
        Make a plot.
        """
        return seaborn\
            .catplot(
                data=dataframe,
                x=self.xvar,
                y=self.yvar,
                kind="bar",
                hue=self.gvar if self.gvar else None,
                height=self.height_figure,
                aspect=self.aspect_ratio_figure)\
            .set(
                xlabel=self.xlabel if self.xlabel else self.xvar,
                ylabel=self.ylabel if self.ylabel else self.yvar)
