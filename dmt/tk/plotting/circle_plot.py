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
Make a circle plot.
"""
"""
Plot heat maps.

"""
from collections import OrderedDict
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt 
from . import golden_aspect_ratio
from dmt.tk.plotting.utils import pivot_table
from dmt.tk.field import Field, LambdaField, lazyfield, WithFields
from .shapes import PolarPoint, Polygon, Path, Circle, Arc
from .figure import Figure


class FlowGeom(Polygon):
    """
    A `FlowGeom` is a geometric representation of a flow from
    a begin node to end node.
    """
    angular_thickness = Field(
        """
        Thickness of the flow, measured in radians
        """,
        __default_value__=0.05)
    network_geom = Field(
        """
        An object that will produce sides of the polygon to be
        drawn for this `FlowGeom`.
        """)
    begin_node_geom = Field(
        """
        The node geometry where this flow begins.
        """)
    end_node_geom = Field(
        """
        The node geometry where this flow ends.
        """)

    @lazyfield
    def sides(self):
        """
        Sides of this flow.
        """
        return self.network_geom.get_sides(self)


class NodeGeom(Polygon):
    """
    Geometry to represent nodes.
    Nodes will be placed on the circumference of a circle.
    """
    network_geom = Field(
        """
        The network geometry that controls this `NodeGeom`.
        """)
    position = Field(
        """
        Position of this node --- type should be determined by
        the network geometry object.
        """)
    thickness = Field(
        """
        Thickness of this node --- type should be the same as position.
        """)

    @lazyfield
    def sides(self):
        """
        Sides to determine where this node geometry should be placed.
        """
        return self.network_geom.get_sides(self)


class NetworkGeom(Circle):
    """
    The circle that will be plotted
    """
    spacing_nodes = Field(
        """
        A fraction indicating how much blank space to leave between
        nodes.
        """,
        __default_value__=0.25)
    


    def _get_thickness_node(self, node):
        """..."""
        return PolarPoint(0.1, node.angular_size)

    def spawn_nodes(self, data):
        """
        Create the nodes.
        """
        node_weights = self.get_node_weights(data)
        assert np.isclose(node_weights.sum(), 1.),\
            "Not normalized: {}".format(node_weights)
        number_nodes =\
            node_weights.shape[0]
        spacing =\
            self.spacing_nodes * 2. * np.pi / number_nodes
        node_sizes =\
            node_weights.apply(
                lambda w: (1. - self.spacing_nodes) * 2. * np.pi * w)
        node_positions = pd.Series(
            np.cumsum([
                node_size + spacing
                for node_size, spacing in zip(
                        node_sizes, number_nodes * [spacing])]),
            index=node_weights.index)
        nodes = pd.DataFrame(dict(
            weight=node_weights,
            angular_size=node_sizes,
            angular_position=node_positions))
        self.node_geoms = OrderedDict([
            (label, self.get_child_geom(label, node))
            for label, node in nodes.iterrows()])
        self.children.extend(self.node_geoms.values())
        return self.node_geoms

    def spawn_flows(self, link_weights):
        """..."""
        self.flow_geoms = OrderedDict([
            ((begin, end), self.get_child_geom(begin, end, link))
            for (begin, end), link in link_weights.iterrows()])
        self.children.extend(self.flow_geoms)
        return self.flow_geoms

    def arc_flow(self, angle_begin, angle_end, label="", radius=None):
        """..."""
        if radius is None:
            radius = self.radius
        angle_mean = (angle_begin + angle_end) / 2.
        angle_min = np.minimum(angle_begin, angle_end)
        angle_off = angle_mean - angle_min
        angle_center = np.pi - 2 * angle_off
        angle_rotation = np.pi / 2 - angle_min
        length = radius / np.cos(angle_off)
        radius_arc = radius * np.tan(angle_off);
        center_arc = self.center + np.array([
            length * np.sin(angle_mean + self.rotation),
            length * np.cos(angle_mean + self.rotation)])
 
        if not label:
            label = "Flow {}==>{}".format(angle_begin, angle_end)
        if angle_begin < angle_end:
            return Arc(
                label=label,
                center=center_arc,
                radius=radius_arc,
                rotation=self.rotation - angle_rotation,
                angle_begin=0.,
                angle_end=-angle_center)
        return Arc(
            label=label,
            center=center_arc,
            radius=radius_arc,
            rotation=self.rotation - angle_rotation - angle_center,
            angle_begin=0.,
            angle_end=angle_center)

    def _get_flow_geom(self,
            begin_node_label,
            end_node_label,
            flow_data):
        """..."""
        return FlowGeom(
            label="{}==>{}".format(begin_node_label, end_node_label),
            angular_thickness=flow_data.weight,
            begin_node_geom=self.children[begin_node_label],
            end_node_geom=self.children[end_node_label],
            network_geom=self)

    def _get_node_geom(self,
            label, node_data):
        """..."""
        return NodeGeom(
            label=label,
            position=PolarPoint(self.radius, node_data.angular_position),
            thickness=PolarPoint(0.1, node_data.angular_size),
            network_geom=self)

    def get_child_geom(self, *args):
        """
        Get a geometry corresponding to  geom_data.
        """
        try:
            return self._get_node_geom(*args) 
        except (AttributeError, TypeError) as error_node:
            try:
                return self._get_flow_geom(*args)
            except (AttributeError, TypeError) as error_flow:
                raise TypeError(
                    """
                    Cannot resolve geometry data:
                    \t{}.
                    {}
                    {}
                    """.format(
                        args,
                        error_node,
                        error_flow))


    def _get_sides_flow(self, flow):
        """
        Sides of a flow.
        """
        theta =\
          flow.angular_thickness / 2.
        arc_begin =(
            flow.begin_node_geom.position.angular - theta,
            flow.begin_node_geom.position.angular + theta)
        arc_end =(
            flow.end_node_geom.position.angular - theta,
            flow.end_node_geom.position.angular + theta)
        begin_base =\
            Path(label="{}_begin".format(flow.label),
                 vertices=self.arc(*arc_begin).points())
        side_forward =\
            Path(label="{}_side_forward".format(flow.label),
                 vertices=self.arc_flow(arc_begin[1], arc_end[0]).points())
        end_base =\
            Path(label="{}_end".format(flow.label),
                 vertices=self.arc(*arc_end).points())
        side_backward =\
            Path(label="{}_side_backward".format(flow.label),
                 vertices=self.arc_flow(arc_end[1], arc_begin[0]).points())
        return [
            begin_base,
            side_forward,
            end_base,
            side_backward]

    def _get_sides_node(self, node):
        """
        Sides of a node.
        """
        radius =(
            node.position.radial - node.thickness.radial/2.,
            node.position.radial + node.thickness.radial/2.)
        angle =(
            node.position.angular - node.thickness.angular/2.,
            node.position.angular + node.thickness.angular/2.)

        radial_out =\
            Path(label="{}_radial_out".format(node.label),
                 vertices=[
                     self.point_at(PolarPoint(radius[0], angle[0])),
                     self.point_at(PolarPoint(radius[1], angle[0]))])
        arc_anti_clockwise =\
            Path(label="{}_arc_anti_clockwise".format(node.label),
                 vertices=self.arc(*angle, radius=radius[1]).points())
        radial_in =\
            Path(label="{}_radial_in".format(node.label),
                 vertices=[
                     self.point_at(PolarPoint(radius[1], angle[1])),
                     self.point_at(PolarPoint(radius[0], angle[1]))])
        arc_clockwise =\
            Path(label="{}_arc_clockwise".format(node.label),
                 vertices=self.arc(angle[1], angle[0], radius=radius[0]).points())
        return [
            radial_out,
            arc_anti_clockwise,
            radial_in,
            arc_clockwise]

    def get_sides(self, sub_geom):
        """
        Get sides for a polygonish geometry controlled by this geometry.
        """
        try:
            return self._get_sides_flow(sub_geom)
        except (AttributeError, TypeError) as error_flow:
            try:
                return self._get_sides_node(sub_geom)
            except (AttributeError, TypeError) as error_node:
                raise TypeError(
                    """
                    Unknown sub-geometry type:
                    \t{}.
                    {}
                    {}
                    """.format(
                        type(sub_geom),
                        error_flow,
                        error_node))

    def get_node_weights(self, data):
        raise NotImplementedError

    def draw(self, data):
        """
        Draw the data.
        """
        self.spawn_nodes(data)


class NetworkFlows(WithFields):
    """
    Illustrate the strength of links in a network as flows.
    """
    title = Field(
        """
        Title to be displayed.
        If not provided, phenomenon for the data will be used.
        """,
        __default_value__="")
    node_variable = Field(
        """
        Name of the variable (i.e. column name) for the nodes.
        """,
        __examples__=["mtype"])
    pre_variable = LambdaField(
        """
        Variable (i.e. column name) providing values of the pre-nodes.
        """,
        lambda self: "pre_{}".format(self.node_variable))
    post_variable = LambdaField(
        """
        Variable (i.e. column name) providing values of the post-nodes.
        """,
        lambda self: "post_{}".format(self.node_variable))
    node_type = Field(
        """
        Type of node values.
        """,
        __default_value__=str)
    phenomenon = Field(
        """
        Variable (i.e. column name) providing the phenomenon whose value will
        be plotted as flows.
        """)

    @property
    def dataframe(self):
        """..."""
        try:
            return self._dataframe
        except AttributeError:
            self._dataframe = None
        return self._dataframe

    @dataframe.setter
    def dataframe(self, dataframe):
        """Interpret dataframe as a geometric data."""
        dataframe = dataframe.reset_index()
        try:
            weight = dataframe[self.phenomenon]["mean"].values
        except KeyError:
            weight = dataframe[self.phenomenon].values

        self._dataframe =\
            pd.DataFrame({
                "begin_node": dataframe[self.pre_variable].values,
                "end_node": dataframe[self.post_variable].values,
                "weight": weight})

    @lazyfield
    def network_geom(self):
        """
        Geometry to hold the graphic.
        """
        return NetworkGeom(label=self.title)

    def _norm_efferent(self,
            dataframe,
            aggregator="sum"):
        """
        Efferent value is the exiting value.
        """
        efferent_values =\
            dataframe.groupby(self.pre_variable)\
                     .agg(aggregator)
        efferent_values.index.name = self.node_variable
        return efferent_values

    def _norm_afferent(self,
            dataframe,
            aggregator="sum"):
        """
        Afferent value is the entering value.
        """
        afferent_values =\
            dataframe.groupby(self.post_variable)\
                     .agg(aggregator)
        afferent_values.index.name = self.node_variable
        return afferent_values

    @lazyfield
    def node_weights(self):
        """..."""
        assert self.dataframe is not None
        weights =\
            self.dataframe\
                .groupby(self.pre_variable)\
                [[self.phenomenon]]\
                .agg("sum")
        weights.index.name = "label"
        weights.name = "weight"
        return weights / np.sum(weights)

    @lazyfield
    def link_weights(self):
        """..."""
        try:
            weight = self.dataframe[self.phenomenon]["mean"].values
        except KeyError:
            weight = self.dataframe[self.phenomenon].values

        begin_nodes = self.dataframe[self.pre_variable].values
        end_nodes = self.dataframe[self.post_variable].values
        return\
            pd.DataFrame(dict(
                begin_node=begin_nodes,
                end_node=end_nodes,
                weight=weight/self.node_weights[begin_nodes].values))\
              .set_index(["begin_node", "end_node"])

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
        self.dataframe = dataframe
        
        network_geom = NetworkGeom.draw(self.dataframe)
        assert self.pre_variable in self.dataframe.columns,\
            "{} not in {}".format(
                self.pre_variable,
                self.dataframe.columns)
        assert self.post_variable in self.dataframe.columns,\
            "{} not in {}".format(
                self.post_variable,
                self.dataframe.columns)
        pre_nodes = set(
            self.dataframe[
                self.pre_variable
            ].astype(self.node_type))
        post_nodes = set(
            self.dataframe[
                self.post_variable
            ].astype(self.node_type))
        all_nodes =\
            pre_nodes.union(post_nodes)

        self.network_geom.spawn_nodes(self.node_weights)
        self.network_geom.spawn_flows(self.link_weights)



