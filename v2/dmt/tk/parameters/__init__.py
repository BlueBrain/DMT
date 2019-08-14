"""
Utility classes to handle measurement parameters.
"""

import pandas
from dmt.tk.field import Field, lazyproperty, WithFields

class Parameters(WithFields):
    """
    Parameters for a measurement.
    """
    values = Field(
        """
        A `pandas.DataFrame` that holds each set of parameter values
        in its rows, with column names corresponding to the parameters'
        variable names.
        """)
    sample_size = Field(
        """
        Number of times each parameter row must be sampled by a measurement.
        """,
        __default_value__=20)

    def __init__(self,
            dataframe,
            *args, **kwargs):
        """
        Initialize with pandas.DataFrame values as an argument.
        """
        super().__init__(
            values=dataframe,
            *args, **kwargs)

    @property
    def for_sampling(self):
        """
        Repeat each row of `self.values` 'size' number of times.
        """
        return (
            parameter_row
            for _, parameter_row in self.values.iterrows()
            for _ in range(self.sample_size) )

    @lazyproperty
    def index(self):
        """
        A `pandas.Index` / `pandas.MultiIndex` for the parameter values.
        """
        return pandas\
            .DataFrame(
                [parameters_row.to_dict()
                 for parameters_row in self.for_sampling])\
            .set_index(
                list(self.values.columns.values))\
            .index


