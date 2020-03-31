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
A chart illustrating connection strengths in a network.
Nodes are placed on a circle's periphery, and arcs connect
them with edges whose thickness is proportional to that connection's
strength.
"""
from collections import OrderedDict
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from dmt.tk.field import Field, LambdaField, lazyfield, WithFields
from ...shapes import Geometry, Path, Polygon, PolarPoint, Circle, Arc
from .data import NetworkChart
from .geometries import ChartGeometry, LabelGeometry, NodeGeometry, FlowGeometry

class NodeArcGeometry(NodeGeometry, Polygon):
    """
    Geometry to represent nodes.
    """
    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(
            *args,
            position=PolarPoint(*kwargs.pop("position")),
            size=PolarPoint(*kwargs.pop("size")),
            **kwargs)

    @lazyfield
    def shape(self):
        """
        Shape of this node.
        """
        return PolarPoint(
            radial=(
                self.position.radial - self.size.radial/2.,
                self.position.radial + self.size.radial/2.),
            angular=(
                self.position.angular - self.size.angular/2.,
                self.position.angular + self.size.angular/2.))

    @lazyfield
    def label_location(self):
        """
        Where should the label be located?
        """
        radial_position =\
            1.5 * self.chart.outer_circle.radius
        return PolarPoint(
            radial_position,
            self.position.angular)

    @lazyfield
    def label_rotation(self):
        """
        How rotated should the label be?
        """
        #return 0.
        if self.position.angular < np.pi:
            return np.pi/2. - self.position.angular
        angle = 3.*np.pi/2. - self.position.angular
        return angle if angle < 0. else 2*np.pi + angle

    @lazyfield
    def sides(self):
        """
        Sides of the polygon that will be plotted.
        """
        #return self.chart.get_sides(self)
        radius = self.shape.radial
        angle = self.shape.angular
        radial_out = Path(
            label=self.label,
            vertices=[
                self.chart.point_at(radius[0], angle[0]),
                self.chart.point_at(radius[1], angle[0])]
        )
        arc_anti_clockwise = Path(
            label=self.label,
            vertices=self.chart.arc(radius[1], angle[0], angle[1])
        )
        radial_in = Path(
            label=self.label,
            vertices=[
                self.chart.point_at(radius[1], angle[1]),
                self.chart.point_at(radius[0], angle[1])]
        )
        arc_clockwise = Path(
            label=self.label,
             vertices=self.chart.arc(radius[0], angle[1], angle[0])
        )
        return [
            radial_out,
            arc_anti_clockwise,
            radial_in,
            arc_clockwise
        ]
    def add_text(self, axes, *args, **kwargs):
        """
        For plotting
        """
        p = self.chart.point_at(
            self.label_location.radial,
            self.label_location.angular)
        axes.text(
            p[0], p[1],
            self.label,
            rotation=180 * self.label_rotation/np.pi,
            fontsize=self.chart.fontsize)


class FlowArcGeometry(ChartGeometry, Polygon):
    """
    Geometry to represent a flow from a begin node to an end node.
    """
    chart = Field(
        """
        The network chart that defines this `NodeGeometry`'s behavior.
        """)
    begin_node = Field(
        """
        A `NodeGeometry` instance where this `FlowGeometry`
        starts.
        """)
    end_node = Field(
        """
        A `NodeGeometry` instance where this `FlowGeometry`
        ends.
        """)
    size_begin = Field(
        """
        Size at beginning.
        """)
    size_end = Field(
        """
        Size at end.
        """)
    label = LambdaField(
        """
        Label can be constructed from nodes.
        """,
        lambda self: (
            self.begin_node.label,
            self.end_node.label))

    @lazyfield
    def size(self):
        return self.size_begin

    @lazyfield
    def identifier(self):
        """
        Identifier can be used as a key in a mapping providing
        features for this `Geometry`.
        """
        return (self.begin_node.identifier, self.end_node.identifier)

    @lazyfield
    def position(self):
        """
        A flow lies between its begin and end nodes.
        """
        return (self.begin_node.position, self.end_node.position)

    @lazyfield
    def sides(self):
        """..."""
        arc_begin = self.chart.get_flow_position(
            self.begin_node, self
        )
        begin_base = Path(
            label=self.label,
            vertices=self.chart.arc(
                self.chart.outer_circle.radius,
                #self.begin_node.shape.radial[0],
                arc_begin[0],
                arc_begin[1])
        )
        if self.begin_node == self.end_node:
            side_forward = Path(
                label=self.label,
                vertices=[
                    self.chart.point_at(
                        self.begin_node.shape.radial[0],
                        arc_begin[1]),
                    self.chart.point_at(
                        self.inner_circle.radius,
                        arc_begin[1])]
            )
            end_base = Path(
                label=self.label,
                vertices=self.chart.arc(
                    self.chart.inner_circle.radius,
                    arc_begin[1],
                    arc_begin[0])
            )
            side_backward = Path(
                label=self.label,
                vertices=[
                    self.chart.point_at(
                        self.chart.inner_circle.radius,
                        self.chart.point_at(
                            self.begin_node.shape.radial[0],
                            arc_begin[0]))]
            )
        else:
            arc_end = self.chart.get_flow_position(
                self.end_node, self
            )
            side_forward = Path(
                label=self.label,
                vertices=self.chart.flow_curve(
                    self.chart.inner_circle.radius,
                    arc_begin[1],
                    arc_end[0])
            )
            end_base = Path(
                label=self.label,
                vertices=self.chart.arc(
                    self.chart.inner_circle.radius,
                    arc_end[0],
                    arc_end[1])
            )
            side_backward = Path(
                label=self.label,
                vertices=self.chart.flow_curve(
                    self.chart.inner_circle.radius,
                    arc_end[1],
                    arc_begin[0])
            )
        return [
            begin_base,
            side_forward,
            end_base,
            side_backward
        ]


    @lazyfield
    def curve(self):
        """
        A curve along the middle of this `FlowGeometry` instance.
        """
        arc_begin =\
            self.chart.get_flow_position(self.begin_node, self)
        angle_begin =\
            (arc_begin[0] + arc_begin[1]) / 2
        if self.begin_node == self.end_node:
            return Path(
                label="{}_curve".format(self.label),
                vertices=[
                    begin_vertex,
                    self.chart.point_at(
                        self.begin_node.shape.radial[0],
                        angle_begin),
                    self.chart.point_at(
                        self.chart.inner_circle.radius,
                        angle_begin)
                ])
        arc_end =\
            self.chart.get_flow_position(self.end_node, self)
        angle_end =\
            (arc_end[0] + arc_end[1]) / 2
        vertices =\
            self.chart.flow_curve(
                self.chart.inner_circle.radius,
                angle_begin,
                angle_end)
        return Path(
            label="{}_curve".format(self.label),
            vertices = vertices)

    def draw(self, axes, *args, **kwargs):
        """
        Draw the `Polygon` associated with this `FlowGeometry` instance,
        and then draw an arrow over it.
        """
        super().draw(*args, **kwargs)
        #self.curve.draw(*args, **kwargs)
        N = len(self.curve.vertices)
        n = -1#np.int32(-0.1 * N)
        #arrow_start = self.curve.vertices[n]
        arc_end =\
            self.chart.get_flow_position(self.end_node, self)
        angle_end =\
            (arc_end[0] + arc_end[1]) / 2
        arrow_start =\
            self.chart.point_at(
                self.end_node.position.radial - self.end_node.size.radial,
                angle_end)
        arrow_direction =\
            self.curve.vertices[n] - self.curve.vertices[n-1]
        arrow_end = arrow_start + arrow_direction
        arrow_direction = arrow_end - arrow_start
        color = self.facecolor
        color[3] = 0.5
        # axes.arrow(
        #     arrow_start[0], arrow_start[1],
        #     arrow_direction[0], arrow_direction[1],
        #     head_width=self.size, head_length=self.end_node.size.radial,
        #     fc=color,
        #     ec="gray")#self.facecolor)
        return axes


class CircularNetworkChart(NetworkChart):
    """
    Illustrate a network's nodes as islands along a circle's periphery,
    and its edges as rivers flowing between these islands.
    """
    NodeGeometryType = Field(
        """
        A callable that returns a node geometry
        """,
        __default_value__=NodeArcGeometry)
    FlowGeometryType = Field(
        """
        A callable that returns a flow geometry
        """,
        __default_value__=FlowArcGeometry)
    center = Field(
        """
        Position on the page where the center of this `Chart` should lie.
        """,
        __default_value__=np.array([0., 0.]))
    rotation = Field(
        """
        The overall angle in radians, by which the chart will be rotated.
        """,
        __default_value__=0.)
    link_data = Field(
        """
        A `pandas.Series` with a double leveled index
        (`begin_node`, 'end_node``), with values providing weights / strengths
        of the links to be displayed as sizes of the flows.
        """)
    size = Field(
        """
        Size of the figure. 
        """,
        __default_value__=12)
    height_figure = LambdaField(
        """
        Height of the figure.
        """,
        lambda self: self.size)
    width_figure = LambdaField(
        """
        Width of the figure.
        """,
        lambda self: self.size)
    radial_size_node = Field(
        """
        Radial size of a node --- will be the same for all nodes.
        """,
        __default_value__=0.1)
    spacing_factor = Field(
        """
        Fraction of space along the periphery that must be left blank, to space
        nodes.
        """,
        __default_value__=0.25)
    unit_node_size = LambdaField(
        """
        Node size will be determined as a multiple of this unit size.
        """,
        lambda self: 2 * np.pi * (1. - self.spacing_factor))
    inner_outer_spacing = LambdaField(
        """
        Spacing from inner to outer circles.
        """,
        lambda self: 1. * self.radial_size_node)
    margin = Field(
        """
        Space (in units of the axes) around the geometries.
        """,
        __default_value__=0.5)
    node_flow_spacing_factor = Field(
        """
        A multiplicative factor ( > 1.) by which flows placed on a node
        geometry must be spaced.
        """,
        __default_value__=1.)
    fontsize = Field(
        """...""",
        __default_value__=24)
    axes_size = Field(
        """
        Axes will be scaled accordingly.
        """,
        __default_value__=1.)
    color_map = Field(
        """
        Colors for the nodes.
        Please a provide a `Mapping`, like a dictionary, or pandas Series
        that maps node labels to the color value with which they should be
        painted.
        """,
        __default_value__={})

    def get_color(self, geometry, **kwargs):
        """
        Get colors for a geometry.
        """
        return self.color_map.get(geometry.identifier, "green")

    @lazyfield
    def outer_circle(self):
        """..."""
        return Circle(
            label="outer-circle",
            radius=self.axes_size)

    @lazyfield
    def inner_circle(self):
        """..."""
        return Circle(
            label="inner-circle",
            radius=self.axes_size - self.inner_outer_spacing)

    @lazyfield
    def node_geometry_size(self):
        """
        Size of the geometry that will represent a node.
        In a pandas series of tuples (radial, angular)
        """
        return self.node_weight.apply(
            lambda weight: (
                pd.Series({
                    "total": (
                        self.radial_size_node,
                        self.unit_node_size* weight.total),
                    "source": (
                        self.radial_size_node,
                        self.unit_node_size*weight.source),
                    "target":(
                        self.radial_size_node,
                        self.unit_node_size*weight.target)})),
            axis=1
        )

    @staticmethod
    def _angular_size(dataframe_size):
        """..."""
        try:
            return dataframe_size.apply(
                lambda row: pd.Series(dict(
                    total=row.total[1],
                    source=row.source[1],
                    target=row.target[1])),
                axis=1
            )
        except AttributeError:
            return dataframe_size.apply(
                lambda row: pd.Series(dict(
                    source=row.source[1],
                    target=row.target[1])),
                axis=1
            )
        raise RuntimeError(
            "Execution of _angular_size(...) should not reach here."
        )
    @lazyfield
    def node_angular_size(self):
        """..."""
        return self._angular_size(self.node_geometry_size)

    @lazyfield
    def node_position(self):
        """
        Positions where the nodes will be displayed.
        """
        number_nodes = self.node_weight.shape[0]
        spacing = 2. * np.pi * self.spacing_factor / number_nodes

        def _positions_angular():
            position_end = - spacing
            for size in self.node_geometry_size.total.values:
                position_start = position_end + spacing
                position_end = position_start + size[1]
                yield (position_start + position_end) / 2.

        positions_angular = pd.Series(
            list(_positions_angular()),
            index=self.node_geometry_size.index,
            name="angular"
        )
        starts_source = (
            positions_angular - self.node_angular_size.total / 2.
        ).rename(
            "start_source"
        )
        positions_angular_source = (
            starts_source + self.node_angular_size.source / 2.
        ).rename(
            "angular"
        )
        positions_source = positions_angular_source.apply(
            lambda position_angular: (
                self.outer_circle.radius, position_angular)
        )
        starts_target = (
            positions_angular_source + self.node_angular_size.source / 2.
        ).rename(
            "start_target"
        )
        positions_angular_target = (
            starts_target + self.node_angular_size.target / 2.
        ).rename(
            "angular"
        )
        positions_target = positions_angular_target.apply(
            lambda position_angular: (
                self.inner_circle.radius, position_angular)
        )
        return pd.concat(
            [positions_source, positions_target],
            axis=1,
            keys=["source", "target"]
        )
    def point_at(self,
            radius,
            angle):
        """..."""
        return self.center + np.array([
            radius * np.sin(angle + self.rotation),
            radius * np.cos(angle + self.rotation)])

    def arc(self,
            radius,
            angle_begin,
            angle_end,
            label=""):
        """..."""
        if not label:
            label = "{}---{}".format(angle_begin, angle_end)
        return Arc(
            label=label,
            center=self.center,
            radius=radius,
            rotation=self.rotation,
            angle_begin=angle_begin,
            angle_end=angle_end
        ).points()

    def flow_curve(self,
            radius,
            angle_begin,
            angle_end,
            label=""):
        """
        Curve of a flow.
        """
        angle_mean =\
            (angle_begin + angle_end) / 2.
        angle_min =\
            np.minimum(angle_begin, angle_end)
        angle_off =\
            angle_mean - angle_min
        angle_center =\
            np.pi - 2 * angle_off
        angle_rotation =\
            np.pi / 2. - angle_min
        length =\
            radius / np.cos(angle_off)
        radius_arc =\
            radius * np.tan(angle_off)
        center_arc =\
            self.center + np.array([
                length * np.sin(angle_mean + self.rotation),
                length * np.cos(angle_mean + self.rotation)])
        if not label:
            label = "{}==>{}".format(angle_begin, angle_end)
        rotation =\
            self.rotation - angle_rotation\
            if angle_begin < angle_end else\
               self.rotation - angle_rotation - angle_center
        angle_end =\
            -angle_center\
            if angle_begin < angle_end else\
               angle_center
        return Arc(
            label=label,
            center=center_arc,
            radius=radius_arc,
            rotation=rotation,
            angle_begin=0.,
            angle_end=angle_end
        ).points()

    def get_flow_position(self, node_geometry, flow_geometry):
        """
        Where should flow geometry be situated on node geometry.
        """
        assert node_geometry in (
            flow_geometry.begin_node, flow_geometry.end_node),\
            "{} not in ({}, {})".format(
                node_geometry.label,
                flow_geometry.begin_node.label,
                flow_geometry.end_node.label)
        flow_size =\
            flow_geometry.size_end\
            if node_geometry == flow_geometry.end_node else\
               flow_geometry.size_begin
        spaced =\
            lambda pos: self.node_flow_spacing_factor * pos
        start =\
            spaced(
                node_geometry.position.angular - node_geometry.size.angular / 2)
        if not node_geometry.flow_positions:
            position = (start, start + flow_size)
            node_geometry.flow_positions.append((flow_geometry, position))
        else:
            for geometry, position in node_geometry.flow_positions:
                if geometry == flow_geometry:
                    return position
            start = spaced(position[1])
            position = (start, start + flow_size)
            node_geometry.flow_positions.append((flow_geometry, position))

        return position

    @lazyfield
    def flow_geometry_size(self):
        """..."""
        def _flow_sizes(node_type):
            """..."""
            assert node_type in ("source", "target")
            if node_type == "source":
                nodes = self.link_data.index.get_level_values("begin_node")
                return self.node_angular_size.source.loc[nodes].values * (
                    self.link_data / self.node_flow.outgoing.loc[nodes].values
                ).rename(
                    "begin"
                )
            else:
                nodes = self.link_data.index.get_level_values("end_node")
                return self.node_angular_size.target.loc[nodes].values * (
                    self.link_data / self.node_flow.incoming.loc[nodes].values
                ).rename(
                    "end"
                )
            raise RuntimeError(
                "Execution of `flow_data(...)` should not have reached here."
            )
        return pd.concat(
            [_flow_sizes("source"), _flow_sizes("target")],
            axis=1
        )
    def draw(self, draw_diagonal=True, *args, **kwargs):
        """
        Draw this `Chart`.
        """
        figure = plt.figure(figsize=(self.size, self.size))
        axes = plt.gca()
        s = self.axes_size + self.margin
        axes.set(xlim=(-s, s), ylim=(-s, s))
        self.outer_circle.draw(*args, **kwargs)
        self.inner_circle.draw(*args, **kwargs)
        for node_geometry in self.source_geometries.values():
            node_geometry.draw(axes, *args, **kwargs)
            #node_geometry.add_text(axes, *args, **kwargs)
        for node_geometry in self.target_geometries.values():
            node_geometry.draw(axes, *args, **kwargs)
            #node_geometry.add_text(axes, *args, **kwargs)
        for flow_geometry in self.flow_geometries.values():
            if (flow_geometry.begin_node == flow_geometry.end_node
                and not draw_diagonal):
                continue
            flow_geometry.draw(axes, *args, **kwargs)

        # Circle(label="study", radius=1.5).draw()
