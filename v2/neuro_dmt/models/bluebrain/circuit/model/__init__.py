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
from dmt.tk.collections import take
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

    cell_sample_size = Field(
        """
        Number of cells to sample for measurements.
        """,
        __default_value__=20)

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
    def cell_collection(self):
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
    def cells(self):
        """
        Pandas data-frame with cells in rows.
        """
        return self.cell_collection.get()

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

    @lazyfield
    def mtypes(self):
        """
        All the mtypes used in this circuit.
        """
        return self.cells.mtype.unique()

    @lazyfield
    def etypes(self):
        """
        All the etypes in this circuit.
        """
        return self.cells.etype.unique()

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
            self.cell_collection.get(
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
    def random_cells(self,
            **cell_type):
        """
        Generate random cells of a given type.
        """
        cells = self.get_cells(**cell_type)
        while cells.shape[0] > 0:
            yield cells.sample(n=1).iloc[0]

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

    def are_connected(self, pre_neuron, post_neuron):
        """
        Is pre neuron connected to post neuron.
        """
        return pre_neuron in self.connectome.afferent_gids(post_neuron)

    def get_afferent_ids(self, neuron):
        """..."""
        return self.connectome.get_afferent_ids(neuron)

    def random_pathway_pairs(self,
            pre_cell_type={},
            post_cell_type={}):
        """
        Generate random pairs of neurons in a given pathway.
        """
        pre_neurons =\
            self.cell_collection\
                .ids(group=self._get_cell_query(**pre_cell_type))
        post_neurons =\
            self.cell_collection\
                .ids(group=self._get_cell_query(**post_cell_type))
        while len(pre_neurons) > 0:
            pre_neuron = np.random.sample(pre_neurons)
            while len(post_neurons) > 0:
                post_neuron = np.random.sample(post_neurons)
                yield (pre_neuron, post_neuron)

    def get_cell_types(self, cell_type_specifiers):
        """
        Get cells of the specified type.

        Argument
        --------------
        cell_type_specifiers ::  A tuple of strings each of which
        is a property of cell.

        Results
        ---------------
        A Pandas DataFrame containing all cell types corresponding to
        the specification in `cell_type_specifiers.`
        For example, if the only specifier is `mtype` then this method
        will return a Pandas Series or a single column DataFrame containing
        all values of `mtype` in the circuit.
        """
        if cell_type_specifiers != ("mtype",):
            raise NotImplementedError(
            """
            Current implementation is an example.
            Generalize it...
            """)

        return self.mtypes
            
    def get_connection_probability(self,
            pre_cell_type,
            post_cell_type):
        """..."""
        pre_cells = take(
            self.cell_sample_size,
            self.random_cells(**pre_cell_type))
        post_cells = take(
            self.cell_sample_size,
            self.random_cells(**post_cell_type))
        number_connections =\
            np.sum([
                np.in1d(
                    pre_cells,
                    self.connectome.get_afferent_ids(post_cell))
                for post_cell in post_cells])
        return number_connections / (self.cell_sample_size ^ 2)
    
    def get_pathway_property(self,
            cell_type_specifiers,
            property_defining_computation):
        """
        Compute a pathway property.

        Arguments
        ---------------
        cell_type_specifiers : A tuple of cell properties that define the
        pathway. For example `('mtype', )`
        property_defining_computation : A method to compute the property for a
        single (pre, post) pair...
        """
        cell_types =\
            self.get_cell_types(cell_type_specifiers)
        cell_types_at = lambda pos: cell_types.rename(**{
            column: "{}_{}".format(pos, column)
            for column in cell_types.columns})
        pre_types = cell_types_at("pre")
        post_types = cell_types_at("post")
        return pd\
            .concat(
                [pre_types,
                 post_types,
                 pd.Series(
                     property_defining_computation(pre_type, post_type)
                     for _, pre_type in pre_types.iterrows()
                     for _, post_type in post_types.iterrows())],
                axis=1)\
            .set_index(
                list(pre_types.columns.values) + list(post_types.columns.values))

    @lazyfield
    def connection_probability_cache(self):
        """..."""
        return {}

    def connection_probability(self,
            cell_type_specifiers):
        """..."""
        if cell_type_specifiers\
           not in self.connection_probability_cache:
            self.connection_probability_cache[
                cell_type_specifiers] =\
                    self.get_pathway_property(
                        cell_type_specifiers,
                        self.get_connection_probability)
        return self.connection_probability_cache[cell_type_specifiers]
