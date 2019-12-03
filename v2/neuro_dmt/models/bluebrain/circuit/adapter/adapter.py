"""
Adapters for circuits from the Blue Brain Project.
"""

from copy import deepcopy
from collections.abc import Set, Mapping
from functools import wraps
import numpy as np
import pandas as pd
from dmt.tk.journal import Logger 
from dmt.model.interface import implements
from dmt.model.adapter import adapts
from dmt.tk.field import Field, lazyfield, WithFields 
from dmt.tk.collections import take
from neuro_dmt.analysis.circuit.composition.interfaces import\
    CellDensityAdapterInterface
from neuro_dmt.analysis.circuit.connectome.interfaces import\
    AfferentConnectionCountInterface
from neuro_dmt.models.bluebrain.circuit.model import\
    BlueBrainCircuitModel
from neuro_dmt import terminology
from neuro_dmt.models.bluebrain.circuit.geometry import Cuboid
from ..model.cell_type import CellType
from ..model.pathway import PathwaySummary
from .query import QueryDB, SpatialQueryData

logger = Logger(client=__file__)

def measurement_method(description):
    """
    Decorator to provide description about how an adapter method makes 
    measurements on the circuit model.
    """
    def decorated(adapter_method):
        adapter_method.__method__ = description
        return adapter_method

    return decorated

