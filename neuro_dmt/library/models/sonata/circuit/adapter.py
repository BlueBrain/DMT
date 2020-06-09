# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published 
# by the Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT 
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License 
# for more details.

# You should have received a copy of the GNU Lesser General Public License 
# along with DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Adapt a SONATA circuit (loaded by BluePySNAP) to our analyses.
"""

from copy import deepcopy
from collections.abc import Set, Mapping, Iterable
import numpy as np
import pandas as pd
from dmt.model.interface import implements
from dmt.model.adapter import adapts
from dmt.tk.journal import Logger
from dmt.tk.field import NA, Field, LambdaField, lazyfield, WithFields
from dmt.tk.collections import get_list
from neuro_dmt.analysis.circuit.composition.interfaces import\
    CellDensityAdapterInterface
from neuro_dmt.library.models.sonata.circuit.model import\
    SonataCircuitModel
from neuro_dmt import terminology
from neuro_dmt.utils.geometry.roi import Cuboid

X = terminology.bluebrain.cell.x
Y = terminology.bluebrain.cell.y
Z = terminology.bluebrain.cell.z
XYZ =[X, Y,Z]
LAYER = terminology.bluebrain.cell.layer

def _get_bounding_box(region_of_interest):
    """
    Extract the bounding box of region of interest.
    """
    try:
        return region_of_interest.bbox
    except AttributeError:
        return region_of_interest


@adapts(SonataCircuitModel)
class SonataCircuitAdapter(WithFields):
    """
    Adapt a circuit that confirms to SONATA
    """
    sample_size = Field(
        """
        Number of samples to make to measure a circuit phenomenon.
        """,
        __default_value__=20)
    bounding_box_size = Field(
        """
        Dimensions of the bounding box to sample spatial regions inside the
        circuit's physical space.
        """,
        __default_value__=50. * np.ones(3))
    model_has_subregions = Field(
        """
        Does the circuit model have subregions?
        For example, we might have circuit that models some atlas based 
        sub-regions of the SSCX. The `cells` dataframe will have these values
        in column `region`.
        Otherwise we may have a simpler circuit, like the O1, that uses
        experimental data obtained for the SSCx, but models just a column.
        Thus we cannot say that the circuit model has sub-regions.
        """)

    def get_namespace(self, circuit_model):
        """
        A namespace providing values for circuit properties required by our
        analyses.
        """
        return {
            "layer-values": self.get_layers(circuit_model),
            "layer-type": self.get_layer_type(circuit_model),
            "region": self.get_brain_region(circuit_model),
            "sub-regions": self.get_sub_regions(circuit_model),
            "animal": self.get_animal(circuit_model)
        }

    def get_provenance(self, circuit_model):
        """..."""
        return circuit_model.provenance.field_dict

    def get_label(self, circuit_model):
        """..."""
        return circuit_model.label

    def get_animal(self, circuit_model):
        return circuit_model.provenance.animal

    def get_brain_region(self, circuit_model):
        """
        Label for the brain region modeled.
        """
        return circuit_model.provenance.brain_region

    def get_sub_regions(self, circuit_model):
        """..."""
        return circuit_model.cells.region.unique()\
            if self.model_has_subregions else\
               [self.get_brain_region(circuit_model)]
    @staticmethod
    def _prefix_L(layer):
        if isinstance(layer, (int, np.int16, np.int32, np.int64, np.integer)):
            return "L{}".format(layer)
        if isinstance(layer, str):
            if layer[0] != "L":
                return "L{}".format(layer)
            return layer
        raise TypeError(
            "Bad type {} of layer value {} ".format(type(layer), layer))

    def get_layers(self, circuit_model):
        return [self._prefix_L(layer) for layer in circuit_model.cells.layer.unique()]

    def get_layer_type(self, circuit_model):
        try:
            return circuit_model.layer_type
        except AttributeError:
            return "Cortical"

    def get_mtypes(self, circuit_model):
        """..."""
        return circuit_model.cells.mtype.unique()

    def get_etypes(self, circuit_model):
        """..."""
        return circuit_model.cells.etype.unique()

    def get_base_morphology(self, mtype):
        """
        Remove layer information from an `mtype` label.
        """
        return mtype.split('_')[-1]

    def get_cell_types(self, circuit_model, query):
        """
        Get cell-types for the given specifiers

        Arguments
        -------------
        query :: Either an iterable of unique cell type specifiers
        ~        Or a mapping cell_type_specifier --> value / list(value)

        Returns
        -------------
        A `pandas.DataFrame` containing all cell-types,
        each row providing values for each cell type specifier.
        """
        try:
            key_values = query.items()
        except AttributeError:
            key_values = []

        query_with_values ={
            key: value
            for key, value in key_values
            if value is not None}

        def _values(variable):
            try:
                raw_values = query_with_values[variable]
            except (TypeError, KeyError):
                try:
                    get_values = getattr(self, "get_{}s".format(variable))
                except AttributeError as error:
                    raise AttributeError(
                        """
                        {} adapter does not implement a getter for cell property
                        {}.
                        """.format(self.__class__.__name__, variable))
                raw_values = get_values(circuit_model)

            return get_list(raw_values)

        def _get_tuple_values(params):
            """..."""
            if not params:
                return [[]]

            head_tuples =[
                [(params[0], value)]
                 for value in _values(params[0])]
            tail_tuples =\
                _get_tuple_values(params[1:])
            return [
                h + t for h in head_tuples
                for t in tail_tuples]

        try:
            cell_type_specifiers = query.keys()
        except AttributeError:
            cell_type_specifiers = query

        return pd.DataFrame([
            dict(row)
            for row in _get_tuple_values(tuple(cell_type_specifiers))])

    def get_pathways(self,
            circuit_model,
            pre_synaptic=None,
            post_synaptic=None):
        """
        Arguments
        ----------
        pre_synaptic ::  Either an iterable of unique cell type specifiers
        ~                Or a mapping `cell_type_specifer==>value`
        post_synaptic :: Either an iterable of unique cell type specifiers
        ~               Or a mapping `cell_type_specifer==>value`
        """
        if pre_synaptic is None:
            if post_synaptic is None:
                raise TypeError(
                    """
                    Missing arguments. Pass at least one of:
                    1. pre_synaptic
                    2. post_synaptic
                    """)
            pre_synaptic = post_synaptic
        else:
            if post_synaptic is None:
                post_synaptic = pre_synaptic

        def _at(synaptic_location, cell_type):
            return pd.concat(
                [cell_type],
                axis=1,
                keys=["{}_synaptic".format(synaptic_location)])

        pre_synaptic_cell_types =\
            _at("pre",
                self.get_cell_types(circuit_model, pre_synaptic))
        post_synaptic_cell_types =\
            _at("post",
                self.get_cell_types(circuit_model, post_synaptic))
        return\
            pd.DataFrame([
                pre.append(post)
                for _, pre in pre_synaptic_cell_types.iterrows()
                for _, post in post_synaptic_cell_types.iterrows()])\
              .reset_index(drop=True)

    def get_bounding_box(self, circuit_model):
        """
        A bounding box containing the circuit.
        """
        df = self.get_cells(circuit_model)[XYZ]\
                 .agg(["min", "max"])
        return Cuboid(df["min"].values, df["max"].values)

    def get_layer_thickness_values(self,
            circuit_model,
            sample_size=100,
            **spatial_query):
        """
        Get layer thickness sample for regions specified by a spatial query.
        Thicknesses will be computed for all voxels visible for the spatial
        query. Another possibility is to compute thickness for a random sample
        of visible voxels.

        Because there can be too many (voxel) positions in a region,
        measurement will be made on a sample of positions in the specified
        region.

        Note
        ------
        This implementation is for columnar circuits,
        with layers along the y-axis.
        Change this for an atlas based circuit.
        """
        cells = self.get_cells(
            circuit_model, **spatial_query
        ).assign(layer=lambda df: df.layer.apply(self._prefix_L))
        bbox_circuit = cells[XYZ].agg(["min", "max"])
        ymin_circuit = bbox_circuit.loc["min"].y
        ymax_circuit = bbox_circuit.loc["max"].y

        def _get_column(position):
            """
            Get a column spanning the circuit with its axis passing through
            a given position.
            """
            return Cuboid(
                np.array(
                    [position[0], ymin_circuit, position[2]]
                ) - self.bounding_box_size,
                np.array(
                    [position[0], ymax_circuit, position[2]]
                ) + self.bounding_box_size
            )

        def _apparent_thickness(position):
            """
            Thickness of layers as apparent from a position in the column.
            """
            column = _get_column(position)
            return\
                self.get_cells(circuit_model, roi=column)[[LAYER, Y]]\
                    .assign(**{LAYER: lambda df: df[LAYER].apply(self._prefix_L)})\
                    .groupby(LAYER)\
                    .agg(["min", "max"])[Y]\
                    .apply(lambda ys: ys["max"] - ys["min"], axis=1)

        positions = cells.sample(n=sample_size)[XYZ]
        return positions.apply(_apparent_thickness, axis=1)
        # return\
        #     self.get_cells(circuit_model, **spatial_query)\
        #         .groupby(terminology.bluebrain.cell.layer)\
        #         .agg(["min", "max"])\
        #         .y\
        #         .apply(lambda ys: ys["max"] - ys["min"], axis=1)

    def get_height(self, circuit_model, depth):
        """
        Get height for model of a cortical column.
        """
        cells = self.get_cells(circuit_model)
        return cells.y.max() - depth

    @terminology.use(*(
        terminology.circuit.terms + terminology.cell.terms))
    def _resolve_query_region(self, brain_region, **query):
        """
        Resolve term `term` in query.

        brain_region :: Brain region modeled 
        """
        if not (terminology.circuit.roi in query
                or (terminology.circuit.region in query
                    and not isinstance(query[terminology.circuit.region], str))):
            if not self.model_has_subregions:
                try:
                    region = query.pop(terminology.circuit.region)
                except KeyError:
                    region = None
                if region and region != brain_region:
                    query["region"] = region
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
    
    def get_cell_query(self, query):
        """
        Convert `query` that will be accepted by a `BluePySNAPCircuit`.
        """
        def _get_query_layer(layers):
            """
            Arguments
            ----------
            layers : list or a singleton
            """
            if isinstance(layers, list):
                return [_get_cell_query(layer) for layer in layers]
            
            layer = layers
            if isinstance(layer, (int, np.int, np.int32)):
                return layer
            if layer.startswith('L') and layer[1] in "123456":
                return int(layer[1])
            return layer

        cell_query =\
            terminology.bluebrain.cell.filter(**query)

        if terminology.bluebrain.cell.layer in cell_query:
            cell_query[
                terminology.bluebrain.cell.layer] =\
                    _get_query_layer(cell_query[
                        terminology.bluebrain.cell.layer])
        return cell_query

    @terminology.use(*(
        terminology.circuit.terms + terminology.cell.terms))
    def get_cells(self,
            circuit_model,
            properties=None,
            with_gid_column=True,
            target=None,
            **query):
        """
        Get cells in a pandas.DataFrame
        """
        cell_query =\
            self.get_cell_query(
                self._resolve_query_region(
                    self.get_brain_region(circuit_model),
                    **terminology.bluebrain.cell.filter(**query)))
        if isinstance(target, str):
            cell_query["$target"] = target

        cells =\
            circuit_model.cell_collection\
                         .get(group=cell_query, properties=properties)
        if isinstance(target, Iterable):
            if isinstance(target, str):
                cells = cells.assign(group=target)
            elif isinstance(target, pd.DataFrame):
                cells = cells.reindex(target.index.to_numpy(np.int32))
            else:
                cells = cells.reindex(np.sort(np.unique([x for x in target])))\
                             .dropna()
        return cells.assign(gid=cells.index.values)\
            if with_gid_column else cells

    def get_soma_positions(self, circuit_model, cells):
        """..."""
        try:
            return cells[XYZ]
        except KeyError:
            return self.get_cells(circuit_model)\
                       .loc[cells.index.to_numpy(np.int32)]\
                       [XYZ]

    def get_soma_distance(self,
            circuit_model,
            cell,
            cell_group,
            bin_size=100):
        """..."""
        delta_positions =\
            cell_group[XYZ].to_numpy(np.float)\
            - cell[XYZ].to_numpy(np.float)
        distances =\
            np.linalg.norm(delta_positions, axis=1)
        bin_starts =\
            bin_size * np.floor(distances / bin_size)
        return np.array([
            bin_start + bin_size / 2.
            for bin_start in bin_starts])

    def get_cell_gids(self, circuit_model, cells=None):
        """..."""
        if cells is None:
            cells = self.get_cell(circuit_model)

        return\
            cells.index.to_numpy(np.int32)

    def get_afferent_gids(self,
            circuit_model,
            post_synaptic_cell):
        """..."""
        return\
            circuit_model.connectome\
                         .afferent_gids(
                             post_synaptic_cell.gid)
    def _resolve_gids(self, circuit_model, cell_group):
        """
        Resolve cell gids...
        """
        if isinstance(cell_group, np.ndarray):
            gids = cell_group
        elif isinstance(cell_group, list):
            gids = np.ndarray(cell_group)
        elif isinstance(cell_group, pd.Series):
            try:
                gids = np.array([cell_group.gid])
            except AttributeError:
                gids = self.get_cells(circuit_model, **cell_group).gid.values
        elif isinstance(cell_group, pd.DataFrame):
            gids = cell_group.gid.values
        else:
            raise ValueError(
                """
                Could not resolve gids from object {}
                """.format(cell_group))
        return gids

    def get_afferent_connections(self,
            circuit_model,
            post_synaptic,
            with_synapse_ids=False,
            with_synapse_count=True):
        """
        Arguments
        ----------------
        post_synaptic :: Either a pandas.Series representing a cell
        ~                or a pandas.DataFrame containing cells as rows
        ~                or a numpy.array of cell gids.,
        """
        post_synaptic_gids =\
            self._resolve_gids(circuit_model, post_synaptic)
        iter_connections =\
            circuit_model.connectome\
                         .iter_connections(
                             target=post_synaptic_gids,
                             return_edge_ids=with_synapse_ids,
                             return_edge_count=with_synapse_count)
        connections =\
            np.array([
                connection for connection in iter_connections])
        if with_synapse_count:
            if connections.shape[0] == 0:
                return pd.DataFrame([], columns=["pre_gid", "post_gid", "strength"])
            return\
                pd.DataFrame({
                    "pre_gid": np.array(connections[:, 0], dtype=np.int32),
                    "post_gid": np.array(connections[:, 1], dtype=np.int32),
                    "strength": connections[:, 2]})
        if connections.shape[0] == 0:
            return pd.DataFrame([], columns=["pre_gid"])
        return pd.DataFrame({"pre_gid": connections[:, 0]})

    def get_efferent_connections(self,
            circuit_model,
            pre_synaptic,
            with_synapse_ids=False,
            with_synapse_count=True):
        """

        Arguments
        ----------------
        pre_synaptic :: Either a pandas.Series representing a cell
        ~               or a pandas.DataFrame containing cells as rows
        ~               or a numpy.array of cell gids.,
        """
        pre_synaptic_gids =\
            self._resolve_gids(circuit_model, pre_synaptic)
        iter_connections =\
            circuit_model.connectome\
                         .iter_connections(
                             source=pre_synaptic_gids,
                             return_edge_ids = with_synapse_ids,
                             return_edge_count=with_synapse_count)
        connections =\
            np.array([
                connection for connection in iter_connections])
        if with_synapse_count:
            if connections.shape[0] == 0:
                return pd.DataFrame([], columns=["post_gid", "post_gid", "strength"])
            return\
                pd.DataFrame({
                    "pre_gid": np.array(connections[:, 0], dtype=np.int32),
                    "post_gid": np.array(connections[:, 1], dtype=np.int32),
                    "strength": connections[:, 2]})
        if connections.shape[0] == 0:
            return pd.DataFrame([], columns=["post_gid"])
        return pd.DataFrame({"post_gid": connections[:, 1]})

    def get_connections(self,
            circuit_model,
            cell_group,
            direction,
            with_synapse_ids=False,
            with_synapse_count=True):
        """..."""
        if with_synapse_ids and with_synapse_count:
            raise TypeError(
                """
                `get_connections(...)` called requesting both synapse ids and
                synapse count. Only one of these may be requested.
                """)
        return\
            self.get_afferent_connections(
                circuit_model, cell_group,
                with_synapse_ids=with_synapse_ids,
                with_synapse_count=with_synapse_count)\
            if direction in ("AFF", "afferent", "aff") else\
               self.get_efferent_connections(
                   circuit_model,
                   cell_group,
                   with_synapse_ids,
                   with_synapse_count)

