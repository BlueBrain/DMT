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

from collections import OrderedDict
import numpy as np
import pandas as pd
from matplotlib import pylab as plt
from dmt.tk.field import Field, LambdaField, lazyfield, WithFields
from ...shapes import PolarPoint, Polygon, Path, Circle, Arc
from ...figure import Figure
from .circle import CircularNetworkChart


class NetworkChartPlot(WithFields):
    """
    A chart that will display network properties.
    """
    chart_type = Field(
        """
        A callable that takes a network's link-weight data, and a color map to 
        generate a chart for the input network data.
        """,
        __default_value__=CircularNetworkChart)
    title = Field(
        """
        Title to be displayed.
        """,
        __default_value__="Network Flows.")
    node_variable = Field(
        """
        Name of the variable associated with the nodes.
        For example, a brain-circuit's connectome data may have an index
        with columns `pre_mtype` and `post_mtype`, in which case the
        `node_variable` must be set to 'mtype'.
        """,
        __examples__=["mtype"])
    source_variable = LambdaField(
        """
        Variable providing values of the beginning node of an edge.
        """,
        lambda self: "pre_{}".format(self.node_variable))
    target_variable = LambdaField(
        """
        Variable providing values of the ending node of an edge
        """,
        lambda self: "post_{}".format(self.node_variable))
    node_type = Field(
        """
        Data-type of the values of nodes provided in the input dataframe.
        """)
    phenomenon = Field(
        """
        Variable providing the phenomenon whose value will be plotted as
        edge flows.
        """)
    color_map = Field(
        """
        Color for geometries that will be draw in the chart.
        Colors will be accessed by geometry identifiers.
        """,
        __default_value__={})

    def chart(self, dataframe):
        """..."""
        try:
            weights = dataframe[(self.phenomenon, "mean")].values
        except KeyError:
            weights = dataframe[self.phenomenon].values

        new_index_name = {
            self.source_variable: "begin_node",
            self.target_variable: "end_node"
        }
        link_weights = pd.Series(
            weights,
            index=dataframe.index.rename([
                new_index_name[name] for name in dataframe.index.names]),
            name="weight"
        )
        return self.chart_type(
            link_data=link_weights,
            color_map=self.color_map)

    def get_figure(self,
            dataframe,
            *args,
            caption="Caption not provided",
            **kwargs):
        """
        Plot the data.

        Arguments
        -----------
        dataframe :: <source_variable, source_variable, phenomenon>
        """
        chart = self.chart(dataframe)
        return Figure(
            chart.draw(*args, **kwargs),
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
            dataframe,
            *args, **kwargs):
        """
        Make this class a callable,
        so that it can masquerade as a function!
        """
        return self.plot(dataframe, *args, **kwargs)
