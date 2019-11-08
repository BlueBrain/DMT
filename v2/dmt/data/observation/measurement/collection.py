"""
Utiility methods to create collections of individual measurements.
"""
from collections.abc import Mapping
import pandas as pd
from dmt.tk.parameters import index_tree

def _with_index(dataframe):
    """..."""
    return\
        dataframe.set_index([
            column
            for column in dataframe.columns
            if column != "value"])

def primitive_type(measurement_generator):
    """
    Use when individual measurements are primitive types...

    Arguments
    -----------
    `measurement_generator` is a generator of individual measurements,
    each of which must be a tuple: (parameters, values)
    """
    def _join(parameters_measurement, value_measurement):
        """..."""
        if isinstance(parameters_measurement, Mapping):
            parameters_measurement =\
                pd.Series(
                    index_tree.as_unnested_dict(
                        parameters_measurement))
        return\
            parameters_measurement.append(
                pd.Series({"value": value_measurement}))
    return _with_index(
        pd.DataFrame([
            _join(parameters, value)
            for parameters, value in measurement_generator]))

def series_type(measurement_generator):
    """
    Use when individual measurements are pandas.Series
    """
    def _join(parameters_measurement, value_measurement):
        """..."""
        if isinstance(parameters_measurement, Mapping):
            parameters_measurement =\
                pd.Series(
                    index_tree.as_unnested_dict(
                        parameters_measurement))
        return\
            value_measurement.rename("value")\
                             .reset_index()\
                             .apply(
                                 parameters_measurement.append,
                                 axis=1)
                                     
    return _with_index(
        pd.concat([
            _join(*args)
            for args in measurement_generator]))

