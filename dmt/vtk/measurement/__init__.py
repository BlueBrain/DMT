"""Measurement is the assignment of a number to a characteristic of an object
or event, which can be compared with other objects or events.
Measurement is the determination or estimation of ratios of quantities.
Measurement is the correlation of numbers with entities that are not numbers.
Statistically speaking, a measurement is a set of observations that reduce
uncertainty where the result is expressed as a quantity. There is not a clear
distinction between estimation and measurement."""

from abc import ABC, abstractmethod
import collections
import pandas as pd
from dmt.vtk.utils.collections import Record
from dmt.vtk.utils.descriptor import ClassAttribute, Field
from dmt.vtk.measurement import parameters
from dmt.vtk.measurement.parameters import GroupParameter, get_grouped_values

class Measurement:
    """Contains the result of measuring something,
    and associated meta-data.

    Implemented this.
    """
    pass


class Method(ABC):
    """A class that encapsulates data and methods needed by a statistical
    measurement."""

    units = ClassAttribute(
        __name__ = "units",
        __type__ = str,
        __doc__  = """String representation of the units of the
        measurement value computed by this Method. Notice that in the future,
        we may use a class Unit."""
    )
    @property
    @abstractmethod
    def label(self):
        """
        Return
        ------------------------------------------------------------------------
        type str #to be used in a report, plot, plot-caption, data-frame column
        """
        pass

    @property
    @abstractmethod
    def phenomenon(self) :
        """The measured phenomenon."""
        pass

    @abstractmethod
    def __call__(self, **measurement_parameters):
        """Perform a single measurement.

        Implementation Guidelines
        ------------------------------------------------------------------------
        1. This method defines the measurement, and will be used to collect
        ~  a sample.
        2. Please provide a good doc-string in your implementation -- it will be
        ~  called by a reporter or a caption generator.
        """
        pass

    def get(self, **measurement_parameters):
        """Perform a single measurement for the given parameters.
        This is an alias..."""
        return self.__call__(**measurement_parameters)

 
class StatisticalMeasurement:
    """A method, augmented with statistical functionality."""
    group_parameters = Field(
        __name__ = "group_parameter",
        __type__ = list,
        __is_valid_value__ = lambda gps: all(issubclass(gp, GroupParameter)
                                             for gp in gps),
        __doc__ = """The GroupParameter types associated with this
        StatisticalMethod."""
    )
    def __init__(self, method, by):
        """...
        """
        if isinstance(by, list):
            self.group_parameters = by
        else:
            self.group_parameters = [by]
        self.method = method

    def sample(self, *model_args):
        """..."""
        gps = self.group_parameters
        df = get_grouped_values(gps, *model_args)
        measured_values = [
            self.method(**row[1][[p.grouped_variable.name for p in gps]])
            for row in df.iterrows()
        ]
        df[self.method.label] = measured_values
        df = df.sort_values(by=[gp.label for gp in gps])
        return df[[self.method.label] + [gp.label for gp in gps]]

    def __call__(self, *model_args):
        """call me"""
        data = summary_statistic(self.sample(*model_args),
                                 [pg.label for pg in self.group_parameters])
        if len(self.group_parameters) == 1:
            return Record(phenomenon = self.method.phenomenon,
                          label = self.method.label,
                          method = method_description(self.method),
                          data = data,
                          units = self.method.units,
                          parameter_group = self.group_parameters[0])

        return Record(phenomenon = self.method.phenomenon,
                      label = self.method.label,
                      method = method_description(self.method),
                      data = data,
                      units = self.method.units,
                      parameter_groups = self.group_parameters)


def method_description(measurement_method):
    """Description of the measurement's method.

    Parameters
    ----------------------------------------------------------------------------
    measurement_method :: Method
    """
    return measurement_method.__call__.__doc__

def summary_statistic(measurement_sample,
                      parameter_columns,
                      measurement_columns=None):
    """Summarize a data-frame.
    Type of the returned data-frame depends on the type of
    'measurement_columns'. Thus this method can accommodate more than one
    parameter columns in the measurement to be summarized, as well as it can
    summarize more than one measurement columns."""
    summary = measurement_sample.groupby(parameter_columns).agg(["mean", "std"])
    measurement_columns = measurement_columns if measurement_columns \
                          else summary.columns.levels[0]
    if len(measurement_columns) == 1:
        return summary[measurement_columns[0]]
    return summary[measurement_columns]
