"""
Build a mock circuit.
"""

import numpy as np
import pandas as pd
from bluepy.v2.enums import Cell as CellProperty
from dmt.tk.field import Field, WithFields

from ..geometry import Position
from .cell import Cell, CellCollection
from .composition import CircuitComposition
from .connectivity import CircuitConnectivity
from .connectome import Connectome

MTYPE = CellProperty.MTYPE
REGION = CellProperty.REGION
LAYER = CellProperty.LAYER


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
                mtype=mtype)
            for region in self.composition.regions
            for layer in self.composition.layers
            for mtype in self.composition.mtypes
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
        afferent_gids =[
            np.sort(np.random.choice(
                cell_collection.gids,
                self.connectivity.get_afferent_degree(**cell_props.to_dict()),
                replace=False))
            for _, cell_props in cell_collection.get().iterrows()]
        mtype_of =\
            np.array(
                cell_collection.get(properties="mtype"),
                dtype=str)
        afferent_synapse_counts =[
            [self.connectivity.get_synapse_count(
                mtype_of[pre_gid], mtype_of[post_gid])
             for post_gid in afferent_gids[pre_gid]]
            for pre_gid in cell_collection.gids]

        assert len(afferent_gids) == len(afferent_synapse_counts)

        for gids, syn_counts in zip(afferent_gids, afferent_synapse_counts):
            assert len(gids) == len(syn_counts),\
                "Length {} of afferent gids should equal that of synapse counts"\
                .format(len(gids), len(syn_counts))

        return Connectome(
            afferent_adjacency=[
                np.array(list(
                    zip(afferent_gids[gid], afferent_synapse_counts[gid])))
                for gid in cell_collection.gids])
