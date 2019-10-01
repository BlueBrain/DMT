"""
Bar plot.
"""

import pandas
import seaborn
from dmt.data.observation import measurement
from dmt.tk.field import Field, lazyproperty, WithFields
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

    def __plotting_parameters(self,
            **kwargs):
        """
        Extract plotting parameters from keyword arguments.
        """
        pass

    @staticmethod
    def _as_single_dataframe(data):
        """
        Get data as a single dataframe that can be plotted.
        """
        return\
            pandas.concat([
                measurement.get_samples(dataframe).assign(dataset=dataset)
                for dataset, dataframe in data.items()]
            ).reset_index()

    def get_figure(self,
            data,
            *args,
            caption="Caption not provided",
            **kwargs):
        """
        Plot the dataframe.
        """
        graphic = seaborn.catplot(
            data=self._as_single_dataframe(data),
            x=self.xvar,
            y=self.yvar,
            kind="bar",
            hue=self.gvar if self.gvar else None,
            height=self.height_figure,
            aspect=self.aspect_ratio_figure)
        return Figure(
            graphic.set(
                xlabel=self.xlabel if self.xlabel else self.xvar,
                ylabel=self.ylabel if self.ylabel else self.yvar),
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
