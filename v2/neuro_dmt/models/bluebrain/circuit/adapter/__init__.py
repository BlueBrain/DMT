"""
Adapters for circuits from the Blue Brain Project.
"""

from copy import deepcopy
import numpy as np
import pandas as pd
from dmt.tk.journal import Logger 
from dmt.model.interface import implements
from dmt.model.adapter import adapts
from dmt.tk.field import Field, WithFields 
from dmt.tk.collections import take
from neuro_dmt.analysis.circuit.composition.interfaces import\
    CellDensityAdapterInterface
from neuro_dmt.analysis.circuit.connectome.interfaces import\
    ConnectomeAdapterInterface
from neuro_dmt.models.bluebrain.circuit.model import\
    BlueBrainCircuitModel
from neuro_dmt import terminology
from neuro_dmt.models.bluebrain.circuit.geometry import Cuboid


@implements(CellDensityAdapterInterface)
@implements(ConnectomeAdapterInterface)
@adapts(BlueBrainCircuitModel)
class BlueBrainCircuitAdapter(WithFields):
    """
    Adapt a circuit from the Blue Brain Project.
    """
    circuit_model = Field(
        """
        The circuit model instance adapted by this `Adapter` instance.
        While not required, attaching a circuit model instance to this
        `Adapter` instance allows us to define an instance of an adapted
        circuit model.
        """,
        __required__=False)
    sample_size = Field(
        """
        Number of samples to make measure a circuit phenomenon.
        """,
        __default_value__=20)
    bounding_box_size = Field(
        """
        Dimensions of the bounding box to sample spatial regions inside
        the circuit.
        """,
        __default_value__=50. * np.ones(3))
    random_position_generator = Field(
        """
        A (nested) dict mapping circuit, and a spatial query to their
        random position generator. 
        """,
        __default_value__={})
    logger = Field(
        """
        A logger to be used to log the activity of this code.
        """,
        __default_value__=Logger(client="BlueBrainCircuitAdapter"))

    def for_circuit_model(self, circuit_model, **kwargs):
        """
        Instance of this BlueBrainModelAdapter prepared for a circuit model.
        """
        other = deepcopy(self)
        other.circuit_model = circuit_model
        return other

    def _resolve(self, circuit_model):
        """
        Result the circuit model to adapt.
        """
        if circuit_model:
            return circuit_model

        try:
            return self.circuit_model
        except AttributeError:
            raise AttributeError(
            """
            Attribute `circuit_model` was not set for this `Adapter` instance.
            You may still use this `Adapter` by explicitly passing a
            `circuit_model` instance as an argument to the `AdapterInterface`
            methods it adapts.
            """)

    def _query_hash(self, **kwargs):
        """
        Hash for a query.
        Keep only keyword arguments with non-None values.
        """
        def __hashable(xs):
            """
            Convert xs to a hashable type.
            """
            try:
                h = hash(xs)
                return xs
            except TypeError:
                return ','.join(str(x) for x in xs)

        return hash(tuple(sorted(
           ((key, __hashable(value))
             for key, value in kwargs.items()
             if value is not None),
            key=lambda xy: xy[0])))

    def random_positions(self,
            circuit_model,
            **spatial_parameters):
        """
        Get a generator for random positions for given spatial parameters.
        """
        if circuit_model not in self.random_position_generator:
            self.random_position_generator[circuit_model] = {}

        query_hash =\
            self._query_hash(**spatial_parameters)
        if query_hash not in self.random_position_generator[circuit_model]:
            self.random_position_generator[circuit_model][query_hash] =\
                circuit_model.random_positions(**spatial_parameters)

        return self.random_position_generator[circuit_model][query_hash]

    def random_region_of_interest(self,
            circuit_model,
            **spatial_parameters):
        """
        Get a generator for random regions of interest for given spatial
        parameters.
        """
        return (
            Cuboid(
                position - self.bounding_box_size / 2.,
                position + self.bounding_box_size / 2.)
            for position in self.random_positions(
                    circuit_model,
                    **spatial_parameters))

    def random_pathway_pairs(self,
            circuit_model,
            **pathway_parameters):
        """
        Random pairs of neurons in a pathway.
        """
        if circuit_model not in self.random_pairs_generator:
            self.random_pairs_generator[circuit_model] = {}

        query_hash =\
            self._query_hash(**pathway_parameters)
        if query_hash not in self.random_pathway_pairs_generator[circuit_model]:
            self.random_pathway_pairs[circuit_model][query_hash] =\
                circuit_model.random_pathway_pairs(**pathway_parameters)

        return self.random_pathway_pairs_generator[circuit_model][query_hash]

    def get_label(self,
            circuit_model):
        """..."""
        return self._resolve(circuit_model).label

    def _get_cell_density_overall(self,
            circuit_model=None,
            **query_parameters):
        """
        Get cell density over the entire relevant volume.

        Pass only keyword arguments that are accepted for cell queries by
        the circuit model.
        """
        query_spatial = {
            key: query_parameters[key]
            for key in ["region", "layer", "depth", "height"]
            if key in query_parameters}
        circuit_model = self._resolve(circuit_model)
        count_cells = circuit_model.get_cell_count(**query_spatial)
        count_voxels = circuit_model.atlas.get_voxel_count(**query_spatial)
        return count_cells/(count_voxels*1.e-9*circuit_model.atlas.volume_voxel)

    @terminology.use(*(terminology.circuit.terms + terminology.cell.terms))
    def get_cell_density(self,
            circuit_model=None,
            mtype=None,
            etype=None,
            region=None,
            layer=None,
            depth=None,
            height=None,
            mesocolumn=None,
            hypercolumn=None,
            synapse_class=None,
            postsynaptic=None,
            presynaptic=None,
            measurement_method=terminology.measurement_method.random_sampling):
        """
        Get cell type density for either the `circuit_model` passes as a
        parameter or `self.circuit_model`.
        """
        circuit_model = self._resolve(circuit_model)
        query = terminology.cell.filter(
            **terminology.circuit.filter(
                mtype=mtype,
                etype=etype,
                region=region,
                layer=layer,
                depth=depth,
                height=height))
        if measurement_method != terminology.measurement_method.random_sampling:
            return self._get_cell_density_overall(
                circuit_model,
                **query)
        try:
            region_of_interest = next(
                self.random_region_of_interest(
                    circuit_model,
                    **query))
        except StopIteration:
            self.logger.warn(
                self.logger.get_source_info(),
                """
                No more random regions of interest for query:
                \t{}""".format(query))
            return np.nan

        number_cells = circuit_model\
            .get_cell_count(
                region=region_of_interest)
        return number_cells / (1.e-9 * region_of_interest.volume)

    def get_mtypes(self,
            circuit_model=None):
        """
        All the mtypes...
        """
        circuit_model = self._resolve(circuit_model)
        return circuit_model.mtypes

    def get_pathways(self,
            circuit_model=None,
            cell_type_specifier=("mtype", )):
        """
        Arguments
        ---------------
        cell_type_specifier : An object that specifies cell groups.
        Examples:
        1. A tuple of strings representing cell properties. When each tuple is
        coupled with a value, the resulting key-value pairs specify a
        group of neurons in the circuit.
        """
        circuit_model = self._resolve(circuit_model)
        cell_types =\
            circuit_model.get_cell_types(cell_type_specifier)
        cell_types_at =\
            lambda pos: cell_types.rename(**{
                column: "{}_{}".format(pos, column)
                for column in cell_types.columns})
        pre_types = cell_types_at("pre")
        post_types = cell_types_at("post")
        return pd.concat([pre_types, post_types], axis=1)

    def get_connection_probability(self,
            circuit_model=None,
            pre_mtype=None,
            post_mtype=None,
            sample_size=20):
        """..."""
        circuit_model = self._resolve(circuit_model)
        return\
            circuit_model.connection_probability(("mtype",))\
                         .loc[(pre_mtype, post_mtype)]
