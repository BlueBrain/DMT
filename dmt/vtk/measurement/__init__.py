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
from dmt.vtk.measurement.parameter.group import get_grouped_values
from dmt.vtk.measurement.parameter.random \
    import RandomVariate, ConditionedRandomVariate
    

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
    def __init__(self, method, by):
        """...
        """
        self.method = method
        self.random_variate = by

    def sample(self, *args, **kwargs):
        """..."""

        vdf = self.random_variate.sample(*args, **kwargs)
        vdf[self.method.label]\
            = [self.method(**row[1]) for row in vdf.iterrows()]
        return vdf[[self.method.label]]

    def __call__(self, *args, **kwargs):
        """call me"""
        data = summary_statistic(self.sample(*args, **kwargs))
        levels = data.index.names
        if len(levels) == 1:
            return Record(phenomenon = self.method.phenomenon,
                          label = self.method.label,
                          method = method_description(self.method),
                          data = data,
                          units = self.method.units,
                          parameter_group = levels[0])

        return Record(phenomenon = self.method.phenomenon,
                      label = self.method.label,
                      method = method_description(self.method),
                      data = data,
                      units = self.method.units,
                      parameter_groups = levels)


def method_description(measurement_method):
    """Description of the measurement's method.

    Parameters
    ----------------------------------------------------------------------------
    measurement_method :: Method
    """
    return measurement_method.__call__.__doc__

def summary_statistic(measurement_sample,
                      parameter_columns=None,
                      measurement_columns=None):
    """Summarize a data-frame.
    Type of the returned data-frame depends on the type of
    'measurement_columns'. Thus this method can accommodate more than one
    parameter columns in the measurement to be summarized, as well as it can
    summarize more than one measurement columns."""
    aggregators = ["mean", "std"]
    if not parameter_columns:
        return measurement_sample.groupby(level=measurement_sample.index.names)\
                                 .agg(aggregators)

    summary = measurement_sample.groupby(parameter_columns).agg(aggregators)
    measurement_columns = measurement_columns if measurement_columns \
                          else summary.columns.levels[0]
    if len(measurement_columns) == 1:
        return summary[measurement_columns[0]]
    return summary[measurement_columns]
