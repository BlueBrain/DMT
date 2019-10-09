from collections import OrderedDict
import numpy as np
import pandas as pd
from matplotlib import pylab as plt
from dmt.tk.field import Field, LambdaField, lazyfield, WithFields
from ...shapes import PolarPoint, Polygon, Path, Circle, Arc
from ...figure import Figure
from .circle import CircularNetworkChart

class Network(WithFields):
    """
    A chart that will display network properties.
    """
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
    pre_variable = LambdaField(
        """
        Variable providing values of the beginning node of an edge.
        """,
        lambda self: "pre_{}".format(self.node_variable))
    post_variable = LambdaField(
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

        link_weights = pd.Series(
            weights,
            index=dataframe.index.rename(["begin_node", "end_node"]),
            name="weight")


        return CircularNetworkChart(
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
        dataframe :: <pre_variable, post_variable, phenomenon>
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
