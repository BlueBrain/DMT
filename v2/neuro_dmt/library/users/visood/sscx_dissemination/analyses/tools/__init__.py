"""
Tools to help analyze.
"""
import numpy as np
import pandas as pd
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
        __default_value__=1)
    by_soma_distance = Field(
        """
        Boolean, indicating if the measurements should be made by soma-distance.
        """,
        __default_value__=True)
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

    def cells(self, cell_type, circuit_model, adapter):
        """..."""
        all_cells =\
            adapter.get_cells(circuit_model, **cell_type)
        sampling_random =\
            self.sampling_methodology == terminology.sampling_methodology.random
        return\
            all_cells.sample(self.sample_size)\
            if sampling_random and self.sample_size < all_cells.shape[0]\
               else all_cells

    def sample_one(self, *args, **kwargs):
        """
        Sample of size 1.
        """
        return\
            list(self.sample(*args, **kwargs))[0]

    def sample(self, circuit_model, adapter,
            pre_synaptic_cell=None,
            post_synaptic_cell=None,
            **kwargs):
        """
        Sample of measurements.

        """
        try:
            sampling_methodology = kwargs.pop("sampling_methodology")
            if sampling_methodology != self.sampling_methodology:
                LOGGER.warn(
                    """
                    Argument `sampling_methodology` will be dropped.
                    A sampling methodology of {} was set at the time this {} 
                    instance computing {} was generated.
                    Provided value {} will be dropped.
                    """.format(self.sampling_methodology,
                               self.__class__.__name__,
                               self.method.__name__,
                               sampling_methodology))
        except KeyError:
            pass

        if pre_synaptic_cell is None:
            if post_synaptic_cell is None:
                raise TypeError(
                    """
                    Provide at least one of:
                    1. pre_synaptic_cell
                    2. post_synaptic_cell
                    """)
            else:
                cell_type =\
                    post_synaptic_cell
                prefix_aggregated_synaptic_side =\
                    "pre_synaptic_cell"
        else:
            if post_synaptic_cell is None:
                cell_type =\
                    pre_synaptic_cell
                prefix_aggregated_synaptic_side =\
                    "post_synaptic_cell"
            else:
                raise NotImplementedError(
                    """
                    PathwayMeasurement not implemented when both pre and post
                    synaptic cell groups specified.
                    Meanwhile provide only when.
                    """)

        def _prefix(variable):
            return\
                (prefix_aggregated_synaptic_side, variable)\
                if variable in self.specifiers_cell_type\
                   else variable

        for _, cell in self.cells(cell_type, circuit_model, adapter).iterrows():
            measurement =\
                self.method(
                    circuit_model, adapter, cell,
                    cell_properties_groupby=self.specifiers_cell_type,
                    by_soma_distance=self.by_soma_distance,
                    bin_size_soma_distance=self.bin_size_soma_distance,
                    **kwargs)
            if isinstance(measurement, (pd.Series, pd.DataFrame)):
                if isinstance(measurement.index, pd.MultiIndex):
                    measurement.index.names =[
                        _prefix(variable) for variable in measurement.index.names]
                else:
                    measurement.index.name = _prefix(measurement.index.name)
                    
                yield measurement.rename(cell.gid)
            else:
                yield measurement

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
    def label_gid(self):
        return\
            "pre_gid" if self.direction == "AFF" else "post_gid"

    def method(self, circuit_model, adapter, cell,
            cell_properties_groupby,
            by_soma_distance,
            bin_size_soma_distance,
            **kwargs):
        """..."""
        try:
            return\
                self.value(
                    circuit_model, adapter, cell,
                    cell_properties_groupby=cell_properties_groupby,
                    by_soma_distance=self.by_soma_distance,
                    bin_size_soma_distance=self.bin_size_soma_distance,
                    **kwargs)
        except TypeError:
            connections =\
                adapter.get_connections(
                    circuit_model,
                    cell,
                    direction=self.direction)
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
            cells_afferent =\
                adapter.get_cells(circuit_model)\
                       .loc[connections[self.label_gid].values]\
                       .assign(**{self.variable: value})
            if by_soma_distance:
                def _soma_distance(other_cells):
                    return\
                        self.get_soma_distance_bins(
                            circuit_model, adapter,
                            cell, other_cells,
                            bin_size=bin_size_soma_distance)
                cells_afferent =\
                    cells_afferent.assign(soma_distance=_soma_distance)
            cells_afferent = cells_afferent[columns_relevant]

            try:
                value_groups =\
                    cells_afferent.groupby(variables_groupby)
            except TypeError:
                value_groups =\
                    cells_afferent 
            return\
                value_groups.agg("sum")[self.variable]
        
    def collect(self, *args, **kwargs):
        """"..."""
        return\
            pd.concat(
                [m for m in self.sample(*args, **kwargs)],
                axis=1)

    def summary(self,
            *args, **kwargs):
        """..."""
        aggregators =\
            self.summaries[0] if len(self.summaries) == 1 else self.summaries
        return\
            self.collect(*args, **kwargs)\
                .agg(aggregators, axis=1)
