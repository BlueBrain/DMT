"""
A class that represents circuit models developed at the Blue Brain Project.
"""

import os
from copy import deepcopy
import yaml
import numpy as np
import pandas as pd
import neurom
import bluepy
from bluepy.v2.circuit import Circuit as BluePyCircuit
from bluepy.exceptions import BluePyError
from bluepy.v2.enums import Cell, Segment, Section
from dmt.tk import collections
from dmt.tk.field import Field, lazyfield, WithFields
from dmt.tk.journal import Logger
from dmt.tk.collections import take
from neuro_dmt import terminology
from ..atlas import BlueBrainCircuitAtlas
from .cell_type import CellType
from .pathway import PathwaySummary

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

class CircuitProvenance(WithFields):
    """
    Provenance of a circuit.
    """
    label = Field(
        """
        A label that names the circuit model.
        """)
    authors = Field(
        """
        A list of authors who built the circuit model.
        """)
    release_date = Field(
        """
        When the circuit model was released in its final form.
        """)
    uri = Field(
        """
        URI from where the circuit model can be loaded.
        """)
    animal = Field(
        """
        The animal whose brain was modeled.
        """)
    age = Field(
        """
        Age of the animal at which its brain was modeled.
        """)
    brain_region = Field(
        """
        Brain region that was modeled.
        """)

