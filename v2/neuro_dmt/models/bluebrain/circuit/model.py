"""
A class that represents circuit models developed at the Blue Brain Project.
"""

import os
import yaml
import numpy as np
import pandas as pd
import bluepy
from bluepy.v2.circuit import Circuit as BluePyCircuit
from bluepy.exceptions import BluePyError
from bluepy.v2.enums import Cell
from dmt.tk import collections
from dmt.tk.field import Field, lazyfield, WithFields
from dmt.tk.journal import Logger
from neuro_dmt import terminology
from .atlas import BlueBrainCircuitAtlas

XYZ = [Cell.X, Cell.Y, Cell.Z]

logger = Logger(client=__file__)
NA = "not-available"

def _get_bounding_box(region_of_interest):
    """
    Extract the bounding box of region of interest.
    """
    try:
        return region_of_interest.bbox
    except AttributeError:
        return region_of_interest

XYZ = [Cell.X, Cell.Y, Cell.Z]

class BlueBrainCircuitModel(WithFields):
    """
    A circuit model developed at the Blue Brain Project.
    """
    label = Field(
        """
        A label to represent your circuit model instance.
        """,
        __default_value__="BlueBrainCircuitModel")
    path_circuit_data = Field(
        """
        Path to the location of this circuit's data. This data is loaded as a
        BluePy circuit if a Bluepy circuit is not provided at initialization.
        """,
        __required__=False)
    circuit_config = Field(
        """
        Name of the file (under `.path_circuit_data`) that contains the
        circuit's configuration and provides paths to the data containing
        cells and connectome.
        """,
        __default_value__="CircuitConfig")
    circuit_config_base = Field(
        """
        After the first phase of circuit build, that creates a cell collection,
        a basic circuit config file is created in the circuit directory.
        """,
        __default_value__="CircuitConfig_base")

    def __init__(self, circuit=None, *args, **kwargs):
        """
        Initialize with a circuit.

        Arguments
        -------------
        circuit: A BluePy circuit.
        """
        if circuit is not None:
            self._bluepy_circuit = circuit

        super().__init__(*args, **kwargs)

    def get_path(self, *relative_path):
        """
        Absolute path to the file at `relative_path`

        Arguments
        ----------
        `relative_path`: Sequence of strings describing a path relative to
        the circuit's location.
        """
        return os.path.join(self.path_circuit_data, *relative_path)

    @lazyfield
    def bluepy_circuit(self):
        """
        An instance of the BluePy circuit object.
        """
        try:
            circuit = BluePyCircuit(
                self.get_path(self.circuit_config))
        except FileNotFoundError:
            circuit = BluePyCircuit(
                self.get_path(self.circuit_config_base))
        assert isinstance(circuit, BluePyCircuit)
        return circuit

    @lazyfield
    def atlas(self):
        """
        Atlas associated with this circuit.
        """
        return BlueBrainCircuitAtlas(
            path=self.bluepy_circuit.atlas.dirpath)

    @lazyfield
    def cells(self):
        """
        Cells for the circuit.
        """
        try:
            bp = self.bluepy_circuit
            assert isinstance(bp, BluePyCircuit), bp
            return bp.cells
        except BluePyError as error:
            logger.warn(
                logger.get_source_info(),
                "Circuit does not have cells.",
                "BluePy complained:\n\t {}".format(error))
        return None

    @lazyfield
    def connectome(self):
        """
        Connectome for the circuit.
        """
        try:
            bp = self.bluepy_circuit
            assert isinstance(bp, BluePyCircuit), bp
            return bp.connectome
        except BluePyError as error:
            logger.warn(
                logger.get_source_info(),
                "Circuit does not have a connectome.",
                "BluePy complained: \n\t {}".format(error))
        return None

    def _atlas_value(self,
            key, value):
        """
        Value of query parameter as understood by the atlas.
        """
        if value is None:
            return None
        if key == terminology.circuit.region:
            return self.atlas.used_value(region=value)
        if key == terminology.circuit.layer:
            return self.atlas.used_value(layer=value)
        raise RuntimeError(
            "Unknown / NotYetImplemented query parameter {}".format(key))

    @terminology.use(*terminology.circuit.terms)
    def _resolve_query_region(self, **query):
        """
        Resolve region in query.

        Arguments
        ------------
        query : a dict providing parameters for a circuit query.
        """
        if (terminology.circuit.region not in query
            or isinstance(query[terminology.circuit.region], str)):
            return query

        for axis in XYZ:
            assert axis not in query, list(query.keys())

        region = query.pop(terminology.circuit.region)
        assert region, query
        corner_0, corner_1 =\
            _get_bounding_box(region)
        query.update({
            Cell.X: (corner_0[0], corner_1[0]),
            Cell.Y: (corner_0[1], corner_1[1]),
            Cell.Z: (corner_0[2], corner_1[2])})
        return query

    def _get_cell_query(self, **query):
        """
        Convert `query` that will be accepted by `BluePyCircuit`.
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
            if isinstance(layer, (int, np.int)):
                return layer
            if layer.startswith('L') and layer[1] in "123456":
                return int(layer[1])
            return layer

        cell_query = terminology.circuit.filter(
            **terminology.cell.filter(**query))

        if terminology.circuit.layer in cell_query:
            cell_query[terminology.circuit.layer] =\
                _get_query_layer(cell_query[terminology.circuit.layer])

        return cell_query

    @terminology.use(*(terminology.circuit.terms + terminology.cell.terms))
    def get_cells(self, properties=None, **query):
        """
        Get cells in a region, with requested properties.

        Arguments
        --------------
        properties : single cell property or  list of cell properties to fetch.
        query : sequence of keyword arguments providing query parameters.
        """
        cell_query = self._get_cell_query(
            **self._resolve_query_region(**query))
        return\
            self.cells.get(
                group=cell_query,
                properties=properties)

    @terminology.use(*(terminology.circuit.terms + terminology.cell.terms))
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
    def random_positions(self,
            as_array=False,
            **query_parameters):
        """
        Generate random positions (as np.array([x, y, z])) in a region defined
        by spatial parameters in the query.
        """
        cells = self.get_cells(properties=XYZ, **query_parameters)
        
        while cells.shape[0] > 0:
            position = cells.sample(n=1).iloc[0]
            yield position.values if as_array else position
            