@implements(CellDensityAdapterInterface)
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
    logger = Field(
        """
        A logger to be used to log the activity of this code.
        """,
        __default_value__=Logger(client="BlueBrainCircuitAdapter"))

    # @lazyfield
    # def _random_position_generator_cache(self):
    #     """
    #     Cache random position generators.
    #     """
    #     return {}

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

    # def _query_hash(self, **kwargs):
    #     """
    #     Hash for a query.
    #     Keep only keyword arguments with non-None values.
    #     """
    #     def __hashable(xs):
    #         """
    #         Convert xs to a hashable type.
    #         """
    #         try:
    #             h = hash(xs)
    #             return xs
    #         except TypeError:
    #             return ','.join(str(x) for x in xs)

    #     return hash(tuple(sorted(
    #        ((key, __hashable(value))
    #          for key, value in kwargs.items()
    #          if value is not None),
    #         key=lambda xy: xy[0])))

    @lazyfield
    def visible_voxels(self):
        """
        If it is not masked, a voxel is visible.
        """
        def _get_visible_voxel_data(circuit_model, query):
            """..."""
            visible_voxel_ids ={
                tuple(ijk) for ijk in zip(*np.where( 
                    circuit_model.get_mask(
                        terminology.circuit.get_spatial_query(query))))}
            return SpatialQueryData(
                ids=pd.Series(
                    list(visible_voxel_ids), name="voxel_id"),
                positions=circuit_model.get_voxel_positions(
                    np.array(list(visible_voxel_ids))),
                cell_gids=pd.Series(
                    circuit_model.voxel_indexed_cell_gids.loc[
                        list(visible_voxel_ids.intersection(
                            circuit_model.voxel_indexed_cell_gids.index.values
                        ))
                    ]
                )
            )
        return QueryDB(_get_visible_voxel_data)

    def random_position(self,
            circuit_model,
            query):
        """
        Get a generator for random positions for given spatial parameters.
        """
        positions = self.visible_voxels(circuit_model, query).positions
        return positions.sample(n=1).iloc[0] if not positions.empty else None
            
        # spatial_query =\
        #     terminology.circuit.get_spatial_query(query)
        # voxel_mask =\
        #     circuit_model.atlas.get_mask(spatial_query)
        # if np.nansum(voxel_mask) == 0:
        #     raise StopIteration(
        #         """
        #         No valid voxels that satisfy spatial query: {}
        #         """.format(spatial_query))
        # voxel_indices = list(zip(*np.where(voxel_mask)))
        # while True:
        #     yield circuit_model.atlas.voxel_data.indices_to_positions(
        #         voxel_indices[np.random.randint(len(voxel_indices))])
        # if circuit_model not in self._random_position_generator_cache:
        #     self._random_position_generator_cache[circuit_model] = {}

        # if query_hash not in self._random_position_generator_cache[circuit_model]:
        #     self.random_position_generator_cache[circuit_model][query_hash] =\
        #         self._get_random_positions(circuit_model, **spatial_parameters)

        # return self._random_position_generator_cache[circuit_model][query_hash]

    def random_region_of_interest(self,
            circuit_model,
            query_dict):
        """
        Get a generator for random regions of interest for given spatial
        parameters.
        """
        random_position = self.random_position(circuit_model, query_dict)
        cuboid = lambda : Cuboid(
            random_position - self.bounding_box_size / 2.,
            random_position + self.bounding_box_size / 2.
        )
        return cuboid() if random_position is not None else None

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

    def get_method_description(self,
            name_measurement,
            sampling_methodology=terminology.sampling_methodology.random,
            **kwargs):
        """
        Describe methods.
        """
        try:
            measurement_method =\
                getattr(self, name_measurement)
        except AttributeError:
            try:
                measurement_method =\
                    getattr(self, "get_{}".format(name_measurement))
            except AttributeError:
                raise ValueError(
                    "Undescribed measurement method {}".format(name_measurement))

        return measurement_method.__method__.format(self.field_dict)

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

    @measurement_method("""
    =============================
    Exhaustive Methodology
    =============================
        Count of cells in all the voxcells confirming to a cell-query was divided by the total volume of these voxcells.
    =============================
    Random Sampling Methodology
    =============================
        Cells were counted in a box with sides of dimensions {bounding_box_size} um. Each cube was centered at a cell that was randomly sampled from  a population described by a cell-query.
    """)
    @terminology.require(
        *(terminology.circuit.terms + terminology.cell.terms)
    )
    def get_cell_density(self,
            circuit_model=None,
            sampling_methodology=terminology.sampling_methodology.random,
            **kwargs):
        """
        Get cell type density for either the `circuit_model` passed as a
        parameter or `self.circuit_model`.
        """
        circuit_model = self._resolve(circuit_model)
        query = terminology.cell.filter(
            **terminology.circuit.filter(**kwargs))

        if sampling_methodology != terminology.sampling_methodology.random:
            return self._get_cell_density_overall(circuit_model, query)

        random_roi = self.random_region_of_interest(circuit_model, query)
        if random_roi is None:
            return np.nan
        number_cells = circuit_model.get_cell_count(roi=random_roi)
        return number_cells/(1.e-9 * random_roi.volume)

    @measurement_method("""
    Fraction of inhibitory cells was computed in randomly sampled boxes of dimensions {bounding_box_size} um. 
    """)
    @terminology.require(*terminology.circuit.terms)
    def get_inhibitory_cell_fraction(self,
            circuit_model=None,
            sampling_methodology=terminology.sampling_methodology.random,
            **query):
        """
        Get fraction of inhibitory neurons in region of the brain specified by
        `query`
        """
        circuit_model = self._resolve(circuit_model)
        random_roi = self.random_region_of_interest(circuit_model, query)
        if random_roi is None:
            return np.nan
        cells_roi = circuit_model.get_cells(roi=random_roi)
        return(
            np.sum(cells_roi.synapse_class == "INH")
            / cells_roi.shape[0]
        )
    #@terminology.require(*(terminology.circuit.terms + terminology.cell.terms))
    def get_fiber_density(self,
            circuit_model=None,
            sampling_methodology=terminology.sampling_methodology.random,
            **kwargs):
        """
        Get density of dendritic and aboreal segments.
        """
        circuit_model =\
            self._resolve(
                circuit_model)
        query =\
            terminology.cell.filter(
                **terminology.circuit.filter(
                    **kwargs))
        if sampling_methodology != terminology.sampling_methodology.random:
            return self\
                ._get_fiber_density_overall(
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
                \t{}
                """.format(query))
            return np.nan

        number_segments = circuit_model\
            .get_segment_count(
                region=region_of_interest)
        return number_segments / (1.e-9 * region_of_interest.volume)

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
            """
        )
    def _resolve_sample_cells(self,
            circuit_model,
            cell_type,
            sampling_methodology,
            sample_size):
        """..."""
        cells_all =\
            circuit_model.get_cells(**cell_type)
        return\
            cells_all.sample(n=np.minimum(sample_size, cells_all.shape[0]))\
            if sampling_methodology==terminology.sampling_methodology.random\
            else cells_all

    def get_connection_probability(self,
            circuit_model=None,
            pre_synaptic={},
            post_synaptic={},
            upper_bound_soma_distance=None,
            sampling_methodology=terminology.sampling_methodology.random,
            sample_size_pre_synaptic_cells=20,
            sample_size_post_synaptic_cells=20,
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
            sample_size_pre_synaptic_cells=20,
            sample_size_post_synaptic_cells=20,
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
            sample_size_post_synaptic_cells=20,
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
            ).number_connections_afferent[
                "mean"
            ]
    def get_number_connections_afferent_by_soma_distance(self,
            circuit_model=None,
            pre_synaptic={},
            post_synaptic={},
            soma_distance_bins=None,
            sampling_methodology=terminology.sampling_methodology.random,
            sample_size_post_synaptic_cells=20,
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
            ).number_connections_afferent[
                "mean"
            ].rename(
                "number_connections_afferent"
            )
    @measurement_method("""
    Post-synaptic cells were sampled, given their cell-type. For example,
    when the post-synaptic cell is specified by it's mtype, a group
    of cells with the specified mtype is sampled.
    For each post-synaptic cell, it's afferent connections from all the 
    cells in the circuit were counted and grouped by their (specified)
    cell type (for example, the pre-synaptic cell's mtype). 
    """)
    def get_afferent_connection_count_summary(self,
            circuit_model=None,
            post_synaptic=None,
            pre_synaptic_cell_type_specifier=None,
            sampling_methodology=terminology.sampling_methodology.random,
            sample_size_post_synaptic_cells=100,
            by_soma_distance=True,
            as_series=True,
            **kwargs):
        """..."""
        circuit_model =\
            self._resolve(circuit_model)
        if post_synaptic is None:
            raise TypeError(
                """
                Missing required argument `post_synaptic_cell_type` in call to
                'get_afferent_connection_count_summary(..)'.
                """)
        if pre_synaptic_cell_type_specifier is None:
            pre_synaptic_cell_type_specifier =\
                frozenset(post_synaptic.keys())

        def _prefix_pre_synaptic(variable):
            return\
                ("pre_synaptic", variable)\
                if variable in pre_synaptic_cell_type_specifier\
                   else variable

        variables_groupby = [
            _prefix_pre_synaptic(variable)
            for variable in pre_synaptic_cell_type_specifier
        ]
        if by_soma_distance:
            variables_groupby.append(
                "soma_distance")

        def _summary_afferent(post_synaptic_cell):
            """..."""
            gids_afferent =\
                circuit_model.connectome.afferent_gids(
                    post_synaptic_cell.gid
                )

            def _soma_distance(pre_cells, bin_size=100):
                XYZ = ["x", "y", "z"]
                distance =\
                    np.linalg.norm(
                        pre_cells[XYZ] - post_synaptic_cell[XYZ],
                        axis=1)
                bin_starts = bin_size * np.floor(distance / bin_size)
                return [
                    bin_start + bin_size / 2
                    for bin_start in bin_starts]
                    
            variables_measurement =\
                dict(number_connections_afferent=1, soma_distance=_soma_distance)\
                if by_soma_distance else\
                   dict(number_connections_afferent=1)
            return\
                circuit_model.cells.loc[
                    gids_afferent
                ].assign(**
                    variables_measurement
                ).rename(
                    columns=_prefix_pre_synaptic
                )[
                    variables_groupby
                    + ["number_connections_afferent"]
                ].groupby(
                    variables_groupby
                ).agg("sum")
        
        post_synaptic_cells_all =\
            circuit_model.get_cells(
                **post_synaptic)
        post_synaptic_cells =\
            post_synaptic_cells_all.sample(n=sample_size_post_synaptic_cells)\
            if sampling_methodology == terminology.sampling_methodology.random\
               else post_synaptic_cells_all
        dataframe = pd.concat([
            _summary_afferent(post_synaptic_cell)
            for _, post_synaptic_cell in post_synaptic_cells.iterrows()
        ])
        return\
            dataframe.number_connections_afferent\
            if as_series else dataframe
