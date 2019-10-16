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
            return BluePyCircuit(
                self.get_path(self.circuit_config))
        except FileNotFoundError:
            return BluePyCircuit(
                self.get_path(self.circuit_config_base))
        raise Exception("Execution should not reach here.")

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
            return self.bluepy_circuit.cells
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
            return self.bluepy_circuit.connectome
        except BluePyError as error:
            logger.warn(
                logger.get_source_info(),
                "Circuit does not have a connectome.",
                "BluePy complained: \n\t {}".format(error))
        return None

    @terminology.use(terminology.circuit.region)
    def _resolve_query_region(self, query):
        """
        Resolve region in query.

        Arguments
        ------------
        query : a dict providing parameters for a circuit query.
        """
        if ("region" not in query
            or isinstance(str, query[terminology.circuit.region])):
            return query
        for axis in XYZ:
            assert axis not in query, list(query.keys())
        corner_0, corner_1 =\
            _get_bounding_box(
                query.pop(terminology.circuit.region))
        query.update{
            Cell.X: (corner_0[0], corner_1[0]),
            Cell.Y: (corner_0[1], corner_1[1]),
            Cell.Z: (corner_0[2], corner_1[2])}
        return query

    @terminology.use(
        terminology.circuit.region,
        terminology.circuit.layer,
        terminology.circuit.depth,
        terminology.circuit.height,
        terminology.cell.mtype,
        terminology.cell.etype,
        terminology.cell.synapse_class)
    def get_cells(self,
            properties=[],
            **query):
        """
        Get cells in a region, with requested properties.

        Arguments
        --------------
        properties : single cell property or  list of cell properties to fetch.
        query : sequence of keyword arguments providing query parameters.
        """
        return self.cells.get(
            group=self._resolve_query_region(query),
            properties=properties)


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
            **query_parameters)
    """
    Generate random positions (as np.array([x, y, z])) in a region defined
    by spatial parameters in the query.
    """
    cells = self.get_cells(properties=XYZ, **query_parameters)

    while cells.shape[0] > 0:
        position = cells.sample(n=1).iloc[0]
        yield position.values if as_array else position

