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
Generic geometry types that are used by network charts.
"""

from collections import OrderedDict
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dmt.tk.field import Field, LambdaField, lazyfield, WithFields
from ...shapes import Geometry, Path, Polygon, PolarPoint, Circle, Arc

class ChartGeometry:
    """
    List of attributes that can be mixed into a `Geometry` to get an object
    that can be used specifically as a `Chart`'s `Geometry`
    """
    chart = Field(
        """
        The chart object that defines this `NodeGeometry`'s behavior.
        """)
    label = Field(
        """
        A string label to track this `ChartGeometry` instance.
        """)
    size = Field(
        """
        Size of this `ChartGeometry` --- with data-type determined by its
        owning `self.chart`.
        """)
    position = Field(
        """
        Position of this `ChartGeometry` --- with data-type determined by its
        owning `self.chart`.
        """)
    facecolor = LambdaField(
        """
        Color for this `ChartGeometry`'s face.
        You may provide a value, otherwise this `ChartGeometry` instance will
        query it's owning `self.chart`.
        """,
        lambda self: self.chart.get_color(self))

    def __hash__(self):
        """
        A hash for this `ChartGeometry` instance will be used as a key in
        mappings.
        """
        return hash(self.label)


class LabelGeometry(WithFields):
    """
    A helper class to handle a label for a geometry
    """
    location = Field(
        """
        Location in the chart plot where the label for this `NodeGeometry` will
        be written.
        """)
    rotation = Field(
        """
        Angle with which to rotate a label annotation in the chart plot.
        """,
        __default_value__=0)


class NodeGeometry(ChartGeometry, Polygon):
    """
    Geometries to represent nodes.
    """
    flow_weight = Field(
        """
        Total weight of connections to or from this `NodeGeometry`, measured in
        units of link weight.
        """)
    flow_positions = Field(
        """
        Position inside the plotted shape of this `NodeGeometry` instance where
        a flows should start or stop.
        """,
        __default_value__=[])
    
    shape = Field(
        """
        Shape defining how this node will be plotted.
        """)
        

class FlowGeometry(ChartGeometry):
    """
    Geometry to represent a connection from a begin node to an end node as a
    flow.
    """
    begin_node = Field(
        """
        The `NodeGeometry` instance where this `FlowGeometry` instance starts.
        """)
    end_node = Field(
        """
        The `NodeGeometry` instance where this `FlowGeometry` instance ends.
        """)
    size_begin = Field(
        """
        Size of this `FlowGeometry` where it starts.
        """)
    size_end = Field(
        """
        Size of this `FlowGeometry` where it ends.
        """)
    label = LambdaField(
        """
        Label for this `FlowGeometry` is constructed  from it's `begin_node` and
        `end_node`. A custom value may be provided at initialization.
        """,
        lambda self: "({},{})".format(
            self.begin_node.label,
            self.end_node.label))

    @lazyfield
    def size(self):
        """..."""
        return self.size_begin

    @lazyfield
    def identifier(self):
        """
        Identifier can be used as a key in a mapping providing features of this
        `Geometry`.
        """
        return (self.begin_node.identifier, self.end_node.identifier)

    @lazyfield
    def position(self):
        """
        Position of a flow in the chart.
        """
        return (self.begin_node.position, self.end_node.position)


