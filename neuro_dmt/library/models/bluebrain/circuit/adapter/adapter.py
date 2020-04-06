# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published 
# by the Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

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
from dmt.tk.field import Field, lazyfield, WithFields 
from dmt.tk.collections import get_list
from neuro_dmt.analysis.circuit.composition.interfaces import\
    CellDensityAdapterInterface
from neuro_dmt.library.models.bluebrain.circuit.model import\
    BlueBrainCircuitModel
from neuro_dmt import terminology
from neuro_dmt.library.models.bluebrain.circuit.geometry import Cuboid
from ..model.cell_type import CellType
from ..model.pathway import PathwaySummary
from .query import QueryDB, SpatialQueryData

LOGGER = Logger(client=__file__)

XYZ = ["x", "y", "z"]

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
        LOGGER.study(
            LOGGER.get_source_info(),
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
            LOGGER.study(
                LOGGER.get_source_info(),
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
            if sampling_methodology == terminology.sampling_methodology.random\
            else cells_all

    def get_provenance(self,
            circuit_model=None):
        """..."""
        circuit_model = self._resolve(circuit_model)
        return circuit_model.provenance.field_dict

    def get_brain_regions(self,
            circuit_model=None):
        """
        Brain regions that were populated with cells in the circuit model.
        """
        circuit_model = self._resolve(circuit_model)
        return circuit_model.brain_regions

    def get_layers(self,
            circuit_model=None):
        """
        All the layers in the circuit model.

        Returns
        ==============
        A list of layers.
        None, if layers are not defined.
        """
        circuit_model = self._resolve(circuit_model)
        return circuit_model.layers

    def get_mtypes(self,
            circuit_model=None):
        """
        All the mtypes...
        """
        circuit_model = self._resolve(circuit_model)
        return circuit_model.mtypes

    def get_etypes(self,
                   circuit_model=None):
        """..."""
        circuit_model = self._resolve(circuit_model)
        return circuit_model.etypes

    def mtype_to_morphology(self,
            circuit_model=None,
            mtypes=[]):
        """..."""
        return [mtype.split('_')[-1] for mtype in mtypes]

    def get_cell_types(self,
            circuit_model=None,
            query=None):
        """
        Get cell-types for the given specifiers.

        Arguments
        -------------
        query :: Either an iterable of unique cell type specifiers
        ~        Or a mapping cell_type_specifier --> value / list(value)

        Returns
        ----------
        A `pandas.DataFrame` containing all cell-types,
        each row providing values for each cell type specifier.
        """
        if query is None:
            raise TypeError(
                """
                Missing argument query. Please pass a query:
                1. Either a tuple of cell type specifiers
                2. Or a Mapping cell_type_specifier --> value / list(value)
                """)
        circuit_model = self._resolve(circuit_model)
        def __values(variable):
            try:
                raw_values = query[variable]
            except (TypeError, KeyError):
                try:
                    get_values = getattr(self,  "get_{}s".format(variable))
                except AttributeError as error:
                    raise AttributeError(
                        """
                        {} adapter does not implement a getter for cell property
                        {}.
                        """.format(self.__class__.__name__, variable))
                raw_values = get_values(circuit_model)

            return get_list(raw_values)

        def _get_tuple_values(params):
            """..."""
            if not params: return [[]]

            head_tuples =[
                [(params[0], value)]
                for value in __values(params[0])]
            tail_tuples =\
                _get_tuple_values(params[1:])
            return[
                h + t for h in head_tuples
                for t in tail_tuples]

        try:
            cell_type_specifiers = list(query.keys())
        except AttributeError:
            cell_type_specifiers = tuple(query)

        return pd.DataFrame([
            dict(row)
            for row in _get_tuple_values(tuple(cell_type_specifiers))])

    def get_pathways(self,
            circuit_model=None,
            pre_synaptic=None,
            post_synaptic=None):
        """
        Arguments
        ---------------
        pre_synaptic :: Either an iterable of unique cell type specifiers 
        ~               (a.k.a cell properties)
        ~               Or a mapping `cell_type_specifier-->value`
        post_synaptic :: Either an iterable of unique cell type specifiers 
        ~               (a.k.a cell properties)
        ~               Or a mapping `cell_type_specifier-->value`
        """
        circuit_model = self._resolve(circuit_model)
        if pre_synaptic is None:
            if post_synaptic is None:
                raise TypeError(
                    """
                    Missing arguments. Pass at least one of:
                    1. pre_synaptic
                    2. post_synaptic
                    """)
            pre_synaptic = post_synaptic
        else:
            if post_synaptic is None:
                post_synaptic = pre_synaptic

        def _at(synaptic_location, cell_type):
            return\
                pd.concat(
                    [cell_type],
                    axis=1,
                    keys=["{}_synaptic".format(synaptic_location)])

        pre_synaptic_cell_types =\
            _at("pre",
                self.get_cell_types(circuit_model, pre_synaptic))
        post_synaptic_cell_types =\
            _at("post",
                self.get_cell_types(circuit_model, post_synaptic))
        return\
            pd.DataFrame([
                pre.append(post)
                for _, pre in pre_synaptic_cell_types.iterrows()
                for _, post in post_synaptic_cell_types.iterrows()])\
              .reset_index(drop=True)

    def get_pathways_older_implementation(self,
            circuit_model=None,
            pre_synaptic_cell_type_specifiers =None,
            post_synaptic_cell_type_specifiers=None):
        """
        Arguments
        ------------
        pre_synaptic_cell_type ::  An object describing the group of
        ~  pre-synaptic cells to be investigated in these analyses.
        ~  This object must be a `Mappable` with cell properties such as
        ~  region, layer, mtype, and etype defined as keys or columns.
        ~  Each key may be given either a single value or an iterable of
        ~  values. Phenomena must be evaluated for each of these values and
        ~  collected as a pandas.DataFrame.
        post_synaptic_cell_type :: An object describing the group of
        ~  post-synaptic cells to be investigated in these analyses.
        ~  This object must be a `Mappable` with cell properties such as
        ~  region, layer, mtype, and etype defined as keys or columns.
        ~  Each key may be given either a single value or an iterable of
        ~  values. Phenomena must be evaluated for each of these values and
        ~  collected as a pandas.DataFrame.

        Returns
        ------------
        pandas.DataFrame with nested columns, with two columns 
        `(pre_synaptic, post_synaptic)` at the 0-th level.
        Under each of these two columns should be one column each for
        the cell properties specified in the `cell_group` when it is a
        set, or its keys if it is a mapping.
        """
        circuit_model = self._resolve(circuit_model)
        if pre_synaptic_cell_type_specifiers is None:
            if post_synaptic_cell_type_specifiers is None:
                raise TypeError(
                    """
                    Missing arguments. Pass at least one of:
                    1. pre_synaptic_cell_type_specifiers
                    2. post_synaptic_cell_type_specifiers
                    """)
            pre_synaptic_cell_type_specifiers =\
                post_synaptic_cell_type_specifiers
        else:
            if post_synaptic_cell_type_specifiers is None:
                post_synaptic_cell_type_specifiers =\
                    pre_synaptic_cell_type_specifiers

        def _at(synaptic_location, cell_type):
            return\
                pd.concat(
                    [cell_type],
                    axis=1,
                    keys=["{}_synaptic_cell".format(synaptic_location)])

        pre_synaptic_cell_types =\
            _at("pre", self.get_cell_types(circuit_model,
                                           pre_synaptic_cell_type_specifiers))
        post_synaptic_cell_types =\
            _at("post", self.get_cell_types(circuit_model,
                                            post_synaptic_cell_type_specifiers))
        return\
            pd.DataFrame([
                pre.append(post)
                for _, pre in pre_synaptic_cell_types.iterrows()
                for _, post in post_synaptic_cell_types.iterrows()])\
              .reset_index(drop=True)

    # def get_pathways(self,
    #         circuit_model=None,
    #         pre_synaptic_cell_type=None,
    #         post_synaptic_cell_type=None):
    #     """
    #     Arguments
    #     ------------
    #     pre_synaptic_cell_type ::  An object describing the group of
    #     ~  pre-synaptic cells to be investigated in these analyses.
    #     ~  This object must be a `Mappable` with cell properties such as
    #     ~  region, layer, mtype, and etype defined as keys or columns.
    #     ~  Each key may be given either a single value or an iterable of
    #     ~  values. Phenomena must be evaluated for each of these values and
    #     ~  collected as a pandas.DataFrame.
    #     post_synaptic_cell_type :: An object describing the group of
    #     ~  post-synaptic cells to be investigated in these analyses.
    #     ~  This object must be a `Mappable` with cell properties such as
    #     ~  region, layer, mtype, and etype defined as keys or columns.
    #     ~  Each key may be given either a single value or an iterable of
    #     ~  values. Phenomena must be evaluated for each of these values and
    #     ~  collected as a pandas.DataFrame.

    #     Returns
    #     ------------
    #     pandas.DataFrame with nested columns, with two columns 
    #     `(pre_synaptic, post_synaptic)` at the 0-th level.
    #     Under each of these two columns should be one column each for
    #     the cell properties specified in the `cell_group` when it is a
    #     set, or its keys if it is a mapping.
    #     ~   1. When `cell_group` is a set of cell properties, pathways between
    #     ~      all possible values of these cell properties.
    #     ~   2. When `cell-group` is a mapping, pathways between cell groups
    #     ~      that satisfy the mapping values.
    #     """
    #     circuit_model = self._resolve(circuit_model)
    #     if isinstance(cell_group, Set) :
    #         return\
    #             circuit_model.pathways(
    #                 cell_type_specifier=cell_group)
    #     if isinstance(cell_group, pd.DataFrame):
    #         return\
    #             circuit_model.pathways(
    #                 cell_types=cell_group)
    #     raise TypeError(
    #         """
    #         `get_pathways(...)` argument `cell_group` is neither a set of
    #         cell properties, nor a `pandas.DataFrame` specifying cell types.
    #       """)
    @lazyfield
    def visible_voxels(self):
        """
        If it is not masked, a voxel is visible.
        """
        def _spatial_query_data(
                voxel_ids,
                voxel_positions,
                cell_gids):
            """..."""
            return SpatialQueryData(
                ids=pd.Series(list(voxel_ids), name="voxel_id"),
                positions=voxel_positions,
                cell_gids=pd.Series(cell_gids, name="cell_gid"))


        def _get_visible_voxel_data(circuit_model, query):
            """..."""
            LOGGER.debug(
                """
                Compute visible voxel data for query
                \t {}.
                """.format(query))
            visible_voxel_ids ={
                tuple(ijk) for ijk in zip(*np.where( 
                    circuit_model.get_mask(
                        terminology.circuit.get_spatial_query(query))))}
            visible_cell_voxel_ids = list(
                visible_voxel_ids.intersection(
                    circuit_model.voxel_indexed_cell_gids.index.values))
            visible_cell_gids =\
                circuit_model.voxel_indexed_cell_gids\
                             .loc[visible_cell_voxel_ids]
            visible_voxel_positions =\
                circuit_model.get_voxel_positions(
                    np.array(list(visible_voxel_ids)))
            return\
                _spatial_query_data(
                    visible_voxel_ids,
                    visible_voxel_positions,
                    visible_cell_gids)

        return QueryDB(_get_visible_voxel_data)

    def random_position(self,
            circuit_model,
            **query):
        """
        Get a generator for random positions for given spatial parameters.
        """
        positions =\
            self.visible_voxels(circuit_model, query)\
                .positions
        return\
            positions.sample(n=1).iloc[0]\
            if not positions.empty\
               else None

    def get_layer_thickness_values(self,
            circuit_model,
            sample_size=10000,
            **spatial_query):
        """
        Get layer thickness sample for regions specified by a spatial query.
        Thicknesses will be computed for all voxels visible for the spatial
        query. Another possibility is to compute thickness for a random sample
        of visible voxels.

        Because there can be too many (voxel) positions in a region,
        measurement will be made on a sample of positions in the specified
        region.
        """
        positions =\
            self.visible_voxels(circuit_model, spatial_query)\
                .positions\
                .sample(n=sample_size, replace=True)
        return\
            circuit_model.get_thickness(positions)

    def random_region_of_interest(self,
            circuit_model,
            query_dict):
        """
        Get a generator for random regions of interest for given spatial
        parameters.
        """
        random_position = self.random_position(circuit_model, **query_dict)
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

    def get_cells(self,
            circuit_model=None,
            properties=None,
            target=None,
            **query):
        """..."""
        LOGGER.debug(
            LOGGER.get_source_info(),
            "Adapter get cells for query: ",
            "target {}".format(target),
            "{}".format(query))
        cells =\
            self._resolve(circuit_model)\
                .get_cells(properties=properties,
                           target=target,
                           **query)
        query_atlas =\
            terminology.circuit.atlas.filter(**query)

        if not query_atlas:
            return cells

        visible_cell_gids =\
            self.visible_voxels(circuit_model, query_atlas)\
                .cell_gids\
                .values
        return\
            cells.reindex(visible_cell_gids)\
                 .dropna()

    def get_spatial_volume(self,
            circuit_model=None,
            **spatial_query):
        """
        Get total spatial volume of the circuit space that satisfies a
        spatial query.
        """
        circuit_model =\
            self._resolve(circuit_model)
        count_voxels =\
            circuit_model.get_voxel_count(**spatial_query)
        return\
            count_voxels * circuit_model.volume_voxel

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
        count_voxels = circuit_model.get_voxel_count(**query_spatial)
        return count_cells/(count_voxels*1.e-9*circuit_model.volume_voxel)

    @measurement_method("""
    =============================
    Exhaustive Methodology
    =============================
    Count of cells in all the voxcells confirming to a cell-query was
    divided by the total volume of these voxcells.
    =============================
    Random Sampling Methodology
    =============================
    Cells were counted in a box with sides of dimensions {bounding_box_size} um.
    Each cube was centered at a cell that was randomly sampled from
    a population described by a cell-query.
    """)
    @terminology.require(
        *(terminology.circuit.terms + terminology.cell.terms))
    def get_cell_density(self,
            circuit_model=None,
            *args,
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
    Fraction of inhibitory cells was computed in randomly sampled boxes
    of dimensions {bounding_box_size} um.
    """)
    @terminology.require(*terminology.circuit.terms)
    def get_inhibitory_cell_fraction(self,
            circuit_model=None,
            *args, 
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
            LOGGER.warn(
                LOGGER.get_source_info(),
                """
                No more random regions of interest for query:
                \t{}
                """.format(query))
            return np.nan

        number_segments = circuit_model\
            .get_segment_count(
                region=region_of_interest)
        return number_segments / (1.e-9 * region_of_interest.volume)


    def get_soma_positions(self, circuit_model, cells):
        try:
            return cells[XYZ]
        except KeyError:
            return\
                self.get_cells(circuit_model).loc[
                    cells.index.to_numpy(np.int32)
                ][XYZ]

    def get_soma_distance(self,
            circuit_model,
            cell,
            cell_group,
            bin_size=100.):
        """
        Soma distance of a cell from each other cell in a group.
        Arguments
        ---------------
        cell :: a `pandas.Series` defining a cell in the circuit
        cell_group :: A `pandas.DataFrame` containing entries for cell's
        ~             position <X, Y, Z>.
        """
        delta_positions =\
            cell_group[XYZ].to_numpy(dtype=np.float64)\
            - cell[XYZ].to_numpy(dtype=np.float64)
        distances =\
            np.linalg.norm(delta_positions, axis=1)
        bin_starts = bin_size * np.floor(distances / bin_size)
        return np.array([
            bin_start + bin_size / 2. for bin_start in bin_starts])

    def get_cell_gids(self, circuit_model, cells=None):
        """..."""
        if cells is None:
            cells = self.get_cells(circuit_model)

        return\
            cells.index.to_numpy(np.int32)

    def get_adjacency_list(self,
            circuit_model=None,
            pre_synaptic_cells=None,
            post_synaptic_cells=None,
            upper_bound_soma_distance=None,
            with_soma_distance=False,
            *args, **kwargs):
        """...
        Arguments
        ----------
        pre_synaptic_cells :: pandas.DataFrame
        post_synaptic_cells :: pandas.DataFrame
        *args, **kwargs :: accommodate super's call
        """
        circuit_model = self._resolve(circuit_model)
        LOGGER.study(
            LOGGER.get_source_info(),
            """
            Get connection probability for
            {} pre synaptic cells
            {} post synaptic cells
            """.format(
                pre_synaptic_cells.shape[0],
                post_synaptic_cells.shape[0]))
        for count, (_, post_cell) in enumerate(post_synaptic_cells.iterrows()):
            LOGGER.info(
                LOGGER.get_source_info(),
                """
                Get all pairs for post cell {} / {} ({})
                """.format(
                    post_cell,
                    post_synaptic_cells.shape[0],
                    count / post_synaptic_cells.shape[0]))
            pairs =\
                pre_synaptic_cells\
                .reset_index(drop=True)\
                .assign(
                    number_pairs_connected=np.in1d(
                        pre_synaptic_cells.gid.values,
                        circuit_model.connectome.afferent_gids(post_cell.gid)),
                    number_pairs_total=1.)
            if upper_bound_soma_distance is not None:
                soma_distance =\
                    self.soma_distance(
                        pre_synaptic_cells,
                        post_cell)
                pairs =\
                    pairs[
                        soma_distance < upper_bound_soma_distance
                    ].reset_index(drop=True)
            if with_soma_distance:
                pairs =\
                    pairs.assign(
                        soma_distance=self.soma_distance(
                            pre_synaptic_cells,
                            post_cell))
            post_cell_info =\
                pd.DataFrame(pairs.shape[0] * [post_cell.drop("gid")])\
                  .reset_index(drop=True)
            yield\
                pd.concat([pairs, post_cell_info], axis=1)\
                  .reset_index(drop=True)

    def get_afferent_gids(self,
            circuit_model,
            post_synaptic_cell):
        """
        Ids of the cells afferently connected to a post-synaptic cell.
        These ids (gids) are used to index the circuit's cells.
        """
        return circuit_model.connectome.afferent_gids(post_synaptic_cell.gid)

    def _resolve_gids(self, circuit_model, cell_group):
        """
        Resolve cell gids...
        """
        if isinstance(cell_group, np.ndarray):
            gids = cell_group
        elif isinstance(cell_group, pd.Series):
            try:
                gids = np.array([cell_group.gid])
            except AttributeError:
                gids = self.get_cells(circuit_model, **cell_group).gid.values
        elif isinstance(cell_group, pd.DataFrame):
            gids = cell_group.gid.values
        else:
            raise ValueError(
                """
                Could not resolve gids from object {}
                """.format(cell_group))
        return gids

    def get_afferent_connections(self,
            circuit_model,
            post_synaptic,
            with_synapse_count=True):
        """
        Arguments
        ----------------
        post_synaptic :: Either a pandas.Series representing a cell
        ~                or a pandas.DataFrame containing cells as rows
        ~                or a numpy.array of cell gids.,
        """
        iter_connections =\
            circuit_model.connectome\
                         .iter_connections(
                             post=self._resolve_gids(circuit_model, post_synaptic),
                             return_synapse_count=with_synapse_count)
        connections =\
            np.array([
                connection for connection in iter_connections])
        if with_synapse_count:
            if connections.shape[0] == 0:
                return pd.DataFrame([], columns=["pre_gid", "post_gid", "strength"])
            return\
                pd.DataFrame({
                    "pre_gid": np.array(connections[:, 0], dtype=np.int32),
                    "post_gid": np.array(connections[:, 1], dtype=np.int32),
                    "strength": connections[:, 2]})
        if connections.shape[0] == 0:
            return pd.DataFrame([], columns=["pre_gid"])
        return pd.DataFrame({"pre_gid": connections[:, 0]})

    def get_efferent_connections(self,
            circuit_model,
            pre_synaptic,
            with_synapse_count=True):
        """

        Arguments
        ----------------
        pre_synaptic :: Either a pandas.Series representing a cell
        ~               or a pandas.DataFrame containing cells as rows
        ~               or a numpy.array of cell gids.,
        """
        iter_connections =\
            circuit_model.connectome\
                         .iter_connections(
                             pre=self._resolve_gids(circuit_model, pre_synaptic),
                             return_synapse_count=with_synapse_count)
        connections =\
            np.array([
                connection for connection in iter_connections])
        if with_synapse_count:
            if connections.shape[0] == 0:
                return pd.DataFrame([], columns=["post_gid", "post_gid", "strength"])
            return\
                pd.DataFrame({
                    "pre_gid": np.array(connections[:, 0], dtype=np.int32),
                    "post_gid": np.array(connections[:, 1], dtype=np.int32),
                    "strength": connections[:, 2]})
        if connections.shape[0] == 0:
            return pd.DataFrame([], columns=["post_gid"])
        return pd.DataFrame({"post_gid": connections[:, 1]})

    def get_connections(self,
            circuit_model,
            cell_group,
            direction,
            with_synapse_count=True):
        """..."""
        return\
            self.get_afferent_connections(
                circuit_model, cell_group, with_synapse_count)\
            if direction == "AFF" else\
               self.get_efferent_connections(
                   circuit_model, cell_group, with_synapse_count)

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
            circuit_model.pathway_summary\
                         .probability_connection(
                             pre_synaptic_cells,
                             post_synaptic_cells,
                             with_soma_distance=True)\
                         .reset_index()\
                         .assign(
                             soma_distance=lambda df: df.soma_distance.apply(np.mean))\
                         .set_index("soma_distance")\
                         .probability_connection

    def get_number_connections_afferent(self,
            circuit_model=None,
            pre_synaptic_cell_type={},
            post_synaptic_cell_type={},
            soma_distance_bins=None,
            sampling_methodology=terminology.sampling_methodology.random,
            sample_size_post_synaptic_cells=20,
            **kwargs):
        """
        Number of afferent connections incident upon a cell is the same as
        its in-degree. Thus this method computes in-degree for cells in a group
        defined by `post_synaptic_cell_type`. If the methodology is random, a
        subset of cells in this group will be sampled. The connections incident
        upon these post-synaptic cells must originate from pre-synaptic cells.
        The pre-synaptic cell group is defined by `pre_synaptic_cell_type`, and
        all cells in this group must be considered to compute each sampled
        post-synaptic cell's in-degree.

        Arguments
        -----------
        `pre_synaptic_cell_type` : Mappable or pandas.Series specifying the
        ~                          type of the cells on the pre-synaptic side.
        `post_synaptic_cell_type`: Mappable or pandas.Series specifying the
        ~                           type of the cells on the post-synaptic side.
        """
        if soma_distance_bins is not None:
            raise NotImplementedError(
                """
                Not yet implemented for custom values of `soma_distance_bins`.
                """)
        circuit_model =\
            self._resolve(
                circuit_model)
        pre_synaptic_cells =\
            circuit_model.get_cells(
                **pre_synaptic_cell_type)
        post_synaptic_cells =\
            self._resolve_sample_cells(
                circuit_model,
                post_synaptic_cell_type,
                sampling_methodology,
                sample_size_post_synaptic_cells)
        return\
            circuit_model.pathway_summary\
                         .number_connections_afferent(
                             pre_synaptic_cells,
                             post_synaptic_cells,
                             with_soma_distance=False)\
                         .number_connections_afferent["mean"]

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
                soma_distance=lambda df: df.soma_distance.apply(np.mean)
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

    def get_column(self, circuit_model, target=None, axcell=None, radius=250.):
        """
        Get a (cortical) column with the argumented `axcell` on its axis.

        Returns
        -------------
        A subset of all cells in the argumented circuit model that lie in the
        column.
        """
        if target is not None:
            if axcell is not None:
                raise TypeError(
                    """
                    get_column(...) called with both `target` and `axcell`
                    arguments. Only one of are accepted.
                    """)
            return self.get_cells(circuit_model, target=target)

        cells = self.get_cells(circuit_model)
        if isinstance(axcell, (float, np.float)):
            axcell = all_cells.iloc[axcell]

        def _axis(orientation):
            """..."""
            return np.dot(orientation, np.array([0., 1., 0.]))

        try:
            axis_column = _axis(axcell.orientation)
        except AttributeError:
            axis_column = np.array([0., 1., 0.])


        position =\
            lambda cell: cell[XYZ].to_numpy(np.float64)
        position_axcell =\
            position(cells) - position(axcell)
        distance_axcell =\
            np.linalg.norm(
                position_axcell, axis=1)
        component_axis =\
            np.dot(
                position_axcell, axis_column)
        distance_axis =\
            np.sqrt(
                distance_axcell ** 2 - component_axis ** 2)

        return\
            cells[distance_axis < radius]
