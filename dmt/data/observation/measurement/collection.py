# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

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


def summary_type(
        measurement_generator,
        sample_type,
        summary_variable):
    """
    Use to convert a collection of sample measurements to a statistical summary.
    """
    return\
        sample_type(measurement_generator)\
        .groupby(summary_variable)\
        .agg(["size", "mean", "std"])


def summary_series_type(
        measurement_generator,
        summary_variable):
    """..."""
    return\
        summary_type(measurement_generator,
                     series_type,
                     summary_variable)

def summary_primitive_type(
        measurement_generator,
        summary_variable):
    """..."""
    return\
        summary_type(measurement_generator,
                     primitive_type,
                     summary_variable)



