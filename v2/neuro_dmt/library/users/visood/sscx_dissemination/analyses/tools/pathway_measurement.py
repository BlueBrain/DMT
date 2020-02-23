"""
Measure pathways.
"""
import numpy as np
import pandas as pd
from dmt.tk.collections import head, Record
from dmt.tk.field import Field, lazyfield, WithFields
from dmt.tk.journal.logger import Logger 
from neuro_dmt import terminology

LOGGER = Logger(client=__file__)

class PathwayMeasurement(WithFields):
    """
    Measure pathways in a circuit.
    """
    specifiers_cell_type = Field(
        """
        Cell properties that define this pathway.
        """,
        __examples__=["mtype", "etype"],
        __default_value__=[])
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
        """)
    bin_size_soma_distance = Field(
        """
        Size of soma distance bins (in um) 
        """,
        __default_value__=100)
    summaries = Field(
        """
        Summaries required, if making a summary measurement.
        """,
        __default_value__=[
            "count", "sum", "mean", "mad", "std", "var", "min", "median", "max"])

    def _sample_cells(self, circuit_model, adapter, cell_type=None, size=None):
        """..."""
        all_cells =\
            adapter.get_cells(circuit_model, **cell_type)\
            if cell_type is not None\
               else adapter.get_cells(circuit_model)

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

        return (cells,)


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
                    cells,
                    cell_properties_groupby=self.specifiers_cell_type,
                    by_soma_distance=self.by_soma_distance,
                    bin_size_soma_distance=self.bin_size_soma_distance,
                    **kwargs)
            yield\
                self._prefix_aggregated_synaptic_side(pair, measurement)
        # if self.processing_methodology == terminology.processing_methodology.batch:
        #     def measurement():
        #         measurement =\
        #             self._prefix_aggregated_synaptic_side(
        #                 pair,
        #                 self._method(
        #                     circuit_model, adapter,
        #                     cells,
        #                     cell_properties_groupby=self.specifiers_cell_type,
        #                     by_soma_distance=self.by_soma_distance,
        #                     bin_size_soma_distance=self.bin_size_soma_distance,
        #                     **kwargs))
        #         try:
        #             return measurement.rename(cell.gid)
        #         except:
        #             return measurement
        # else:
        #     def measurement():
        #         for _, cell in cells.iterrows():
        #             measurement_one =\
        #                 self._prefix_aggregated_synaptic_side(
        #                     pair,
        #                     self._method(
        #                         circuit_model, adapter,
        #                         cell,
        #                         cell_properties_groupby=self.specifiers_cell_type,
        #                         by_soma_distance=self.by_soma_distance,
        #                         bin_size_soma_distance=self.bin_size_soma_distance,
        #                         **kwargs))
        #             try:
        #                 yield measurement_one.rename(cell.gid)
        #             except:
        #                 yield measurement_one
                
        # return measurement()

    @staticmethod
    def get_soma_distance_bins(
            circuit_model,
            adapter,
            cell,
            cell_group,
            bin_size=100.,
            bin_mids=True):
        """
        Get binned distance of `cell`'s soma from soma of all the cells in
        `cell_group`.
        """
        distance =\
            adapter.get_soma_distance(
                circuit_model,
                cell, cell_group)
        bin_starts =\
            bin_size * np.floor(distance / bin_size)
        return\
            [bin_start + bin_size / 2. for bin_start in bin_starts]\
            if bin_mids else\
               [[bin_start, bin_size] for bin_start in bin_starts]

    @lazyfield
    def label_other_gid(self):
        return\
            "pre_gid" if self.direction == "AFF" else "post_gid"
    @lazyfield
    def label_gid(self):
        return\
            "post_gid" if self.direction == "AFF" else "pre_gid"

    def _single(self, circuit_model, adapter,
            cell,
            cell_properties_groupby,
            by_soma_distance,
            bin_size_soma_distance,
            **kwargs):
        """
        Make measurement for a single cell.

        Arguments
        --------------
        cell :: pandas.Series containing information about the cell.
        """
        """..."""
        LOGGER.debug(
            "PathwayMeasurement _single(...) for cell {}".format(cell))
        connections =\
            adapter.get_connections(
                circuit_model,
                cell,
                direction=self.direction)
        LOGGER.debug(
            "PathwayMeasurement _single(...) connections "\
            .format(connections.shape[0]))
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
        variables_groupby =\
            cell_properties_groupby +(
                ["soma_distance"] if by_soma_distance else [])
        columns_relevant =\
            cell_properties_groupby + (
                [self.variable, "soma_distance"]\
                if by_soma_distance else\
                [self.variable])
        cells_connected =\
            adapter.get_cells(circuit_model)\
                   .loc[connections[self.label_other_gid].values]\
                   .assign(**{self.variable: value})
        if by_soma_distance:
            def _soma_distance(other_cells):
                return\
                    self.get_soma_distance_bins(
                        circuit_model, adapter,
                        cell, other_cells,
                        bin_size=bin_size_soma_distance)
            cells_connected =\
                cells_connected.assign(soma_distance=_soma_distance)

        cells_connected = cells_connected[columns_relevant]

        try:
            value_groups =\
                cells_connected.groupby(variables_groupby)
        except (TypeError, ValueError):
            value_groups =\
                cells_connected 
        return\
            value_groups.agg("sum")[self.variable]

    def _method(self,
            circuit_model, adapter,
            cell_info,
            cell_properties_groupby,
            by_soma_distance,
            bin_size_soma_distance,
            **kwargs):
        """..."""
        LOGGER.debug(
            LOGGER.get_source_info(),
            "PathwayMeasurement _method",
            "cell: {}".format(cell_info),
            "group by {}".format(cell_properties_groupby))
        try:
           return self.value(
               circuit_model, adapter, cell_info,
               cell_properties_groupby=cell_properties_groupby,
               by_soma_distance=self.by_soma_distance,
               bin_size_soma_distance=self.bin_size_soma_distance,
               **kwargs)
        except (TypeError, ValueError):
            pass
            # if isinstance(cell_info, pd.Series):
            #     return self._single(
            #         circuit_model, adapter,
            #         cell_info,
            #         cell_properties_groupby,
            #         by_soma_distance,
            #         bin_size_soma_distance,
            #         **kwargs)

        def _get_connections(gids):
            connections =\
                adapter.get_connections(
                    circuit_model,
                    gids,
                    direction=self.direction)
            LOGGER.debug(
                LOGGER.get_source_info(),
                "PathwayMeasurement _method",
                "number connections: {}".format(connections.shape[0]))
            return connections

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
                _get_connections(
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
            cells_connected =\
                adapter.get_cells(circuit_model)\
                       .loc[_gids_connected(connections)]\
                       .assign(**{self.label_gid: _gids_measured(connections),
                                  self.variable: value})
        elif isinstance(cell_info, pd.Series):
            if not "gid" in cell_info.index:
                raise ValueError(
                    """
                    `PathwayMeasurement._method(...)` got a pandas.Series
                    as a `cell_info` that did not contain cell `gid`.
                    """)
            connections =\
                _get_connections(
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
            cells_connected =\
                adapter.get_cells(circuit_model)\
                       .loc[_gids_connected(connections)]\
                       .assign(**{self.variable: value})
        else:
            raise ValueError(
                """
                `PathwayMeasurement._method(...)` does not know how to handle
                `cell_info` {}.
                """.format(cell_info))

        LOGGER.debug(
            LOGGER.get_source_info(),
            "PathwayMeasurement._method(...)",
            "variables_groupby {}".format(variables_groupby),
            "columns_relevant {}".format(columns_relevant),
            "number cells_connected {}".format(cells_connected.shape[0]),
            "columns in cells_connected {}".format(cells_connected.columns))

        if by_soma_distance:
            def _soma_distance(other_cells):
                return\
                    self.get_soma_distance_bins(
                        circuit_model, adapter,
                        cell_info, other_cells,
                        bin_size=bin_size_soma_distance)
            cells_connected =\
                cells_connected.assign(soma_distance=_soma_distance)

        cells_connected = cells_connected[columns_relevant]

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
        except KeyError:
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
            **kwargs):
        """..."""
        aggregators =\
            self.summaries[0] if len(self.summaries) == 1 else self.summaries
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
        return\
            collection.groupby(variables_groupby).agg(aggregators)
