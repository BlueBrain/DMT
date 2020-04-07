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
PLot lines.
"""
import pandas
import matplotlib.pyplot as plt
import seaborn
from dmt.tk.utils.string_utils import make_name
from dmt.tk.field import Field, LambdaField, lazyfield
from dmt.data.observation import measurement
from . import golden_aspect_ratio
from  .import BasePlotter
from .figure import Figure


class LinePlot(BasePlotter):
    """
    Define the requirements and behavior of a line plot.
    """
    labels_xticks = Field(
        """
        Point type to be plotted.
        """,
        __default_value__="")
    gvar_order = Field(
        """
        An order on group variables, 
        """,
        __default_value__=[])
    gvar_kwargs = Field(
        """
        Customize plotting of group variable data.
        """,
        __default_value__={})
    drawstyle = Field(
        """
        Specify how to draw the lines that join the (x, y) points.
        Default value join the points with simple points. Other possibilities
        are steps.
        """,
        __default_value__="default")
    marker_size = Field(
        """
        Size of the markers.
        """,
        __default_value__=10)

    def get_dataframe(self, data, dataset=None):
        """
        Extract the dataframe to plot.
        """
        if dataset:
            raise NotImplementedError(
            """
                `LinePLot.get_figure(...)` current version does not support
                argument `dataset`.
                """)
        if isinstance(data, (pandas.Series, pandas.DataFrame)):
            return data.reset_index()
        return measurement.concat_as_samples(data).reset_index()

    @staticmethod
    def _get_markers(series, filled=True):
        """
        Get markers for elements in a series...
        """
        markers_filled =[
            "o", "v", "^", "<", ">",  "8", "s", "p", "P", "*",
            "X", "d", "D",  "h", "H"]
        markers_unfilled =[
            "o", "v", "^", "<", ">",  "8", "s", "p", "P", "*",
            "X", "d", "D",  "h", "H"]
        markers_to_use =\
            markers_filled if filled else markers_unfilled
        return {
            value: markers_to_use[index % len(markers_to_use)]
            for index, value in series.iteritems()}

    def get_figure(self,
            data,
            *args,
            dataset=None,
            caption="Caption not provided",
            title=None,
            **kwargs):
        """
        Plot the data.

        Arguments
        -------------
        data : Either a dataframe or a dict mapping dataset to dataframe.
        dataset : dataset or list of dataset names whose data will be plotted.
        """
        def _make_name(label):
            return make_name(
                '_'.join(label) if isinstance(label, tuple) else label,
                separator='_')
        dataframe =\
            self.get_dataframe(data, dataset)
        #if self.fvar:
        grid = seaborn\
            .FacetGrid(
                dataframe,
                col=self.fvar if self.fvar else None,
                hue=self.gvar if self.gvar else None,
                hue_order=self.gvar_order if self.gvar_order else None,
                hue_kws=self.gvar_kwargs if self.gvar_kwargs else None,
                col_wrap=self.number_columns,
                height=self.height_figure,
                aspect=self.aspect_ratio_figure,
                legend_out=True)
        grid.map(
            seaborn.lineplot,
            self.xvar,
            self.yvar,
            drawstyle=self.drawstyle,
            alpha=0.7,
            dashes=False,
            hue=dataframe[self.gvar] if self.gvar else None,
            style=dataframe[self.gvar] if self.gvar else None,
            markers=self._get_markers(dataframe[self.gvar]) if self.gvar else None,
            ms=self.marker_size
        ).set_titles(
            _make_name(self.fvar) + "\n{col_name} "
        ).add_legend(
            title=_make_name(self.gvar))
        return Figure(
            grid.set(
                xlabel=self.xlabel,
                ylabel=self.ylabel,
                title=self.title if title is None else title),
            caption=caption)

    def plot(self,
            *args, **kwargs):
        """
        Plot the data

        Arguments
        -----------
        data : A dict mapping dataset to dataframe.
        """
        return self.get_figure(*args, **kwargs)

