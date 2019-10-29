"""
Utility classes to handle measurement parameters.
"""

from types import GeneratorType
import pandas
from dmt.tk.field import Field, lazyproperty, WithFields
from dmt.tk.utils import Nothing
from dmt.tk.collections.data import make_hashable

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
            with_labels=True,
            *args, **kwargs):
        """
        Arguments
        --------------
        `values`: Either a dataframe, or a callable on (adapter, model)
        `with_labels`: Either the names of the parameters, or a boolean 
        indicating whether this instance of `Parameters` should have labels.

        Note
        ---------------
        Parameter labels may not be well defined for instances that are
        initialized from callables. The callables are allowed to return an 
        iterable mapping of parameter label to its value --- the labels allowed
        to change from one mapping in the iterable to the next. Thus the set
        of parameter labels covering all the mappings can be become arbitrary.
        In  such cases, the user is advised to set `with_labels` to `False`.
        """
        if callable(values):
            pass
        elif isinstance(values, pandas.DataFrame) and with_labels:
            if kwargs.get("labels", tuple()):
                raise TypeError(
                    """
                    'labels' provided for initializing `Parameters` from a
                    pandas.DataFrame.
                    When initialized from a pandas.DataFrame, parameters will 
                    be initialized from the dataframe's columns.
                    """)
            kwargs["labels"] = list(values.columns.values)
        else:
            raise ValueError(
                "Provided values should be a callable or a dataframe.")
        kwargs["values"] = values
        super().__init__(
            *args, **kwargs)
        self._with_labels = with_labels

    def for_model(self, *args):
        """
        Parameters for a model.

        With an adapter, model in `*args`, this creates a new instance of
        `Parameters` initialized with a pandas DataFrame.
        """
        if not callable(self.values):
            raise TypeError("Parameters defined with a dataframe.")
        return Parameters(pandas.DataFrame(self.values(*args)))

    def _resolve_values(self, *args):
        """
        Return a dataframe for values.
        """
        if callable(self.values):
            values = self.values(*args)
            return list(values) if isinstance(values, GeneratorType) else values
        return self.values

    def _set_labels(self, values):
        """
        Set labels affirming to `values`, but only if they are not already set,
        and if the dataframe generated from them does not have any null values.
        """
        if not self._with_labels:
            return None
        if not self.labels:
            dataframe = pandas.DataFrame(values)
            if not dataframe.isnull().values.any():
                self.labels = list(dataframe.columns.values)
        return self.labels

    def for_sampling(self, *args, size=None):
        """
        Repeat each row of `self.values` 'size' number of times.
        """
        size = size if size else self.sample_size
        values = self._resolve_values(*args)
        self._set_labels(values)

        try:
            parameter_rows = [row for _, row in values.iterrows()]
        except AttributeError:
            parameter_rows = values

        return list(
            parameter_row
            #dict(parameter_row)
            for parameter_row in parameter_rows
            for _ in range(size))
            
    def as_dataframe(self, parameter_values):
        """
        Arguments
        --------
        `parameter_values` : A pandas.DataFrame or a list of parameter rows,
        each of which is a mapping (or a pandas Series)...
        """
        if isinstance(parameter_values, pandas.DataFrame):
            return parameter_values
        assert isinstance(parameter_values, list)
        return pandas\
            .DataFrame(parameter_values)\
            .apply(make_hashable, axis=0)

    def get_index(self, parameter_values):
        """
        Get a `pandas.Index` / `pandas.MultiIndex` for the parameter values.

        Arguments
        -------------
        `parameter_values`: A list of mappings (label --> value)
        """
        dataframe = self.as_dataframe(parameter_values)
        return dataframe.set_index(list(dataframe.columns.values)).index


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
