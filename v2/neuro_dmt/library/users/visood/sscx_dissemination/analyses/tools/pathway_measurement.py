"""
Measure pathways.
"""
from enum import Enum
from tqdm import tqdm
from collections import namedtuple, Iterable, Mapping
import numpy as np
import pandas as pd
from dmt.tk.collections import head, Record
from dmt.tk.field import NA, Field, LambdaField, lazyfield, WithFields
from dmt.tk.journal.logger import Logger 
from neuro_dmt import terminology
from .import count_number_calls

LOGGER = Logger(client=__file__)


class Connectivity(Enum):
    """
    Used for testing, or to compute pathway phenomena on a complete network
    connectome.
    """
    COMPLETE = 1
    RANDOM   = 2
    CIRCUIT  = 3


class PathwayQuery(WithFields):
    """
    Defines a pathway query.
    """
    post_synaptic_cell_group = Field(
        """
        Either a cell type described by a `Mapping` or `pandas.Series`,
        or a collection of cells as a `pandas.DataFrame`,
        or a collection of gids as a `np.ndarray, list, Iterable`,
        or a named target
        """)
    pre_synaptic_cell_group = Field(
        """
        Either a cell type described by a `Mapping` or `pandas.Series`,
        or a collection of cells as a `pandas.DataFrame`,
        or a collection of gids as a `np.ndarray, list, Iterable`,
        or a named target
        """)
    direction = Field(
        """
        `afferent` or `efferent`
        """)

    def __repr__(self):
        return "{}".format(self.field_dict)

    @lazyfield
    def cell_group(self):
        """
        Determine the primary and secondary synaptic cell types in the query.
        Cell type of the primary, with respect to the direction of measurement,
        synaptic side sides.
        If the measurement will be made in the afferent direction, the primary
        cell type will be that of the post-synaptic cells, and the secondary
        that of the pre-synatic cells.
        If the measurement will be made in the efferent direction, the primary
        cell type will be that of the pre-synaptic cells, and the secondary
        that of the post-synaptic cells.s
        """
        if self.direction == terminology.direction.afferent:
            return Record(
                primary=self.post_synaptic_cell_group,
                secondary=self.pre_synaptic_cell_group)
        if self.direction == terminology.direction.efferent:
            return Record(
                primary=self.pre_synaptic_cell_group,
                secondary=self.post_synaptic_cell_group)
        raise ValueError(
            "Unknown measurement direction {}.".format(self.direction))

    @lazyfield
    def secondary_synaptic_side(self):
        if self.direction == terminology.direction.afferent:
            return "pre_synaptic_cell"
        if self.direction == terminology.direction.efferent:
            return "post_synaptic_cell"
        raise ValueError(
            "Unknown measurement direction {}.".format(self.direction))

    @lazyfield
    def primary_synaptic_side(self):
        if self.direction == terminology.direction.afferent:
            return "post_synaptic_cell"
        if self.direction == terminology.direction.efferent:
            return "pre_synaptic_cell"
        raise ValueError(
            "Unknown measurement direction {}.".format(self.direction))
 

