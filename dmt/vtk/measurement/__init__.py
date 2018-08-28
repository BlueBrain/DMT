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

    def sample(self, model):
        """..."""
        gps = self.group_parameters
        df = get_grouped_values(gps)
        measured_values = [
            self.method(**row[1][[p.grouped_variable.name for p in self.gps]])
            for row in df.iterrows()
        ]
        df[self.label] = measured_values
        df = df.sort_values(by=[gp.label for gp in gps])
        return df[[self.label] + [gp.label for gp in gps]]

    def __call__(self, model):
        """call me"""
        if len(self.group_parameters) == 1:
            return Record(phenomenon = self.phenomenon,
                          label = self.label,
                          method = method_description(self.method),
                          data = summary_statistic(self.sample(model)),
                          parameter_group = self.group_parameters[0].label)

        return Record(phenomenon = self.phenomenon,
                      label = self.label,
                      method = method_description(self.method),
                      data = summary_statistic(self.sample(model)),
                      parameter_groups = [gp.label for gp in self.group_parameters])



def method_description(measurement_method):
    """Description of the measurement's method.

    Parameters
    ----------------------------------------------------------------------------
    measurement_method :: Method
    """
    return measurement_method.__call__.__doc__

def summary_statistic(measurement_sample):
    """summarize a data-frame."""
    return measurement_sample.data\
                             .groupby(measurement_sample.parameter_group)\
                             .agg(["mean", "std"])\
                             [measurement_sample.name]
