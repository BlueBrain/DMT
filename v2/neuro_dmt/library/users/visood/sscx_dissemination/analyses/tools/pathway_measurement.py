"""
Measure pathways.
"""
from enum import Enum
import numpy as np
import pandas as pd
from dmt.tk.collections import head, Record
from dmt.tk.field import Field, LambdaField, lazyfield, WithFields
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
        Mapping <circuit -> cells > to cache for a given circuit.
        """,
        __default_value__={})

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

    def _load_cells(self, circuit_model, adapter):
        """
        Load cells...
        """
        if circuit_model not in self.target:
            if not self.using_subset_of_cells:
                self.target[circuit_model] =\
                    adapter.get_cells(circuit_model)
            else:
                def _sample_cells(group_id, cell_type):
                    cells =\
                        adapter.get_cells(
                            circuit_model, **cell_type)
                    n_cells =\
                        np.int32(
                            self.fraction_circuit_cells * cells.shape[0])
                    return\
                        cells.sample(n_cells)\
                             .assign(group=group_id)
                
                cell_types =\
                    adapter.get_cell_types(
                        circuit_model, self.specifiers_cell_type)
                pool_cells =\
                    pd.concat([
                        _sample_cells(group_id, cell_type)
                        for group_id, cell_type in cell_types.iterrows()])
                self.target[circuit_model] =\
                    pool_cells
                self.cell_counts[circuit_model] =\
                    cell_types.assign(number=pool_cells.group.value_counts())\
                              .set_index(self.specifiers_cell_type)\
                              .number

        return self.target[circuit_model]

    def get_cells(self, circuit_model, adapter, cell_type=None):
        """
        Population of cells in the circuit model to work with.
        """
        pool_cells =self._load_cells(circuit_model, adapter)

        if cell_type is None:
            return pool_cells

        gids_cell_type =\
            adapter.get_cells(circuit_model, **cell_type)\
                   .index\
                   .to_numpy(np.int32)

        return\
            pool_cells.reindex(gids_cell_type)\
                      .dropna()

    def get_pairs(self, circuit_model, adapter, gids):
        """
        Get pairs between all pooled cells and cells with the argumented gids.
        """
        other_gids =\
            adapter.get_cell_gids(
                circuit_model,
                self.get_cells(circuit_model, adapter))
        return\
            pd.concat([
                pd.DataFrame({
                    self.label_gid: gid,
                    self.label_other_gid: other_gids})
                for gid in gids])

    def get_connections(self,
            circuit_model,
            adapter,
            gids,
            connectivity=None):
        """
        Get connections...
        """
        connectivity =\
            connectivity if connectivity else self.connectivity
        if connectivity == Connectivity.COMPLETE:
            return\
                self.get_pairs(circuit_model, adapter, gids)\
                    .assign(strength=1.)

        all_connections =\
            adapter.get_connections(
                circuit_model,
                gids,
                direction=self.direction)

        LOGGER.debug(
            "PathwayMeasurement get_connections",
            "queried gids {}".format(len(gids)),
            "number connections: {}".format(all_connections.shape[0]))

        if not self.using_subset_of_cells:
            return all_connections

        pooled_gids =\
            adapter.get_cell_gids(
                circuit_model,
                self.get_cells(circuit_model, adapter))
        return\
            all_connections[np.in1d(
                all_connections[self.label_other_gid].to_numpy(np.int32),
                pooled_gids)]

    def get_connected_cells(self, cells, connections):
        """..."""
        return\
            cells.loc[connections[self.label_other_gid].to_numpy(np.int32)]\
                 .dropna()\
                 .assign(**{self.label_gid: connections[self.label_gid].values})

    def _sample_cells(self, circuit_model, adapter, cell_type=None, size=None):
        """..."""
        all_cells =\
            self.get_cells(circuit_model, adapter, cell_type)

        if (self.sampling_methodology == terminology.sampling_methodology.exhaustive
            and size is None):\
           return all_cells

        sample_size = size if size is not None else self.sample_size

        if sample_size == 1:
            return\
                all_cells.sample(1).iloc[0]\
                if all_cells.shape[0] > 0\
                   else None
        if all_cells.shape[0] == 0:
            return\
                pd.DataFrame([], columns=all_cells.columns)

        return\
            all_cells.sample(sample_size)\
            if all_cells.shape[0] > sample_size\
               else all_cells

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

    def _resolve_pair(self, pre_synaptic_cell, post_synaptic_cell):
        """..."""
        if self.direction == "AFF":
            if post_synaptic_cell is None:
                raise TypeError(
                    """
                    Missing argument `post_synaptic_cell` for a pathway
                    measurement to be made in the afferent direction.
                    """)
            return Record(
                cell_type=post_synaptic_cell,
                prefix_aggregated_synaptic_side="pre_synaptic_cell")
                    
        elif self.direction == "EFF":
            if pre_synaptic_cell is None:
                raise TypeError(
                    """
                    Missing argument `pre_synaptic_cell` for a pathway
                    measurement to be made in the direction efferent.
                    """)
            return Record(
                cell_type=pre_synaptic_cell,
                prefix_aggregated_synaptic_side="post_synaptic_cell")
        else:
            LOGGER.warn(
                LOGGER.get_source_info(),
                """
                Unknown direction, will fall on default behavior.
                """)
            if pre_synaptic_cell is None:
                if post_synaptic_cell is None:
                    raise TypeError(
                        """
                        Provide at least one of:
                        1. pre_synaptic_cell
                        2. post_synaptic_cell
                        """)
                else:
                    return Record(
                        cell_type=post_synaptic_cell,
                        prefix_aggregated_synaptic_side="pre_synaptic_cell")
            else:
                if post_synaptic_cell is None:
                    return Record(
                        cell_type=pre_synaptic_cell,
                        prefix_aggregated_synaptic_side="post_synaptic_cell")
                else:
                    raise NotImplementedError(
                        """
                        PathwayMeasurement not implemented when both pre and post
                        synaptic cell groups specified.
                        Meanwhile provide only when.
                        """)
        return RuntimeError(
            "Execution should not reach here.")
 
    def _prefix_aggregated_synaptic_side(self, pair, measured_values):
        """..."""
        if isinstance(measured_values, (pd.Series, pd.DataFrame)):
            if isinstance(measured_values.index, pd.MultiIndex):
                measured_values.index.names =[
                    self._prefix(pair, variable)
                    for variable in measured_values.index.names]
            else:
                measured_values.index.name =\
                    self._prefix(pair, measured_values.index.name)

        return measured_values

    def _prefix(self, pair, variable):
        """..."""
        return\
            (pair.prefix_aggregated_synaptic_side, variable)\
            if variable in self.specifiers_cell_type\
               else variable

    def sample_one(self, circuit_model, adapter,
            pre_synaptic_cell=None,
            post_synaptic_cell=None,
            **kwargs):
        """
        ...
        """
        LOGGER.debug(
            "PathwayMeasurement sample one",
            "pre_synaptic_cell {}".format(pre_synaptic_cell),
            "post_synaptic_cell {}".format(post_synaptic_cell))
        self._check_sampling_methodology(kwargs)
        pair =\
            self._resolve_pair(pre_synaptic_cell, post_synaptic_cell)
        cell =\
            self._sample_cells(
                circuit_model, adapter,
                cell_type=pair.cell_type,
                size=1)
        measured_values =\
            self._prefix_aggregated_synaptic_side(
                pair,
                self._method(
                    circuit_model, adapter, cell,
                    cell_properties_groupby=self.specifiers_cell_type,
                    by_soma_distance=self.by_soma_distance,
                    bin_size_soma_distance=self.bin_size_soma_distance,
                    **kwargs))
        try:
            return measured_values.rename(cell.gid)
        except:
            return measured_values
        raise RuntimeError("Execution should not reach here.")

    def sample_one_old(self, *args, **kwargs):
        """
        Sample of size 1.
        """
        if self.sampling_methodology != terminology.sampling_methodology.random:
            raise TypeError(
                """
                A single size sample makes sense only when sampling randomly.
                This instance of {} was set to
                \t `sampling_methodology {}`.
                """.format(
                    self.__class__.__name__,
                    self.sampling_methodology))
        return head(self.sample(*args, **kwargs))

    def _batches(self, cells):
        """
        Batches of cells to process.
        """
        if self.processing_methodology == terminology.processing_methodology.serial:
            return (cell for _, cell in cells.iterrows())

        n_batches =\
            int(np.floor(cells.shape[0] / self.batch_size))
        batches =\
            [(b * self.batch_size, (b+1) * self.batch_size)
             for b in range(n_batches)] +\
                 [(n_batches * self.batch_size, cells.shape[0])]
        return (cells.iloc[begin_batch: end_batch]
                for (begin_batch, end_batch) in batches)

    def sample(self, circuit_model, adapter,
            pre_synaptic_cell=None,
            post_synaptic_cell=None,
            **kwargs):
        """
        Sample of measurements.

        """
        LOGGER.debug(
            "PathwayMeasurement.sample(...)",
            "with sampling methodology {}".format(self.sampling_methodology))
        self._check_sampling_methodology(kwargs)
        pair =\
            self._resolve_pair(pre_synaptic_cell, post_synaptic_cell)
        cells =\
            self._sample_cells(
                circuit_model, adapter, pair.cell_type)

        for batch_cells in self._batches(cells):
            measurement =\
                self._method(
                    circuit_model, adapter,
                    batch_cells,
                    cell_properties_groupby=self.specifiers_cell_type,
                    by_soma_distance=self.by_soma_distance,
                    bin_size_soma_distance=self.bin_size_soma_distance,
                    **kwargs)
            yield\
                self._prefix_aggregated_synaptic_side(pair, measurement)

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
                        cell_group_to[self.label_gid].to_numpy(np.int32)])
            positions_to =\
                adapter.get_soma_positions(
                    circuit_model,
                    cell_group_to)
            return\
                _binned(np.linalg.norm(
                    positions_to.values - positions_from.values,
                    axis=1))


    @lazyfield
    def label_other_gid(self):
        return\
            "pre_gid" if self.direction == "AFF" else "post_gid"
    @lazyfield
    def label_gid(self):
        return\
            "post_gid" if self.direction == "AFF" else "pre_gid"

    @count_number_calls(LOGGER)
    def _method(self,
            circuit_model, adapter,
            cell_info,
            cell_properties_groupby,
            **kwargs):
        """..."""
        LOGGER.ignore(
            LOGGER.get_source_info(),
            "PathwayMeasurement _method")
        by_soma_distance =\
            kwargs.get("by_soma_distance", self.by_soma_distance)
        bin_size_soma_distance =\
            kwargs.get("bin_size_soma_distance", self.bin_size_soma_distance)
        try:
           return self.value(
               circuit_model, adapter, cell_info,
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
            return _gids(connections, self.label_gid)

        def _gids_connected(connections):
            return _gids(connections, self.label_other_gid)


        if isinstance(cell_info, pd.DataFrame):
            connections =\
                self.get_connections(
                    circuit_model, adapter,
                    cell_info.gid.to_numpy(np.int32))
            value =\
                _get_value(connections)
            variables_groupby =\
                cell_properties_groupby +(
                    [self.label_gid, "soma_distance"]
                    if by_soma_distance else 
                    [self.label_gid])
            columns_relevant =\
                cell_properties_groupby + (
                    [self.label_gid, "soma_distance", self.variable]
                    if by_soma_distance else
                    [self.label_gid, self.variable])
        elif isinstance(cell_info, pd.Series):
            if not "gid" in cell_info.index:
                raise ValueError(
                    """
                    `PathwayMeasurement._method(...)` got a pandas.Series
                    as a `cell_info` that did not contain cell `gid`.
                    """)
            connections =\
                self.get_connections(
                    circuit_model, adapter,
                    np.array([cell_info.gid]))
            value =\
                _get_value(connections)
            variables_groupby =\
                cell_properties_groupby +(
                    ["soma_distance"]
                    if by_soma_distance else
                    [])
            columns_relevant =\
                cell_properties_groupby +(
                    ["soma_distance", self.variable] if by_soma_distance else
                    [self.variable])
        else:
            raise ValueError(
                """
                `PathwayMeasurement._method(...)` does not know how to handle
                `cell_info` {}.
                """.format(cell_info))

        cells_connected =\
            self.get_connected_cells(self.get_cells(circuit_model, adapter),
                                     connections)\
                .assign(**{self.variable: value})
        if by_soma_distance or self.filter_by_upper_bound_soma_distance:
            def _soma_distance(other_cells):
                return\
                    self.get_soma_distance_bins(
                        circuit_model, adapter,
                        cell_info, other_cells,
                        bin_size_soma_distance=bin_size_soma_distance)
            cells_connected =\
                cells_connected.assign(soma_distance=_soma_distance)

        if self.filter_by_upper_bound_soma_distance:
            cells_connected =\
                cells_connected[
                    cells_connected.soma_distance < self.upper_bound_soma_distance]

        cells_connected = cells_connected[columns_relevant]

        LOGGER.ignore(
            LOGGER.get_source_info(),
            "PathwayMeasurement._method(...)",
            "variables_groupby {}".format(variables_groupby),
            "columns_relevant {}".format(columns_relevant),
            "number cells_connected {}".format(cells_connected.shape[0]),
            "columns in cells_connected {}".format(cells_connected.columns))

        try:
            value_groups =\
                cells_connected.groupby(variables_groupby)
        except (TypeError, ValueError):
            value_groups =\
                cells_connected 
        summed_value_groups =\
            value_groups.agg("sum")[self.variable]
        try:
            summed_value_groups =\
                summed_value_groups.droplevel(self.label_gid)
        except (KeyError, AttributeError, ValueError):
            pass

        return summed_value_groups
 
    def collect(self, circuit_model, adapter,
            pre_synaptic_cell=None,
            post_synaptic_cell=None,
            **kwargs):
        """"..."""
        listed_sample =[
            m for m in
            self.sample(
                circuit_model, adapter,
                pre_synaptic_cell=pre_synaptic_cell,
                post_synaptic_cell=post_synaptic_cell,
                **kwargs)]
        try:
            return pd.concat(listed_sample)
        except TypeError:
            return pd.Series(listed_sample, name=self.variable)
        # sample =\
        #     self.sample(
        #         circuit_model, adapter,
        #         pre_synaptic_cell=pre_synaptic_cell,
        #         post_synaptic_cell=post_synaptic_cell,
        #         **kwargs)
        # if self.processing_methodology == terminology.processing_methodology.batch:
        #     return sample

        # listed_sample = [m for m in sample]
        # try:
        #     return pd.concat(listed_sample)
        # except TypeError:
        #     return pd.Series(listed_sample, name=self.variable)
        # pass
    def summary(self, circuit_model, adapter,
            pre_synaptic_cell=None,
            post_synaptic_cell=None,
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
                pre_synaptic_cell=pre_synaptic_cell,
                post_synaptic_cell=post_synaptic_cell,
                **kwargs)
        pair =\
            self._resolve_pair(pre_synaptic_cell, post_synaptic_cell)
        variables_groupby =[
            self._prefix(pair, variable)
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
                    
        # pair =\
        #     self._resolve_pair(
        #         pre_synaptic_cell=pre_synaptic_cell,
        #         post_synaptic_cell=post_synaptic_cell)
        # number_pairs_pathway =\
        #     self.cell_counts[circuit_model].loc[
        #         tuple(pair.cell_type[p] for p in self.specifiers_cell_type)
        #     ] * self.cell_counts[circuit_model]
        return\
            number_connections_pathway / number_pairs_pathway