class PathwayMeasurement(WithFields):
    """
    Measure pathways in a circuit.
    """
    connectivity = Field(
        """
        Indicates if the circuit model itself will provide measurements (
        through the adapter), or if the connectome connections must be assumed
        to be complete (i.e. all pairs connected), or are randomly connected.
        """,
        __type__=Connectivity,
        __default_value__=Connectivity.CIRCUIT)
    direction = Field(
        """
        AFF / EFF.
        """)
    value = Field(
        """
        Measurement method for a single set of parameter-values.
        """)
    variable = Field(
        """
        Name of the variable to give to the measurement.
        Thus variable may be queried to retrieve the measurement from
        a connections pandas dataframe.
        """,
        __default_value__="measurement")
    specifiers_cell_type = Field(
        """
        Cell properties that define this pathway.
      """,
      __examples__=["mtype", "etype"],
        __default_value__=[])
    sampling_methodology = Field(
        """
        Random or exhaustive?
        """,
        __default_value__=terminology.sampling_methodology.random)
    sample_size = Field(
        """
        Number of samples to consider if random sampling methodology.
        """,
        __default_value__=20)
    processing_methodology = Field(
        """
        Specifies if `Field value` computes it's result for one cell at a time,
        or a batch of cells at a time.
        """,
        __default_value__=terminology.processing_methodology.serial)
    batch_size = Field(
        """
        Maximum size of a single batch that can be processed.
        """,
        __default_value__=10000)
    by_soma_distance = Field(
        """
        Boolean, indicating if the measurements should be made by soma-distance.
        """,
        __default_value__=False)
    bin_size_soma_distance = Field(
        """
        Size of soma distance bins (in um) 
        """,
        __default_value__=100)
    upper_bound_soma_distance = Field(
        """
        Consider cell pairs that are separated by up to this soma-distance,
        interpreting a nan value as infinity.
        """,
        __default_value__=np.nan)
    summaries = Field(
        """
        Summaries required, if making a summary measurement.
        """,
        __default_value__=[
            "count", "sum", "mean", "mad", "std", "var", "min", "median", "max"])

    fraction_circuit_cells = Field(
        """
        Float representing the fraction of circuit cells to define a sub-network
        to measure.
        """,
        __default_value__=np.nan)

    cell_counts = Field(
        """
        Mapping <circuit -> cell-type> to cache for a given circuit.
        """,
        __default_value__={})
    target = Field(
        """
        Mapping <circuit -> Record(primary, secondary) >
        to cache for a given circuit.
        """,
        __default_value__=NA)
    return_primary_info = Field(
        """
        Boolean indicating if the queries primary cell gid(s) should be
        returned in the index.
        """,
        __default_value__=True)

    def _validate_fields(self):
        """..."""
        if (self.by_soma_distance and
            not np.isnan(self.upper_bound_soma_distance)):
            raise TypeError(
                """
                {} cannot be instantiated to bin results by soma-distance and 
                use an upper bound on soma-distance to filter connections.
                """.format(self.__class__.__name__))

    @lazyfield
    def using_subset_of_cells(self):
        """
        Boolean, set to `False` if all cells in circuit should be used for
        connectome measurements. Otherwise a subset of all the circuit cells
        will be used.
        By default, the value will inferred from `Field fraction_circuit_cells`.
        If its value is meaningful (i.e. not NaN), a random pool of cells will
        be used (and cached).
        """,
        return not np.isnan(self.fraction_circuit_cells)

    @lazyfield
    def filter_by_upper_bound_soma_distance(self):
        return not np.isnan(self.upper_bound_soma_distance)


    def _default_target(self, adapter, circuit_model):
        """
        Default target is all cell.
        """
        if not self.using_subset_of_cells:
            all_cells =\
                adapter.get_cells(circuit_model)\
                       .assign(group_id="Ungrouped")
            return\
                Record(primary=all_cells,
                       secondary=all_cells)

        def _subset_cells(group_id, cell_type):
            cells =\
                adapter.get_cells(circuit_model, **cell_type)
            n_cells =\
                np.int32(self.fraction_circuit_cells * cells_shape[0])
            return\
                cells.sample(n_cells).assign(group=group_id)
        cell_types =\
            adapter.get_cell_types(circuit_model, self.specifiers_cell_type)
        pool_cells =\
            pd.concat([
                _subset_cells(group_id, cell_type)
                for group_id, cell_type in cell_types.iterrows()])
        self.cell_counts[circuit_model] =\
            cell_types.assign(number=pool_cells.group.value_counts())\
                      .set_index(self.specifiers_cell_type)\
                      .number
        return\
            Record(primary=pool_cells, secondary=pool_cells)

    def _load_target(self, adapter, circuit_model):
        """
        Load cells...
        """
        target =\
            self.target(adapter, circuit_model)\
            if self.target is not NA else\
               self._default_target(adapter, circuit_model)
        if isinstance(target, (pd.Series, pd.DataFrame)):
            return\
                Record(primary=target, secondary=target)
        if not (hasattr(target, "primary") and hasattr(target, "secondary")):
            raise TypeError(
                "Circuit model target does not have primary and secondary.")
        primary_target =\
            target.primary\
            if isinstance(target.primary, (pd.Series, pd.DataFrame)) else\
               target.primary(adapter, circuit_model)
        secondary_target =\
            target.secondary \
            if isinstance(target.secondary, (pd.Series, pd.DataFrame)) else\
               target.secondary(adapter, circuit_model)
        return\
            Record(primary=primary_target,
                   secondary=secondary_target)
            
    def get_target(self, adapter, circuit_model, query):
        """
        Population of cells in the circuit model to work with.
        """
        target_pool = self._load_target(adapter, circuit_model)

        def _get(position_query):
            group = getattr(query.cell_group, position_query)
            pool  = getattr(target_pool, position_query)

            LOGGER.debug(
                LOGGER.get_source_info(),
                "PathwayMeasurement.get_target(...)",
                "position_query {}".format(position_query),
                "group: {}".format(group))

            if isinstance(group, (Mapping, pd.Series)):
                all_cells =\
                    adapter.get_cells(circuit_model, **group)
            elif isinstance(group, pd.DataFrame):
                all_cells =\
                    group.copy()
            elif isinstance(group, Iterable):
                all_cells =\
                    adapter.get_cells(circuit_model, target=group)
            else:
                all_cells =\
                    adapter.get_cells(circuit_model)

            return\
                pool.reindex(all_cells.index.to_numpy(np.int32))\
                    .dropna()

        return Record(
            primary=_get("primary"),
            secondary=_get("secondary"))

        # if isinstance(cell_group, (Mapping, pd.Series)):
        #     all_cells =\
        #         adapter.get_cells(circuit_model, **cell_group)
        # elif isinstance(cell_group, pd.DataFrame):
        #     all_cells =\
        #         cell_group.copy()
        # elif isinstance(cell_group, Iterable):
        #     all_cells =\
        #         adapter.get_cells(circuit_model, target=cell_group)
        # else:
        #     all_cells =\
        #         adapter.get_cells(circuit_model)

        # return\
        #     pool_cells.reindex(all_cells.index.to_numpy(np.int32))\
        #               .dropna()
    def _sample_target(self, adapter, circuit_model, query, size=None):
        """
        Primary and secondary cell samples.
        """
        LOGGER.debug(
            "PathwayMeasurement._sample_target(...)",
            "{}".format(query))
        exhaustive =\
            self.sampling_methodology ==\
            terminology.sampling_methodology.exhaustive
        target =\
            self.get_target(adapter, circuit_model, query)

        def _sample(cells):
            if exhaustive and size is None:
                return cells
                
            sample_size = size if size is not None else self.sample_size
            if sample_size == 1:
                return cells.sample(1).iloc[0]\
                    if cells.shape[0] > 0\
                       else None

            if cells.shape[0] == 0:
                return pd.DataFrame(
                    [], columns=cells.columns)

            return cells.sample(sample_size)\
                if cells.shape[0] > sample_size\
                   else cells

        return Record(
            primary=_sample(target.primary),
            secondary=target.secondary)

    def get_pairs(self,
            gids_primary,
            gids_secondary):
        """
        Get pairs between all pooled cells and cells with the argumented gids.
        """
        return\
            pd.concat([
                pd.DataFrame({
                    self.label_gid_primary: gid,
                    self.label_gid_secondary: gids_secondary})
                for gid in gids_primary])

    def get_connections(self,
            circuit_model,
            adapter,
            gids_primary,
            gids_secondary,
            connectivity=None):
        """
        Get connections...
        """
        LOGGER.ignore(
            "PathwayMeasurement.get_connections(...)",
            "queried primary gids {}".format(len(gids_primary)),
            "queried secondary gids {}".format(len(gids_secondary)))
            
        connectivity =\
            connectivity if connectivity else self.connectivity
        if connectivity == Connectivity.COMPLETE:
            return\
                self.get_pairs(gids_primary, gids_secondary)\
                    .assign(strength=1.)

        all_connections =\
            adapter.get_connections(
                circuit_model,
                gids_primary,
                direction=self.direction)

        LOGGER.debug(
            "PathwayMeasurement get_connections",
            "queried gids {}".format(len(gids_primary)),
            "number connections: {}".format(all_connections.shape[0]))

        return\
            all_connections[np.in1d(
                all_connections[self.label_gid_secondary].to_numpy(np.int32),
                gids_secondary)]

    def _check_sampling_methodology(self, kwargs):
        """..."""
        try:
            sampling_methodology = kwargs.pop("sampling_methodology")
            if sampling_methodology != self.sampling_methodology:
                LOGGER.warn(
                    """
                    Argument `sampling_methodology` will be dropped.
                    A sampling methodology of {} was set at the time this {} 
                    instance was generated.
                    Provided value '{}' will be dropped.
                    """.format(self.sampling_methodology,
                               self.__class__.__name__,
                               sampling_methodology))
        except KeyError:
            pass

    def _prefix_secondary_synaptic_side(self, query, measured_values):
        """..."""
        if isinstance(measured_values, (pd.Series, pd.DataFrame)):
            if isinstance(measured_values.index, pd.MultiIndex):
                measured_values.index.names =[
                    self._prefix(query, variable)
                    for variable in measured_values.index.names]
            else:
                measured_values.index.name =\
                    self._prefix(query, measured_values.index.name)

        return measured_values

    def _prefix_primary_synaptic_side(self, query, measured_values):
        """
        Primary side cell information is just the gid of the cell,
        either a single cell as a series or a group as a dataframe.
        """
        if isinstance(measured_values, (pd.Series, pd.DataFrame)):
            if isinstance(measured_values.index, pd.MultiIndex):
                measured_values.index.names =[
                    ((query.primary_synaptic_side, "gid")
                     if variable == self.label_gid_primary else variable)
                    for variable in measured_values.index.names]

        return measured_values

    def _prefix(self, query, variable):
        """..."""
        return\
            (query.secondary_synaptic_side, variable)\
            if variable in self.specifiers_cell_type\
               else variable


    # def sample_one(self, adapter, circuit_model,
    #         pre_synaptic_cell=None,
    #         post_synaptic_cell=None,
    #         **kwargs):
    #     """
    #     ...
    #     """
    #     LOGGER.debug(
    #         "PathwayMeasurement sample one",
    #         "pre_synaptic_cell {}".format(pre_synaptic_cell),
    #         "post_synaptic_cell {}".format(post_synaptic_cell))
    #     self._check_sampling_methodology(kwargs)
    #     pair =\
    #         self._resolve_pair(pre_synaptic_cell, post_synaptic_cell)
    #     cell =\
    #         self._sample_cells(
    #             circuit_model, adapter,
    #             cell_type=pair.cell_type,
    #             size=1)
    #     measured_values =\
    #         self._prefix_aggregated_synaptic_side(
    #             pair,
    #             self._method(
    #                 circuit_model, adapter, cell,
    #                 cell_properties_groupby=self.specifiers_cell_type,
    #                 by_soma_distance=self.by_soma_distance,
    #                 bin_size_soma_distance=self.bin_size_soma_distance,
    #                 **kwargs))
    #     try:
    #         return measured_values.rename(cell.gid)
    #     except:
    #         return measured_values
    #     raise RuntimeError("Execution should not reach here.")
    def _batches(self, cells):
        """
        Batches of cells to process.
        """
        if isinstance(cells, pd.DataFrame):
            mtypes = cells.mtype.unique()
            LOGGER.debug(
                LOGGER.get_source_info(),
                "PathwayMeasurement._batches(...)",
                "cell mtypes {}".format(mtypes))
        else:
            mtype = cells.mtype
            LOGGER.debug(
                LOGGER.get_source_info(),
                "PathwayMeasurement._batches(...)",
                "cell {}".format(cells))

        if self.processing_methodology == terminology.processing_methodology.serial:
            return (cell for _, cell in cells.iterrows())

        n_batches =\
            int(np.floor(cells.shape[0] / self.batch_size))
        batches =\
            [(b * self.batch_size, (b+1) * self.batch_size)
             for b in range(n_batches)]
        if n_batches * self.batch_size < cells.shape[0]:
            batches.append((n_batches * self.batch_size, cells.shape[0]))
        return (cells.iloc[begin_batch:end_batch]
                for (begin_batch, end_batch) in batches)

    def sample(self,
            adapter, circuit_model,
            pre_synaptic_cell_group={},
            post_synaptic_cell_group={},
            **kwargs):
        """
        Sample of measurements.

        """
        LOGGER.debug(
            "PathwayMeasurement.sample(...)",
            "with sampling methodology {}".format(self.sampling_methodology))
        self._check_sampling_methodology(kwargs)
        query =\
            PathwayQuery(
                post_synaptic_cell_group=post_synaptic_cell_group,
                pre_synaptic_cell_group=pre_synaptic_cell_group,
                direction=self.direction)
        target =\
            self._sample_target(
                adapter, circuit_model, query)

        batches =\
            self._batches(target.primary)
        for n_batch, batch in tqdm(enumerate(batches)):
            LOGGER.info(
                LOGGER.get_source_info(),
                "batch {}: {}".format(n_batch,  batch))
            measurement =\
                self._method(
                    circuit_model, adapter,
                    target=Record(primary=batch, secondary=target.secondary),
                    cell_properties_groupby=self.specifiers_cell_type,
                    by_soma_distance=self.by_soma_distance,
                    bin_size_soma_distance=self.bin_size_soma_distance,
                    **kwargs)
            LOGGER.debug(
                LOGGER.get_source_info(),
                "measurement obtained: ".format(type(measurement)))
            if measurement is None:
                yield None
                continue
            LOGGER.debug(
                LOGGER.get_source_info(),
                "measurement obtained {}: ".format(measurement.shape),
                "columns {}".format(measurement.name))
            if self.return_primary_info:
                # specifiers_secondary =\
                #     measurement.index\
                #                .to_frame()[self.specifiers_cell_type]\
                #                .reset_index(drop=True)
                specifiers_secondary =\
                    pd.DataFrame({
                        level: measurement.index.get_level_values(level).values
                        for level in self.specifiers_cell_type})
                values =\
                    measurement.values
                _gids_primary =\
                    measurement.index.get_level_values(self.label_gid_primary)\
                                     .to_numpy(np.int32)
                _specifiers_primary =\
                    adapter.get_cells(circuit_model)\
                           .iloc[_gids_primary]\
                           [self.specifiers_cell_type]\
                           .reset_index(drop=True)
                gids_primary =\
                    pd.Series(_gids_primary, name="gid")
                specifiers_primary =\
                    pd.concat(
                        [gids_primary, _specifiers_primary],
                        axis=1)
                LOGGER.debug(
                    LOGGER.get_source_info(),
                    "specifiers primary {}".format(specifiers_primary.head()))

                index =\
                    pd.concat(
                        [specifiers_primary, specifiers_secondary],
                        axis=1,
                        keys=[query.primary_synaptic_side,
                              query.secondary_synaptic_side])
                yield\
                    pd.DataFrame(
                        {self.variable: values},
                        index=pd.MultiIndex.from_frame(index))
            else:
                yield\
                    self._prefix_secondary_synaptic_side(
                        query,
                        measurement.droplevel(self.label_gid_primary))

    def get_soma_distance_bins(self,
            circuit_model,
            adapter,
            cell_group_from,
            cell_group_to,
            bin_size_soma_distance=None):
        """
        Get binned distance of `cell`'s soma from soma of all the cells in
        `cell_group`.
        """
        def _binned(distances):
            bin_size =\
                bin_size_soma_distance if bin_size_soma_distance\
                else self.bin_size_soma_distance
            bin_starts =\
                bin_size * np.floor(distances / bin_size)
            return\
                np.array([
                    bin_start + bin_size / 2.
                    for bin_start in bin_starts])

        if isinstance(cell_group_from, pd.Series):
            return\
                _binned(adapter.get_soma_distance(
                    circuit_model,
                    cell_group_from,
                    cell_group_to))
        elif isinstance(cell_group_from, pd.DataFrame):
            positions_from =\
                adapter.get_soma_positions(
                    circuit_model,
                    cell_group_from.loc[
                        cell_group_to[self.label_gid_primary].to_numpy(np.int32)])
            positions_to =\
                adapter.get_soma_positions(
                    circuit_model,
                    cell_group_to)
            return\
                _binned(np.linalg.norm(
                    positions_to.values - positions_from.values,
                    axis=1))

    @lazyfield
    def label_gid_secondary(self):
        return\
            "pre_gid" if self.direction == "AFF" else "post_gid"
    @lazyfield
    def label_gid_primary(self):
        return\
            "post_gid" if self.direction == "AFF" else "pre_gid"

    @count_number_calls(LOGGER)
    def _method(self,
            circuit_model, adapter,
            target,
            cell_properties_groupby,
            **kwargs):
        """..."""
        def _get_size(t):
            if isinstance(t, pd.DataFrame):
                return t.shape[0]
            if isinstance(t, pd.Series):
                return 1
            return np.nan

        size_target =\
            Record(primary=_get_size(target.primary),
                   secondary=_get_size(target.secondary))
        LOGGER.debug(
            LOGGER.get_source_info(),
            "PathwayMeasurement._method(...)",
            "number primary.target {}".format(size_target.primary),
            "number secondary.target {}".format(size_target.secondary))

        by_soma_distance =\
            kwargs.get("by_soma_distance", self.by_soma_distance)
        bin_size_soma_distance =\
            kwargs.get("bin_size_soma_distance", self.bin_size_soma_distance)
        try:
           return self.value(
               circuit_model, adapter,
               target.primary,
               cell_properties_groupby=cell_properties_groupby,
               by_soma_distance=by_soma_distance,
               bin_size_soma_distance=bin_size_soma_distance,
               **kwargs)
        except (TypeError, ValueError):
            pass

        def _get_value(connections):
            try:
               value = self.value(connections)
            except TypeError:
                try:
                    value = connections[self.variable]
                except:
                    raise TypeError(
                        """
                        Not enough information to make the measurement:
                        \t value: {}
                        \t variable: {}
                        """.format(
                            self.value,
                            self.variable))
            return value

        def _gids(connections, label_nodes):
            return\
                connections[label_nodes].to_numpy(np.int32)

        def _gids_measured(connections):
            return _gids(connections, self.label_gid_primary)

        def _gids_connected(connections):
            return _gids(connections, self.label_gid_secondary)

        if isinstance(target.primary, pd.DataFrame):
            target_primary =\
                target.primary.gid.to_numpy(np.int32)
        elif isinstance(target.primary, pd.Series):
            if not "gid" in target.primary.index:
                raise ValueError(
                """
                `PathwayMeasurement._method(...)` got a pandas.Series
                as a `cell_info` that did not contain cell `gid`.
                """)
            target_primary =\
                np.array([target.primary.gid])
        else:
            raise ValueError(
            """
            `PathwayMeasurement._method(...)` does not know how to handle
            `cell_info` {}.
            """.format(target.primary))
        connections =\
            self.get_connections(
                circuit_model, adapter,
                target_primary,
                target.secondary.gid.to_numpy(np.int32))
        if connections.empty:
            return None

        variables_groupby =\
            cell_properties_groupby +(
                [self.label_gid_primary, "soma_distance"]
                if by_soma_distance else
                [self.label_gid_primary])
        columns_relevant =\
            cell_properties_groupby + (
                [self.label_gid_primary, "soma_distance", self.variable]
                if by_soma_distance else
                [self.label_gid_primary, self.variable])

        # if isinstance(target.primary, pd.DataFrame):
        #     connections =\
        #         self.get_connections(
        #             circuit_modelcircuit_model, adapter,
        #             target.primary.gid.to_numpy(np.int32),
        #             target.secondary.gid.to_numpy(np.int32))
        #     variables_groupby =\
        #         cell_properties_groupby +(
        #             [self.label_gid_primary, "soma_distance"]
        #             if by_soma_distance else
        #             [self.label_gid_primary])
        #     columns_relevant =\
        #         cell_properties_groupby + (
        #             [self.label_gid_primary, "soma_distance", self.variable]
        #             if by_soma_distance else
        #             [self.label_gid_primary, self.variable])
        # elif isinstance(target.primary, pd.Series):
        #     if not "gid" in target.primary.index:
        #         raise ValueError(
        #             """
        #             `PathwayMeasurement._method(...)` got a pandas.Series
        #             as a `cell_info` that did not contain cell `gid`.
        #             """)
        #     connections =\
        #         self.get_connections(
        #             circuit_model, adapter,
        #             np.array([target.primary.gid]),
        #             target.secondary.gid.to_numpy(np.int32))
        #     variables_groupby =\
        #         cell_properties_groupby +(
        #             ["soma_distance"]
        #             if by_soma_distance else
        #             [])
        #     columns_relevant =\
        #         cell_properties_groupby +(
        #             ["soma_distance", self.variable] if by_soma_distance else
        #             [self.variable])
        # else:
        #     raise ValueError(
        #         """
        #         `PathwayMeasurement._method(...)` does not know how to handle
        #         `cell_info` {}.
        #         """.format(target.primary))

        primary_gids =\
            connections[self.label_gid_primary].to_numpy(np.int32)
        secondary_gids =\
            connections[self.label_gid_secondary].to_numpy(np.int32)
        cells_connected =\
            adapter.get_cells(circuit_model)\
                   .loc[secondary_gids]\
                   .assign(**{
                       self.label_gid_primary: primary_gids,
                       self.variable: self.value(connections)})

        if by_soma_distance or self.filter_by_upper_bound_soma_distance:
            def _soma_distance(other_cells):
                return\
                    self.get_soma_distance_bins(
                        circuit_model, adapter,
                        target.primary,
                        other_cells,
                        bin_size_soma_distance=bin_size_soma_distance)
            cells_connected =\
                cells_connected.assign(soma_distance=_soma_distance)
        if self.filter_by_upper_bound_soma_distance:
            cells_connected =\
                cells_connected[
                    cells_connected.soma_distance < self.upper_bound_soma_distance]

        cells_connected =\
            cells_connected[columns_relevant]

        LOGGER.ignore(
            LOGGER.get_source_info(),
            "PathwayMeasurement._method(...)",
            "variables_groupby {}".format(variables_groupby),
            "columns_relevant {}".format(columns_relevant),
            "number cells_connected {}".format(cells_connected.shape[0]),
            "columns in cells_connected {}".format(cells_connected.columns))

        try:
            value_groups = cells_connected.groupby(variables_groupby)
        except (TypeError, ValueError) as error:
            LOGGER.warn(
                """
                Connected cells {} could not be grouped by {}:
                \t {}
                """.format(
                    cells_connected.shape,
                    variables_groupby,
                    error))
            value_groups = cells_connected

        summed_value_groups = value_groups.agg("sum")[self.variable]
        
        # try:
        #      summed_value_groups =\
        #          summed_value_groups.droplevel(self.label_gid_primary)
        # except (KeyError, AttributeError, ValueError):
        #     pass

        return summed_value_groups

    def collect(self, adapter, circuit_model,
            pre_synaptic_cell_group={},
            post_synaptic_cell_group={},
            **kwargs):
        """"..."""
        listed_sample =[
            m for m in
            self.sample(
                circuit_model, adapter,
                pre_synaptic_cell_group=pre_synaptic_cell_group,
                post_synaptic_cell_group=post_synaptic_cell_group,
                **kwargs)
            if m is not None]
        try:
            return pd.concat(listed_sample)
        except TypeError:
            return pd.Series(listed_sample, name=self.variable)

    def summary(self, adapter, circuit_model,
            pre_synaptic_cell_group={},
            post_synaptic_cell_group={},
            aggregators=None,
            **kwargs):
        """..."""
        if aggregators is None:
            aggregators =\
                self.summaries[0]\
                if len(self.summaries) == 1 else\
                self.summaries
        collection =\
            self.collect(
                circuit_model, adapter,
                pre_synaptic_cell_group=pre_synaptic_cell_group,
                post_synaptic_cell_group=post_synaptic_cell_group,
                **kwargs)
        query =\
            PathwayQuery(
                post_synaptic_cell_group=post_synaptic_cell_group,
                pre_synaptic_cell_group=pre_synaptic_cell_group,
                direction=self.direction)
        variables_groupby =[
            self._prefix(query, variable)
            for variable in (self.specifiers_cell_type+(
                ["soma_distance"] if self.by_soma_distance else []))]
        try:
            return\
                collection.groupby(variables_groupby).agg(aggregators)
        except ValueError:
            return\
                collection.agg(aggregators)

        raise RuntimeError(
            "Execution should not reach here.")

    def norm_per_pair(self, *args, **kwargs):
        """
        Get a norm for the summaries...
        Will be used to measure connection probability.
        """

        number_connections_pathway =\
            self.summary(*args, aggregators="sum", **kwargs)

        number_pairs_pathway =\
            self.with_field_values(connectivity=Connectivity.COMPLETE,
                                   target=self.target)\
                .summary(*args, aggregators="sum", **kwargs)

        return\
            number_connections_pathway / number_pairs_pathway




