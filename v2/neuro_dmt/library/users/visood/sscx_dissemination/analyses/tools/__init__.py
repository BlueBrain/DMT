"""
Tools to help analyze.
"""
import pandas as pd
from dmt.tk.field import Field, lazyfield, WithFields
from neuro_dmt import terminology


class PathwayMeasurement(WithFields):
    """
    Measure pathways in a circuit.
    """
    # circuit_model = Field(
    #     """
    #     Cicuit on which measurement should be made.
    #     """)
    # adapter = Field(
    #     """
    #     Adapter for the circuit model on which this instance's
    #     measurement method will apply.
    #     """)
    method = Field(
        """
        Measurement method for a single set of parameter-values.
        """)
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

    def sample(self, circuit_model, adapter,
            pre_synaptic_cell=None,
            post_synaptic_cell=None):
        """
        Sample of measurements.
        """
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
                self.method(circuit_model, adapter, cell,
                            variables_groupby=specifier_aggregated_synaptic_side_cells,
                            by_soma_distance=self.by_soma_distance,
                            bin_size_soma_distance=self.bin_size_soma_distance,
                            prefix_synaptic=prefix_aggregated_synaptic_side)\
                    .rename(cell.gid)
            if isinstance(measurement.index, pd.MultiIndex):
                measurement.index.names =[
                    _prefix(variable) for variable in measurement.index.names]
            else:
                measurement.index.name = _prefix(variable)

            yield measurement
