"""
Utility classes to handle measurement parameters.
"""

import pandas
from dmt.tk.field import Field, lazyproperty, WithFields
from dmt.tk.utils import Nothing

class Parameters(WithFields):
    """
    Parameters for a measurement.
    """
    values = Field(
        """
        Either A `pandas.DataFrame` that holds each set of parameter values
        in its rows, with column names corresponding to the parameters'
        variable names, or a callable taking (adapter, model) as arguments,
        with labels for the parameters provided separated.
        """,
        __default_value__=Nothing)
    labels = Field(
        """
        A tuple of parameter labels. If not provided, `class Parameters` will
        try to extract these from the provided values.
        """,
        __default_value__=tuple())
    sample_size = Field(
        """
        Number of times each parameter row must be sampled by a measurement.
        """,
        __default_value__=20)

    def __init__(self,
            values,
            *args, **kwargs):
        """
        Arguments
        --------------
        `values`: Either a dataframe, or a callable on (adapter, model)
        `labels`: The names of the parameters
        """
        if callable(values):
            pass
        elif isinstance(values, pandas.DataFrame):
            kwargs["labels"] = values.columns.values
        else:
            raise ValueError(
                "Provided values should be a callable or a dataframe.")
        kwargs["values"] = values
        super().__init__(
            *args, **kwargs)

    def for_model(self, *args):
        """
        Parameters for a model.
        """
        if not callable(self.values):
            raise TypeError("Parameters defined with a dataframe.")
        return Parameters(self.values(*args))

    def _resolve_values(self, *args):
        return self.values(*args) if callable(self.values) else self.values

    def for_sampling(self, *args, size=None):
        """
        Repeat each row of `self.values` 'size' number of times.
        """
        values = self._resolve_values(*args)
        self.labels = values.columns.values
        return (
            parameter_row
            for _, parameter_row in values.iterrows()
            for _ in range(size if size else self.sample_size) )

    def index(self, *args, sample_size=None):
        """
        A `pandas.Index` / `pandas.MultiIndex` for the parameter values.
        """
        values = self._resolve_values(*args)
        return pandas\
            .DataFrame(
                [parameters_row.to_dict()
                 for parameters_row in self.for_sampling(*args, size=sample_size)])\
            .set_index(
                list(values.columns.values))\
            .index

    @lazyproperty
    def variables(self):
        """
        Names of the parameters.
        This returns a list that can be used with a `pandas.DataFrame`
        """
        if not self.labels:
            raise TypeError("Parameters lack labels.")
        return list(self.labels)

    def __call__(self, *args, **kwargs):
        """
        Call Me
        """
        pass
