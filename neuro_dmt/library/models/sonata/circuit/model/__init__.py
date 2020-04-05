# Copyright (c) 2019, EPFL/Blue Brain Project

# This file is part of BlueBrain SNAP library <https://github.com/BlueBrain/snap>

# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published
# by the Free Software Foundation.

# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.

# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""
Circuit models implementing SONATA
"""

import os
from copy import deepcopy
from collections.abc import Iterable
import yaml
import numpy as np
import pandas as pd
import neurom
from bluepysnap.circuit import Circuit as SnapCircuit
from bluepysnap.exceptions import BluepySnapError
from bluepy.exceptions import BluePyError
from bluepy.v2.enums import Cell, Segment, Section
from dmt.tk import collections
from dmt.tk.field import NA, Field, lazyfield, WithFields
from dmt.tk.journal import Logger
from dmt.tk.collections import take
from neuro_dmt import terminology
from neuro_dmt.analysis.reporting import CircuitProvenance
from .cell_type import CellType
from .pathway import PathwaySummary

X = terminology.bluebrain.cell.x
Y = terminology.bluebrain.cell.y
Z = terminology.bluebrain.cell.z
XYZ = [X, Y, Z]

LOGGER = Logger(client=__file__)

NA = "not-available"

def _get_bounding_box(region_of_interest):
    """
    Extract the bounding box of region of interest.
    """
    try:
        return region_of_interest.bbox
    except AttributeError:
        return region_of_interest

class SonataCircuitModel(WithFields):
    """
    A circuit model built according to SONATA...
    """
    provenance = Field(
        """
        `CircuitProvenance` instance describing the circuit model
        """,
        __default_value__=CircuitProvenance(
            label="BlueBrainCircuitModel",
            authors=["BBP Team"],
            date_release="Not Available",
            uri="Not Available",
            animal="Not Available",
            age="Not Available",
            brain_region="Not Available"))
    label = Field(
        """
        A label to represent your circuit model instance.
        """,
        __default_value__="BlueBrainCircuitModel")
    path_config_file = Field(
        """
        Path to the location of this circuit's SONATA config.
        """,
        __default_value__=NA)
    cell_sample_size = Field(
        """
        Number of cells to sample for measurements.
        """,
        __default_value__=20)

    @lazyfield
    def bluepysnap_circuit(self):
        """
        an instance of BluePySnap Circuit.
        """
        return SnapCircuit(self.path_config_file)

    @lazyfield
    def cell_collection(self):
        """
        Cells in the circuit.
        """
        try:
            bp = self.bluepysnap_circuit
            return bp.nodes
        except BluepySnapError as error:
            LOGGER.warn(
                LOGGER.get_source_info(),
                """Circuit does not have cells.
                or cells could not be loaded:
                \t{}""".format(error))
        return None

    @lazyfield
    def cells(self):
        """
        Pandas data-frame with cells in rows.
        """
        cells = self.cell_collection.get()
        return cells.assign(gid=cells.index.values)


    @lazyfield
    def connectome(self):
        """
        Connectome for the circuit.
        """
        try:
            bp = self.bluepysnap_circuit
            return bp.edges
        except BluepySnapError as error:
            LOGGER.warn(
                LOGGER.get_source_info(),
                """Circuit does not have cells.
                or cells could not be loaded:
                \t{}""".format(error))
        return None

    @lazyfield
    def brain_regions(self):
        """
        Brain regions (or sub regions) that the circuit models.
        """
        return self.cells.region.unique()

    @lazyfield
    def layers(self):
        """
        All the layers used in this circuit.
        """
        return self.cells.layer.unique()

    @lazyfield
    def mtypes(self):
        """
        All the mtypes used in this circuit.
        """
        return list(self.cells.mtype.unique())

    @lazyfield
    def etypes(self):
        """
        All the etypes in this circuit.
        """
        return self.cells.etype.unique()

    @terminology.use(*(
        terminology.circuit.terms + terminology.cell.terms))
    def _resolve_query_region(self, **query):
        """
        Resolve term `term` in query.
        """
        if not (terminology.circuit.roi in query
                or (terminology.circuit.region in query
                    and not isinstance(query[terminology.circuit.region], str))):
            return query
        for axis in XYZ:
            if axis in query:
                raise TypeError(
                    """
                    Cell query contained coordinates: {}.
                    To query in a region, use its bounding box as the value
                    for key `roi`.
                    """.format(axis))

        if terminology.circuit.roi in query:
            roi = query.pop(terminology.circuit.roi)
            if terminology.circuit.region in query:
                region = query.pop(terminology.circuit.region)
                raise TypeError(
                    """
                    Cannot disambiguate query.
                    Query contained both {}: {}
                    and {}: {}
                    """.format(
                        terminology.circuit.roi, roi,
                        terminology.circuit.region, region))
        else:
            roi = query.pop(terminology.circuit.region)

        corner_0, corner_1 = _get_bounding_box(roi)
        query.update({
            X: (corner_0[0], corner_1[0]),
            Y: (corner_0[1], corner_1[1]),
            Z: (corner_0[2], corner_1[2])})
        return query

    def _get_cell_query(self, query):
        """
        Convert `query` that will be accepted by a `BluePySNAPCircuit`.
        """
        def _get_query_layer(layers):
            """
            Arguments
            -------------
            layers : list or a singleton
            """
            if isinstance(layers, list):
                return [_get_query_layer(layer) for layer in layers]

            layer = layers
            if isinstance(layer, (int, np.int, np.int32)):
                return layer
            if layer.startswith('L') and layer[1] in "123456":
                return int(layer[1])
            return layer
            #return None

        cell_query =\
            terminology.bluebrain.cell.filter(**query)

        if terminology.bluebrain.cell.layer in cell_query:
            cell_query[terminology.bluebrain.cell.layer] =\
                _get_query_layer(
                    cell_query[terminology.bluebrain.cell.layer])

        return cell_query

    @terminology.use(*(
        terminology.circuit.terms +
        terminology.cell.terms))
    def get_cells(self,
            properties=None,
            with_gid_column=True,
            target=None,
            **query):
        """
        Get cells in a region, with requested properties.

        Arguments
        --------------
        properties : single cell property or  list of cell properties to fetch.
        query : sequence of keyword arguments providing query parameters.
        with_gid_column : if True add a column for cell gids.
        """
        LOGGER.debug(
            "Model get cells for query",
            "{}".format(query))
        cell_query =\
            self._get_cell_query(
                self._resolve_query_region(**query))

        if isinstance(target, str):
            cell_query["$target"] = target


        cells =\
            self.cell_collection.get(
                group=cell_query,
                properties=properties)
        if isinstance(target, Iterable):
            if isinstance(target, str):
                cells =\
                    cells.assign(group=target)
            elif isinstance(target, pd.DataFrame):
                cells =\
                    cells.reindex(target.index.to_numpy(np.int32))
            else:
                cells =\
                    cells.reindex(np.sort(np.unique([x for x in target])))\
                         .dropna()
        return\
            cells.assign(gid=cells.index.values) if with_gid_column else cells

    @terminology.use(*(
        terminology.circuit.terms +
        terminology.cell.terms))
    def get_cell_count(self, **query):
        """..."""
        return self.get_cells(**query).shape[0]


    @terminology.use(
        terminology.circuit.region,
        terminology.circuit.layer,
        terminology.circuit.depth,
        terminology.circuit.height,
        terminology.cell.mtype,
        terminology.cell.etype,
        terminology.cell.synapse_class)
    def random_cells(self,
            **cell_type):
        """
        Generate random cells of a given type.
        """
        cells = self.get_cells(**cell_type)
        while cells.shape[0] > 0:
            yield cells.sample(n=1).iloc[0]

    def are_connected(self, pre_neuron, post_neuron):
        """
        Is pre neuron connected to post neuron.
        """
        return pre_neuron in self.connectome.afferent_gids(post_neuron)

    def get_afferent_ids(self, neuron):
        """..."""
        return self.connectome.get_afferent_ids(neuron)

    def get_cell_types(self, cell_type_specifier):
        """
        Get cells of the specified type.

        Argument
        --------------
        cell_type_specifiers ::  An iterable of strings each of which
        is a property of cell.

        Results
        ---------------
        A Pandas DataFrame containing all cell types corresponding to
        the specification in `cell_type_specifiers.`
        For example, if the only specifier is `mtype` then this method
        will return a Pandas Series or a single column DataFrame containing
        all values of `mtype` in the circuit.
        """
        def __values(variable):
            try:
                return getattr(self, "{}s".format(variable))
            except AttributeError as error:
                raise TypeError(
                    """{} does not seem to be a property specifying
                    model {}'s cell types:
                    \t {}.
                    """.format(
                        variable,
                        self.__class__.__name__,
                        error))
            raise RuntimeError(
                """Computation should not reach here.""")

        def _get_tuple_values(params):
            """..."""
            if not params:
                return [[]]
            head_tuples =[
                [(params[0], value)]
                 for value in __values(params[0])]
            tail_tuples =\
                _get_tuple_values(params[1:])
            return [
                h+t for h in head_tuples
                for t in tail_tuples]

        return pd.DataFrame([
            dict(row)
            for row in _get_tuple_values(tuple(cell_type_specifier))])

    def pathways(self,
            cell_type_specifier=None,
            cell_types=None):
        """
        Pathways in this circuit with pre and post neuron groups
        specified.

        Arguments
        ------------
        `cell_type_specifier`: a tuple of cell properties whose
        values specify a cell.

        `cell_types`: a list of dicts specifying cell groups
        """
        if cell_type_specifier is not None:
            if cell_types is not None:
                raise TypeError(
                    """
                    Either `cell_type_specifier` or `cell_types` expected
                    as argument, not both.
                    """)
            cell_types = self.get_cell_types(cell_type_specifier)
        elif cell_types is None:
            raise TypeError(
                """
                One of either `cell_type_specifier` or `cell_types` expected.
                """)
        return pd.DataFrame(
            [CellType.pathway(pre_cell_type, post_cell_type)
             for _, pre_cell_type in cell_types.iterrows()
             for _, post_cell_type in cell_types.iterrows()])

    def get_thickness(self, positions):
        """
        Layer thickness as measured at a position.

        Arguments
        ------------
        position :: np.ndarray<x, y, z>
        """
        voxel_indices =\
            self.atlas.positions_to_indices(positions)
        thicknesses =\
            pd.DataFrame(self.atlas.layer_thicknesses(voxel_indices))\
              .assign(total=lambda df: df.sum(axis=1))
        thicknesses.columns.name = "layer"
        return thicknesses
                
