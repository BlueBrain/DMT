# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Plot heat maps.
"""
from collections.abc import Mapping
import pandas
import matplotlib.pyplot as plt
import seaborn
from dmt.tk.plotting.utils import pivot_table
from dmt.tk.field import Field, LambdaField
from dmt.data.observation import measurement
from dmt.tk import terminology
from . import golden_aspect_ratio
from .figure import Figure
from .import BasePlotter

class HeatMap(BasePlotter):
    """
    Define the requirements and behavior of a heatmap.
    """
    measurement_type = Field(
        """
        Will this instance of `HeatMap` be called with a measurement type that
        will be a statistical summary or statistical samples?
        Heat map cannot be generated for samples. If measurement type is a
        samples, a summary will be made before plotting.
        """,
        __default_value__=terminology.measurement_type.summary)
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
    phenomenon = LambdaField(
        """
        Phenomenon whose measurement is plotted as a heatmap.
        """,
        lambda self: self.vvar)
    title = LambdaField(
        """
        Title for this plots.
        """,
        lambda self: self.vvar)
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
    adjustments_plt = Field(
        """
        A function that will make adjustments to the plot.
        """,
        __default_value__=lambda *args, **kwargs: None)

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

    def _get_dataframe_default(self, data):
        """..."""
        if not isinstance(data, (pandas.Series, pandas.DataFrame)):
            assert isinstance(data, Mapping) and len(data) == 1,\
                """
                Cannot decide which one to plot among more than one dataset:
                \t{}
                """.format(list(data.keys()))
            dataframe = list(data.values())[0]
            if self.measurement_type != terminology.measurement_type.summary:
                dataframe = measurement.get_summary(dataframe)
        else:
            dataframe = data
        if (
                not isinstance(dataframe.columns, pandas.MultiIndex)
                and not isinstance(dataframe.index, pandas.MultiIndex)
        ):
            return dataframe.reset_index()

        dataframe = dataframe.reset_index()
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
        matrix =\
            pandas.pivot(self.get_dataframe(data),
                         values=self._flattened(self.vvar),
                         index=self._flattened(self.xvar),
                         columns=self._flattened(self.yvar))\
                  .fillna(self.fill_missing_value)
        with seaborn.plotting_context(self.context,
                                      font_scale=self.font_scale,
                                      rc=self.rc_params()):
            #fig, ax = plt.subplots(figsize=(12, 12))
            self.adjustments_plt()
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
            plt.title(' '.join(w.capitalize() for w in self.title.split('_')))
            return Figure(
                graphic,
                caption=caption)
        return None
