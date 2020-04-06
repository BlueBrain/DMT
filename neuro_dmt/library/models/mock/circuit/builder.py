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
Build a mock circuit.
"""

import numpy as np
import pandas as pd
from tqdm import tqdm
from neuro_dmt import terminology
from dmt.tk.field import Field, WithFields
from dmt.tk.journal import Logger
from neuro_dmt.utils.geometry import Position
from .cell import Cell, CellCollection
from .composition import CircuitComposition
from .connectivity import CircuitConnectivity
from .connectome import Connectome

MTYPE = terminology.bluebrain.cell.mtype
REGION = terminology.bluebrain.cell.region
LAYER = terminology.bluebrain.cell.layer

LOGGER = Logger(client=__file__)

class CircuitBuilder(WithFields):
    """
    Builds a circuit.
    """

    composition = Field(
        """
        An object parameterizing the circuit's composition.
        """,
        __type__=CircuitComposition)
    connectivity = Field(
        """
        An object parameterizing the circuit's connectivity.
        """,
        __type__=CircuitConnectivity)

    def get_cell_density(self,
            region=None,
            layer=None,
            mtype=None):
        """
        Density of cells of given 'mtype' in given 'region' and 'layer'.
        At least one of 'region', 'layer', 'mtype' must be specified.
        """
        assert region or layer or mtype,\
            "region, layer, mtype all invalid."
        if not mtype:
            return\
                self.composition\
                    .cell_density.xs(
                        (region, layer) if region else (layer),
                        label=(REGION, LAYER) if region else (LAYER))
        return\
            self.composition\
                .cell_density.xs(
                    (region, layer, mtype) if region else (layer, mtype),
                    level=(REGION, LAYER, MTYPE) if region else (LAYER, MTYPE))

    def get_number_cells(self, region, layer, mtype):
        """
        How many cells of given 'mtype' in a given 'layer'?
        """
        volume =\
            self.composition.thickness_layer[layer] *\
            self.composition.length_base ** 2
        density =\
            self.get_cell_density(
                region, layer, mtype)["mean"]
        return int(1.e-9 * density * volume)

    def get_cells(self):
        """
        Create cells for each layer and mtype combination.
        """
        return [
            Cell(
                region=region,
                layer=layer,
                position=Position.sample(
                    self.composition.bounding_box(layer, mtype)),
                mtype=mtype,
                etype=etype)
            for region in self.composition.regions
            for layer in self.composition.layers
            for mtype in self.composition.mtypes
            for etype in self.composition.etypes
            for _ in range(self.get_number_cells(region, layer, mtype))]

    def get_cell_collection(self):
        """
        Get a CellCollection.
        """
        return CellCollection(
            self.get_cells(),
            regions=self.composition.regions,
            layers=self.composition.layers)

    def get_connectome(self, cell_collection):
        """
        Get this circuit's connectome.
        """
        LOGGER.debug(
            "Mock circuit builder: get_connectome(...)")
        cells =\
            cell_collection.get()
        # afferent_gids =[
        #     self.connectivity.get_afferent_gids(post_synaptic_cell, cells)
        #     for _, post_synaptic_cell in tqdm(cells.iterrows())]
        # mtype_of =\
        #     np.array(
        #         cell_collection.get(properties="mtype"),
        #         dtype=str)
        # afferent_synapse_counts =[
        #     [self.connectivity.get_synapse_count(cells.iloc[pre_gid],
        #                                          post_synaptic_cell)
        #      for pre_gid in afferent_gids[post_gid]]
        #     for post_gid, post_synaptic_cell in tqdm(cells.iterrows())]

        # afferent_synapse_counts =[
        #     [self.connectivity.get_synapse_count(cells.iloc[pre_gid],
        #                                          cells.iloc[post_gid])
        #      for pre_gid in afferent_gids[post_gid]]
        #     for post_gid in tqdm(cell_collection.gids)]

        # afferent_synapse_counts =\
        #     self.connectivity\
        #         .get_synapse_count(
        #             afferent_gids, cell_collection)
        
        # assert len(afferent_gids) == len(afferent_synapse_counts)

        # for gids, syn_counts in zip(afferent_gids, afferent_synapse_counts):
        #     assert len(gids) == len(syn_counts),\
        #         "Length {} of afferent gids should equal that of synapse counts"\
        #         .format(len(gids), len(syn_counts))
        connections =\
            pd.concat([
                self.connectivity.get_afferent_connections(post_gid, post_cell, cells)
                for post_gid, post_cell in tqdm(cells.iterrows())])\
              .assign(synapse_count=self.connectivity.get_synapse_counts)
                  
        return Connectome(
            cells=cell_collection,
            connections=connections)
                
        return Connectome(
            cells=cell_collection,
            connections=pd.concat([
                self.connectivity.get_afferent_connections(post_gid, post_cell, cells)
                for post_gid, post_cell in tqdm(cells.iterrows())]))
        
        
        # return Connectome(
        #     cells=cell_collection,
        #     afferent_adjacency=[
        #         np.array(list(
        #             zip(afferent_gids[gid], afferent_synapse_counts[gid])))
        #         for gid in cell_collection.gids])
