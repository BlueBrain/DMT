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
Utility Mixins to handle network data.
"""
from abc import abstractmethod, abstractproperty
from collections import OrderedDict
import pandas as pd
from dmt.tk.field import Field, LambdaField, lazyfield, WithFields

class NetworkChart(WithFields):
    """
    A mixin that computes data required to plot a network chart.
    """
    NodeGeometryType = Field(
        """
        A callable that returns a node geometry
        """)
    FlowGeometryType = Field(
        """
        A callable that returns a flow geometry
        """)
    link_data = Field(
        """
        A `pandas.Series` with a double leveled index <`begin_node`, `end_node`>,
        with values providing weights / strengths of the links to be displayed
        as sizes of the flows.
        """)
    unit_node_size = Field(
        """
        Node size will be determined as a multiple of this unit size.
        """)
    @abstractmethod
    def get_internode_spacing(self, number_nodes):
        """
        Spacing between nodes, given their number.
        """
        raise NotImplementedError

    @lazyfield
    def node_flow(self):
        """
        Transform `self.link_data` to data required to plot nodes.
        """
        outgoing = self.link_data.groupby(
                "begin_node"
            ).agg(
                "sum"
            ).rename(
                "outgoing"
            )
        incoming = self.link_data.groupby(
                "end_node"
            ).agg(
                "sum"
            ).rename(
                "incoming"
            )
        assert all(
            x == y for x, y in zip(
                outgoing.index.values,
                incoming.index.values)
        ), """
        out {}
        in {}
        """.format(
                outgoing.index.values,
                incoming.index.values
        )

        total = (
            outgoing + incoming
        ).rename(
            "total"
        )
        return pd.concat(
            [outgoing, incoming, total],
            axis=1
        )
    @lazyfield
    def node_weight(self):
        """
        Compute weight of a node from it's in and out flows.
        A node's weight calculated here will determine it's plotted
        position and size.
        """
        number_nodes = self.node_flow.shape[0]
        total_out_flow = self.node_flow.outgoing.sum()
        total_in_flow = self.node_flow.incoming.sum()
        total_flow = total_out_flow + total_in_flow

        weights = (
            (self.node_flow.incoming + self.node_flow.outgoing)/ total_flow
        ).apply(
            lambda weight: weight 
        ).rename(
            "total"
        )
        weights_source = (
            weights * (self.node_flow.outgoing / self.node_flow.total)
        ).rename(
            "source"
        )
        weights_target = (
            weights * (self.node_flow.incoming / self.node_flow.total)
        ).rename(
            "target"
        )
        return pd.concat(
            [weights, weights_source, weights_target],
            axis=1,
            keys=["total", "source", "target"]
        )
    @lazyfield
    def flow_weight(self):
        """
        Data for connection flows.
        """
        return (
            self.link_data / self.link_data.sum()
        ).rename(
            "weight"
        )

    @abstractproperty
    def node_position(self):
        """
        The concrete network chart plotter should provide a dataframe for
        node positions.
        """
        raise NotImplementedError

    @lazyfield
    def node_data(self):
        """All of node data..."""
        return pd.concat(
            [self.node_position, self.node_geometry_size,
             self.node_weight, self.node_flow],
            axis=1,
            keys=["position", "geometry_size", "weight", "flow"]
        )
    def get_source_geometry(self,
                label,
                node_data):
        """..."""
        return self.NodeGeometryType(
            chart=self,
            label=label,
            position=node_data.position.source,
            size=node_data.geometry_size.source,
            flow_weight=node_data.flow.outgoing
        )
    @lazyfield
    def source_geometries(self):
        """
        Where do flows start?
        """
        return OrderedDict([
            (label, self.get_source_geometry(label, node))
            for label, node in self.node_data.iterrows()])

    def get_target_geometry(self,
                label,
                node_data):
        """..."""
        return self.NodeGeometryType(
            chart=self,
            label=label,
            position=node_data.position.target,
            size=node_data.geometry_size.target,
            flow_weight=node_data.flow.incoming
        )
    @lazyfield
    def target_geometries(self):
        """
        Where do flows stop?
        """
        return OrderedDict([
            (label, self.get_target_geometry(label, node))
            for label, node in self.node_data.iterrows()])

    @lazyfield
    def flow_data(self):
        """..."""
        return pd.concat(
            [self.flow_weight, self.flow_geometry_size],
            axis=1
        )
    def get_flow_geometry(self,
            begin_node_label,
            end_node_label,
            flow_size):
        """..."""
        return self.FlowGeometryType(
            chart=self,
            begin_node=self.source_geometries[begin_node_label],
            end_node=self.target_geometries[end_node_label],
            size_begin=flow_size.begin,
            size_end=flow_size.end
        )
    @lazyfield
    def flow_geometries(self):
        """
        Convert data to link geometries.
        """
        return OrderedDict([
            ((begin_node, end_node),
             self.get_flow_geometry(begin_node, end_node, flow))
            for (begin_node, end_node), flow in self.flow_data.iterrows()])

