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

    def for_sampling(self, size=None):
        """
        Repeat each row of `self.values` 'size' number of times.
        """
        return (
            parameter_row
            for _, parameter_row in self.values.iterrows()
            for _ in range(size if size else self.sample_size) )

    def index(self, sample_size=None):
        """
        A `pandas.Index` / `pandas.MultiIndex` for the parameter values.
        """
        return pandas\
            .DataFrame(
                [parameters_row.to_dict()
                 for parameters_row in self.for_sampling(sample_size)])\
            .set_index(
                list(self.values.columns.values))\
            .index

    @lazyproperty
    def variables(self):
        """
        Names of the parameters.
        """
        return list(self.values.columns.values)
