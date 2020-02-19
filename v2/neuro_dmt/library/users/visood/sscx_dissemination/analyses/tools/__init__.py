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
                specifier_aggregated_synaptic_side_cells =\
                    list(post_synaptic_cell.keys())
                prefix_aggregated_synaptic_side =\
                    "pre_synaptic_cell"
        else:
            if post_synaptic_cell is None:
                cell_type =\
                    pre_synaptic_cell
                specifier_aggregated_synaptic_side_cells =\
                    list(pre_synaptic_cell.keys())
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
                if variable in specifier_aggregated_synaptic_side_cells\
                   else variable

        for _, cell in self.cells(cell_type, circuit_model, adapter).iterrows():
            measurement =\
                self.method(
                    circuit_model, adapter, cell,
                    cell_properties_groupby=specifier_aggregated_synaptic_side_cells,
                    by_soma_distance=self.by_soma_distance,
                    bin_size_soma_distance=self.bin_size_soma_distance,
                    **kwargs)
            if isinstance(measurement.index, pd.MultiIndex):
                measurement.index.names =[
                    _prefix(variable) for variable in measurement.index.names]
            else:
                measurement.index.name = _prefix(measurement.index.name)

            yield measurement.rename(cell.gid)

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
                adapter.get_afferent_connections(
                    circuit_model,
                    cell)
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
                       .loc[connections.pre_gid.values]\
                       .assign(**{self.variable: self.value(connections)})
            if by_soma_distance:
                def _soma_distance(other_cells):
                    return\
                        self.get_soma_distance_bins(
                            circuit_model, adapter,
                            cell, other_cells,
                            bin_size=bin_size_soma_distance)
                cells_afferent =\
                    cells_afferent.assign(soma_distance=_soma_distance)
            value_measurement =\
                cells_afferent[columns_relevant].groupby(variables_groupby)\
                                                .agg("sum")
            return\
                value_measurement[self.variable]
        



    def collect(self, *args, **kwargs):
        """"..."""
        return\
            pd.concat(
                [m for m in self.sample(*args, **kwargs)],
                axis=1)

    def summary(self, *args, **kwargs):
        """..."""
        return\
            self.collect(*args, **kwargs)\
                .agg(["count", "sum",
                       "mean", "mad", "std", "var",
                       "min", "median", "max"],
                     axis=1)
