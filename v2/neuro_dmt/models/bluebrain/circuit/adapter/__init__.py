"""
Adapters for circuits from the Blue Brain Project.
"""

from copy import deepcopy
from collections.abc import Set, Mapping
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
from ..model.cell_type import CellType
from ..model.pathway import Pathway

logger = Logger(client=__file__)

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
        raise RuntimeError(
            "Execution of _resolve(...) should not have reached here.")

    def _resolve_cell_group(self,
            circuit_model=None,
            cell_group=None,
            sampling_methodology=terminology.sampling_methodology.random,
            resample=False,
            number=100):
        """

        Returns
        ---------
        pandas.DataFrame containing cells.
        """
        if cell_group is None:
            raise TypeError(
                """
                Missing required argument `cell_group`
                in call to _resolve_cell_group(...)
                """)
        circuit_model = self._resolve(circuit_model)
        other_args = dict(
            sampling_methodology=sampling_methodology,
            resample=resample,
            number=number)
        logger.study(
            logger.get_source_info(),
            """
            resolve cell group {}
            given that {}
            """.format(
                cell_group,
                other_args))
        if cell_group is None:
            return self._resolve_cell_group(
                circuit_model.cells,
                **other_args)
        if isinstance(cell_group, np.ndarray):
            return self._resolve_cell_group(
                circuit_model.cells.loc[cell_group],
                **other_args)
        if isinstance(cell_group, pd.Series):
            return self._resolve_cell_group(
                cell_group.to_dict(),
                **other_args)
        if isinstance(cell_group, Mapping):
            return self._resolve_cell_group(
                circuit_model.get_cells(**cell_group))

        if isinstance(cell_group, pd.DataFrame):
            result = cell_group\
                if (sampling_methodology!=terminology.sampling_methodology.random
                    or cell_group.shape[1] > number - 1
                ) else (
                    cell_group.sample(n=number)\
                    if number < cell_group.shape[0]\
                    else cell_group)
            logger.study(
                logger.get_source_info(),
                """
                Final result for cell group, dataframe with shape {}
                """.format(
                    result.shape))
            return result
                    
        raise NotImplementedError(
            """
            '_resolve_cell_group' not implemented for argument `cell_group`
            value {} of type {}.
            """.format(
                cell_group,
                type(cell_group)))


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

    @terminology.require(*(terminology.circuit.terms + terminology.cell.terms))
    def get_cell_density(self,
            circuit_model=None,
            sampling_methodology=terminology.sampling_methodology.random,
            **kwargs):
        """
        Get cell type density for either the `circuit_model` passes as a
        parameter or `self.circuit_model`.
        """
        circuit_model = self._resolve(circuit_model)
        query = terminology.cell.filter(
            **terminology.circuit.filter(**kwargs))
        if sampling_methodology != terminology.sampling_methodology.random:
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
                no more random regions of interest for query:
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
            cell_group=None):
        """
        Arguments
        ---------------
        cell_group : An object that specifies cell groups.
        ~   This may be 
        ~   1. Either a frozen-set of strings that represent cell properties.
        ~   2. Or, a mapping from cell properties to their values.

        Returns
        ------------
        pandas.DataFrame with nested columns, with two columns 
        `(pre_synaptic, post_synaptic)` at the 0-th level.
        Under each of these two columns should be one column each for
        the cell properties specified in the `cell_group` when it is a
        set, or its keys if it is a mapping.
        ~   1. When `cell_group` is a set of cell properties, pathways between
        ~      all possible values of these cell properties.
        ~   2. When `cell-group` is a mapping, pathways between cell groups
        ~      that satisfy the mapping values.
        """
        circuit_model = self._resolve(circuit_model)
        if isinstance(cell_group, Set) :
            return\
                circuit_model.pathways(
                    cell_type_specifier=cell_group)
        if isinstance(cell_group, pd.DataFrame):
            return\
                circuit_model.pathways(
                    cell_types=cell_group)
        raise TypeError(
            """
            `get_pathways(...)` argument `cell_group` is neither a set of
            cell properties, nor a `pandas.DataFrame` specifying cell types.
            """)

    def _resolve_sample_cells(self,
            circuit_model,
            cell_type,
            sampling_methodology,
            sample_size):
        """..."""
        cells_all =\
            circuit_model.get_cells(**cell_type)
        return\
            cells_all.sample(
                n=np.minimum(
                    sample_size,
                    cells_all.shape[0])
            ) if sampling_methodology==terminology.sampling_methodology.random\
            else cells_all

    def get_connection_probability(self,
            circuit_model=None,
            pre_synaptic={},
            post_synaptic={},
            upper_bound_soma_distance=None,
            sampling_methodology=terminology.sampling_methodology.random,
            sample_size_pre_synaptic_cells=100,
            sample_size_post_synaptic_cells=100,
            **kwargs):
        """
        Arguments
        -----------
        `pre_synaptic_cell_type` : pandas.Series specifying the
        type of the cells on the pre-synaptic side.
        `post_synaptic_cell_type`: pandas.Series specifying the
        type of the cells on the post-synaptic side.
        """
        circuit_model =\
            self._resolve(circuit_model)
        pre_synaptic_cells =\
            self._resolve_sample_cells(
                circuit_model,
                pre_synaptic,
                sampling_methodology,
                sample_size_pre_synaptic_cells)
        post_synaptic_cells =\
            self._resolve_sample_cells(
                circuit_model,
                post_synaptic,
                sampling_methodology,
                sample_size_post_synaptic_cells)
        return\
            circuit_model.pathway_summary.probability_connection(
                pre_synaptic_cells,
                post_synaptic_cells,
                with_soma_distance=False
            ).probability_connection

    @property
    def _soma_distance_mid_point(self):
        return lambda df: df.soma_distance.apply(np.mean)

    def get_connection_probability_by_soma_distance(self,
            circuit_model=None,
            pre_synaptic={},
            post_synaptic={},
            soma_distance_bins=None,
            sampling_methodology=terminology.sampling_methodology.random,
            sample_size_pre_synaptic_cells=100,
            sample_size_post_synaptic_cells=100,
            **kwargs):
        """
        Since the plotter needs a numeric column, we have to convert the
        soma-distance bin tuples obtained from the model to floats.
        See the hack below.
        """
        if soma_distance_bins is not None:
            raise NotImplementedError(
                """
                Not yet implemented for custom values of `soma_distance_bins`.
                """)
        circuit_model =\
            self._resolve(circuit_model)
        pre_synaptic_cells =\
            self._resolve_sample_cells(
                circuit_model,
                pre_synaptic,
                sampling_methodology,
                sample_size_pre_synaptic_cells)
        post_synaptic_cells =\
            self._resolve_sample_cells(
                circuit_model,
                post_synaptic,
                sampling_methodology,
                sample_size_post_synaptic_cells)
        return\
            circuit_model.pathway_summary.probability_connection(
                pre_synaptic_cells,
                post_synaptic_cells,
                with_soma_distance=True
            ).reset_index(
            ).assign(
                soma_distance=self._soma_distance_mid_point
            ).set_index(
                "soma_distance"
            ).probability_connection

    def get_number_connections_afferent(self,
            circuit_model=None,
            pre_synaptic={},
            post_synaptic={},
            soma_distance_bins=None,
            sampling_methodology=terminology.sampling_methodology.random,
            sample_size_post_synaptic_cells=100,
            **kwargs):
        """..."""
        if soma_distance_bins is not None:
            raise NotImplementedError(
                """
                Not yet implemented for custom values of `soma_distance_bins`.
                """)
        circuit_model =\
            self._resolve(circuit_model)
        pre_synaptic_cells =\
            circuit_model.get_cells(**pre_synaptic)
        post_synaptic_cells =\
            self._resolve_sample_cells(
                circuit_model,
                post_synaptic,
                sampling_methodology,
                sample_size_post_synaptic_cells)
        return\
            circuit_model.pathway_summary.number_connections_afferent(
                pre_synaptic_cells,
                post_synaptic_cells,
                with_soma_distance=False
            ).number_connections_afferent["mean"]

    def get_number_connections_afferent_by_soma_distance(self,
            circuit_model=None,
            pre_synaptic={},
            post_synaptic={},
            soma_distance_bins=None,
            sampling_methodology=terminology.sampling_methodology.random,
            sample_size_post_synaptic_cells=100,
            **kwargs):
        """..."""
        if soma_distance_bins is not None:
            raise NotImplementedError(
                """
                Not yet implemented for custom values of `soma_distance_bins`.
                """)
        circuit_model =\
            self._resolve(circuit_model)
        pre_synaptic_cells =\
            circuit_model.get_cells(**pre_synaptic)
        post_synaptic_cells =\
            self._resolve_sample_cells(
                circuit_model,
                post_synaptic,
                sampling_methodology,
                sample_size_post_synaptic_cells)
        return\
            circuit_model.pathway_summary.number_connections_afferent(
                pre_synaptic_cells,
                post_synaptic_cells,
                with_soma_distance=True
            ).reset_index(
            ).assign(
                soma_distance=self._soma_distance_mid_point
            ).set_index(
                "soma_distance"
            ).number_connections_afferent["mean"]

    def get_afferent_connections_summary(self,
            circuit_model=None,
            post_synaptic_cell_type=None,
            pre_synaptic_cell_type_specifier=None,
            sampling_methodology=terminology.sampling_methodology.random,
            sample_size=100):
        """
        Statistical summary of the number of afferent connection counts.
        """
        if not pre_synaptic_cell_type_specifier:
            pre_synaptic_cell_type_specifier =\
                list(post_synaptic_cell_type.keys())

        circuit_model =\
            self._resolve(circuit_model)
        post_synaptic_cells =\
            circuit_model.get_cells(
                **post_synaptic_cell_type)
        post_synaptic_gids =\
            post_synaptic_cells.gid\
            if sampling_methodology == terminology.sampling_methodology.random\
               else post_synaptic_cells.sample(n=sample_size).gid
        afferent_gids =\
            post_synaptic_gids.apply(
                circuit_model.connectome.afferent_gids
            ).rename()

        def _statistical_summary(pre_synaptic_cells):
            return\
                afferent_gids.apply(
                    lambda gids: np.sum(np.in1d(
                        pre_synaptic_cells.gid.values,
                        gids))
                ).agg(
                    ["size", "mean", "std"]
                )
        return\
            circuit_model.cells.groupby(
                list(pre_synaptic_cell_type_specifier)
            ).apply(
                _statistical_summary
            ).reset_index(
            ).rename(
                columns={
                    variable: "pre_synaptic_{}".format(variable)
                    for variable in pre_synaptic_cell_type_specifier}
            ).set_index([
                "pre_synaptic_{}".format(variable) 
                for variable in pre_synaptic_cell_type_specifier
            ])

    def get_efferent_connections_summary(self,
            circuit_model=None,
            pre_synaptic_cell_type=None,
            post_synaptic_cell_type_specifier=None,
            sampling_methodology=terminology.sampling_methodology.random,
            sample_size=100):
        """
        Statistical summary of the number of afferent connection counts.
        """
        if not post_synaptic_cell_type_specifier:
            post_synaptic_cell_type_specifier =\
                list(pre_synaptic_cell_type.keys())

        circuit_model =\
            self._resolve(circuit_model)
        pre_synaptic_cells =\
            circuit_model.get_cells(
                **pre_synaptic_cell_type)
        pre_synaptic_gids =\
            pre_synaptic_cells.gid\
            if sampling_methodology == terminology.sampling_methodology.random\
               else pre_synaptic_cells.sample(n=sample_size).gid
        efferent_gids =\
            pre_synaptic_gids.apply(
                circuit_model.connectome.efferent_gids
            ).rename()

        def _statistical_summary(post_synaptic_cells):
            return\
                efferent_gids.apply(
                    lambda gids: np.sum(np.in1d(
                        post_synaptic_cells.gid.values,
                        gids))
                ).agg(
                    ["size", "mean", "std"]
                )
        return\
            circuit_model.cells.groupby(
                list(post_synaptic_cell_type_specifier)
            ).apply(
                _statistical_summary
            ).reset_index(
            ).rename(
                columns={
                    variable: "post_synaptic_{}".format(variable)
                    for variable in post_synaptic_cell_type_specifier}
            ).set_index([
                "post_synaptic_{}".format(variable) 
                for variable in post_synaptic_cell_type_specifier
            ])