class BlueBrainCircuitModel(WithFields):
    """
    A circuit model developed at the Blue Brain Project.
    """
    provenance = Field(
        """
        `CircuitProvenance` instance describing the circuit model
        """,
        __default_value__=CircuitProvenance(
            label="BlueBrainCircuitModel",
            authors=["BBP Team"],
            release_date="Not Available",
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
        Path to the location of this circuit's data. This data is loaded as a
        BluePy circuit if a Bluepy circuit is not provided at initialization.
        """,
        __default_value__="not-available")
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

    @lazyfield
    def pathway_summary(self):
        """
        Get a summary for a pathway in the circuit.
        """
        return PathwaySummary(circuit_model=self)

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
        try:
            return BlueBrainCircuitAtlas(
                self.bluepy_circuit.atlas
            )
        except AttributeError:
            return BlueBrainCircuitAtlas(
                path=self.bluepy_circuit.atlas.dirpath
            )
        raise RuntimeError(
            """
            Execution of `.atlas(...)` should not have reached here.
            """
        )
    @lazyfield
    def cell_collection(self):
        """
        Cells for the circuit.
        """
        try:
            bp = self.bluepy_circuit
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
        cells = self.cell_collection.get()
        return cells.assign(gid=cells.index.values)

    @lazyfield
    def connectome(self):
        """
        Connectome for the circuit.
        """
        try:
            bp = self.bluepy_circuit
            return bp.connectome
        except BluePyError as error:
            logger.warn(
                logger.get_source_info(),
                "Circuit does not have a connectome.",
                "BluePy complained: \n\t {}".format(error))
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
        return self.atlas.layers

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

    @lazyfield
    def voxel_cell_count(self):
        """
        A pandas.Series providing cell counts in each voxel ---
        indexed by a tuple representing the voxel indices.

        Returns
        -----------
        A numpy.ndarray of the same dimensions as `self.atlas` voxel data.
        """
        return self.atlas.get_bin_counts(self.cells)

    @lazyfield
    def voxel_indexed_cell_gids(self):
        """
        A pandas series mapping a cell's gid to it's voxel index.
        """
        return pd.Series(
            self.cells.index.values,
            index=pd.Series(
                list(
                    self.atlas.voxel_data.positions_to_indices(
                        self.cells[[Cell.X, Cell.Y, Cell.Z]].values)
                )
            ).apply(tuple)
        )
    def get_voxel_positions(self, voxel_ids):
        """
        Get positions of voxels from the atlas.

        Arguments
        -----------
        voxel_ids : Iterable of voxel indices as tuples (i, j, k)
        """
        return pd.DataFrame(
            self.atlas.indices_to_positions(voxel_ids),
            columns=[Cell.X, Cell.Y, Cell.Z],
            index=pd.MultiIndex.from_arrays(
                [voxel_ids[:,0], voxel_ids[:, 1], voxel_ids[:, 2]],
                names=["i", "j", "k"])
        )
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

    @terminology.use(*(terminology.circuit.terms + terminology.cell.terms))
    def _resolve_query_region(self, **query):
        """
        Resolve region in query.

        Arguments
        ------------
        query : a dict providing parameters for a circuit query.
        """
        if not (terminology.circuit.roi in query
            or (terminology.circuit.region in query
                 and not isinstance(query[terminology.circuit.region], str)
            )
        ):
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
                        terminology.circuit.region, region)
                )
        else:
            roi = query.pop(terminology.circuit.region)

        corner_0, corner_1 = _get_bounding_box(roi)
        query.update({
            Cell.X: (corner_0[0], corner_1[0]),
            Cell.Y: (corner_0[1], corner_1[1]),
            Cell.Z: (corner_0[2], corner_1[2])})
        return query

    def _get_cell_query(self, **query):
        """
        Convert `query` that will be accepted by a `BluePyCircuit`.
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
            return None

        cell_query = terminology.circuit.filter(
            **terminology.cell.filter(**query))

        if terminology.circuit.layer in cell_query:
            cell_query[terminology.circuit.layer] =\
                _get_query_layer(cell_query[terminology.circuit.layer])

        return cell_query

    @terminology.use(*(
        terminology.circuit.terms +
        terminology.cell.terms))
    def get_cells(self, properties=None, with_gid_column=True, **query):
        """
        Get cells in a region, with requested properties.

        Arguments
        --------------
        properties : single cell property or  list of cell properties to fetch.
        query : sequence of keyword arguments providing query parameters.
        with_gid_column : if True add a column for cell gids.
        """
        cell_query = self._get_cell_query(
            **self._resolve_query_region(**query))
        cells = self.cell_collection.get(
            group=cell_query,
            properties=properties)
        return cells.assign(gid=cells.index.values)\
            if with_gid_column\
               else cells

    @terminology.use(*(
        terminology.circuit.terms +
        terminology.cell.terms))
    def get_cell_count(self, **query):
        """..."""
        return self.get_cells(**query).shape[0]

    def get_mask(self, query):
        """
        Get a mask from the atlas.
        """
        return self.atlas.get_mask(
            **terminology.circuit.get_spatial_query(query))

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

    # @terminology.use(
    #     terminology.circuit.region,
    #     terminology.circuit.layer,
    #     terminology.circuit.depth,
    #     terminology.circuit.height,
    #     terminology.cell.mtype,
    #     terminology.cell.etype,
    #     terminology.cell.synapse_class)
    # def random_positions(self,
    #         as_array=False,
    #         **query_parameters):
    #     """
    #     Generate random positions (as np.array([x, y, z])) in a region defined
    #     by spatial parameters in the query.
    #     """
    #     depth_query =\
    #         query_parameters.pop(
    #             terminology.circuit.depth, None)
    #     height_query =\
    #         query_parameters.pop(
    #             terminology.circuit.height, None)
    #     region_query =\
    #         query_parameters.pop(
    #             terminology.circuit.region, None)
    #     layer_query =\
    #         query_parameters.pop(
    #             terminology.circuit.layer, None)
    #     mask =\
    #         self.atlas.get_mask(
    #             region=region_query,
    #             layer=layer_query,
    #             depth=depth_query,
    #             height=height_query)

    # def random_positions_from_cells(self,
    #         as_array=False,
    #         **query_parameters):
    #     """
    #     Generate random positions (as np.array([x, y, z])) in a region defined
    #     by spatial parameters in the query.
    #     """
    #     cells = self.get_cells(
    #         properties=XYZ,
    #         with_gid_column=False,
    #         **query_parameters)
    #     while cells.shape[0] > 0:
    #         position = cells.sample(n=1).iloc[0]
    #         yield position.values if as_array else position

    def are_connected(self, pre_neuron, post_neuron):
        """
        Is pre neuron connected to post neuron.
        """
        return pre_neuron in self.connectome.afferent_gids(post_neuron)

    def get_afferent_ids(self, neuron):
        """..."""
        return self.connectome.get_afferent_ids(neuron)

    # def random_pathway_pairs(self,
    #         pre_cell_type={},
    #         post_cell_type={}):
    #     """
    #     Generate random pairs of neurons in a given pathway.
    #     """
    #     pre_neurons =\
    #         self.cell_collection\
    #             .ids(group=self._get_cell_query(**pre_cell_type))
    #     post_neurons =\
    #         self.cell_collection\
    #             .ids(group=self._get_cell_query(**post_cell_type))
    #     while len(pre_neurons) > 0:
    #         pre_neuron = np.random.sample(pre_neurons)
    #         while len(post_neurons) > 0:
    #             post_neuron = np.random.sample(post_neurons)
    #             yield (pre_neuron, post_neuron)

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

    

    def get_connection_probability(self,
            pre_cell_type_specifier,
            post_cell_type_specifier):
        """
        Compute connection probability once for either the entire
        circuit, or samples of afferent, or samples of  efferent,
        or samples of both efferent and afferent cells.
        """
        labels_pre_specifier =[
            "pre_synaptic_{}".format(c)
            for c in pre_cell_type_specifier]
        labels_post_specifier = [
            "post_synaptic_{}".format(c)
            for c in post_cell_type_specifier]
        cells = self.cells

        def _get_summary_connections(post_cell):
            return cells[
                list(pre_cell_type_specifier)
            ].rename(
                columns="pre_synaptic_{}".format
            ).assign(
                number_pairs=np.in1d(
                    self.cells.index.values,
                    self.connectome.afferent_gids(post_cell.gid))
            ).groupby(
                labels_pre_specifier
            ).agg(
                ["size", "sum"]
            ).rename(
                columns={"size": "total", "sum": "connected"}
            ).assign(**{
                "post_synaptic_{}".format(p): post_cell[p] 
                for p in post_cell_type_specifier}
            ).reset_index(
            ).set_index(list(
                labels_pre_specifier + labels_post_specifier)
            )

        def _connection_probability(summary):
            """
            Compute connection probability between pairs
            """
            return summary.number_pairs.connected / summary.number_pairs.total

        return pd.concat(
            [_get_summary_connections(post_cell)
             for _, post_cell in cells.iterrows()]
        ).groupby(list(
            labels_pre_specifier + labels_post_specifier)
        ).agg(
            "sum"
        ).assign(
            connection_probability=_connection_probability )

    @lazyfield
    def segment_index(self):
        """..."""
        return self.morph.spatial_index

    def get_segment_length_by_neurite_type(self,
            region_of_interest):
        """..."""
        if not self.segment_index:
            return None

        corner_0, corner_1 =\
            region_of_interest.bbox
        dataframe_segment =\
            self.segment_index\
                .q_window_oncenter(
                    corner_0,
                    corner_1
                ).assign(
                    length=lambda segments: np.linalg.norm(
                        segments[[Segment.X1, Segment.Y1, Segment.Z1]].values
                        - segments[[Segment.X2, Segment.Y2, Segment.Z2]].values
                    )
                )

        def _total_length(neurite_type):
            return np.sum(
                dataframe_segment.length[
                    dataframe_segment[Section.NEURITE_TYPE] == neurite_type
                ].values
            )
        return pd.Series({
            neurom.AXON: _total_length(neurom.AXON),
            neurom.BASAL_DENDRITE: _total_length(neurom.BASAL_DENDRITE),
            neurom.APICAL_DENDRITE: _total_length(neurom.APICAL_DENDRITE)
        })

    def get_segment_length_densities_by_mtype(self,
            region_of_interest):
        """..."""
        if not self.segment_index:
            return None

        def _get_length(segments):
            """
            Compute total length of segments.
            """
            return\
                np.linalg.norm(
                    segments[[Segment.X1, Segment.Y1, Segment.Z1]]
                    - segments[[Segment.X2, Segment.Y2, Segment.Z2]])

        corner_0, corner_1 =\
            region_of_interest.bbox
        dataframe_segments = self\
            .segment_index\
            .q_window_oncenter(
                corner_0,
                corner_1)\
            .assign(
                length=_get_length)\
            .set_index("gid")\
            .join(
                self.cells[
                    Cell.MTYPE]
            ).groupby(
                u'mtype'
            ).apply(
                lambda segments: {
                    neurom.AXON: np.sum(
                        segments.length[
                            segments[Section.NEURITE_TYPE] == neurom.AXON
                        ]).values / region_of_interest.volume,
                    neurom.BASAL_DENDRITE: np.sum(
                        segments.length[
                            segments[Section.NEURITE_TYPE] == neurom.BASAL_DENDRITE
                        ]).values / region_of_interest.volume,
                    neurom.APICAL_DENDRITE: np.sum(
                        segments.length[
                            segments[Section.NEURITE_TYPE] == neurom.APICAL_DENDRITE
                        ]).values / region_of_interest.volume
                }
            )
