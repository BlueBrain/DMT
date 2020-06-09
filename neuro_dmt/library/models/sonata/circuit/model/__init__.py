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
from dmt.tk import collections
from dmt.tk.field import NA, Field, LambdaField, lazyfield, WithFields
from dmt.tk.journal import Logger
from dmt.tk.collections import take
from neuro_dmt import terminology
from neuro_dmt.analysis.reporting import CircuitProvenance

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
    path_circuit_data = Field(
        """
        Path to the location of this circuit's SONATA config.
        """,
        __default_value__=NA)
    config_file = Field(
        """
        Name of the SONATA circuit configuration file.
        """,
        __default_value__="circuit_config.json")
    path_config_file = LambdaField(
        """
        Path to the SONATA circuit config file.
        """,
        lambda self: os.path.join(self.path_circuit_data, self.config_file))
    cell_sample_size = Field(
        """
        Number of cells to sample for measurements.
        """,
        __default_value__=20)

    def __init__(self, circuit=None, *args, **kwargs):
        """
        Initialize with a circuit.

        Arguments
        ----------
        circuit: BluePySNAP.Circuit
        """
        if circuit is not None:
            self._bluepysnap_circuit = circuit
        super().__init__(*args, **kwargs)

    @lazyfield
    def bluepysnap_circuit(self):
        """
        an instance of BluePySnap Circuit.
        """
        try:
            return SnapCircuit(self.path_config_file)
        except FileNotFoundError:
            raise ValueError(
                """
                Paths to circuit data were not set correctly:
                `path_circuit_data`: {}
                `config_file`: {}
                `path_config_file`: {}
                """.format(self.path_circuit_data,
                           self.config_file,
                           self.path_config_file))


    @lazyfield
    def cell_collection(self):
        """
        Cells in the circuit.
        """
        try:
            bp = self.bluepysnap_circuit
            return bp.nodes["All"]
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
        bp = self.bluepysnap_circuit
        edges = bp.edges
        try:
            return edges["All"]
        except KeyError:
            return edges["default"]
        except BluepySnapError as error:
            LOGGER.warn(
                LOGGER.get_source_info(),
                """Circuit does not have edges,
                or could not be loaded:
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
