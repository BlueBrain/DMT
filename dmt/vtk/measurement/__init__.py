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
from dmt.vtk.measurement.parameters import GroupParameter

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
    def __call__(self, *measurement_parameters):
        """Perform a single measurement.

        Implementation Guidelines
        ------------------------------------------------------------------------
        1. This method defines the measurement, and will be used to collect
        ~  a sample.
        2. Please provide a good doc-string in your implementation -- it will be
        ~  called by a reporter or a caption generator.
        """
        pass

    def get(self, *measurement_parameters):
        """Perform a single measurement for the given parameters.
        This is an alias..."""
        return self.__call__(*measurement_parameters)

    def sample(self, parameter_sampler):
        """Sample measurement. 

        Parameters
        ------------------------------------------------------------------------
        parameter_sampler :: Record(
        ~   group :: Record(label  :: str, #label for parameter groups,
        ~                   values :: list), #values assumed by parameter groups
        ~   sample :: ParameterGroup -> Generator[MeasurementParameter]
        )
        Implementation Notes
        ------------------------------------------------------------------------
        Take a sample of measurements for each of the parameter groups,
        and return a pandas DataFrame that provides the parameter group along 
        with the measurement value in each row.
        """
        data = pd.DataFrame([{parameter_sampler.group.label: g,
                              self.label: self.get(p)}
                             for g in parameter_sampler.group.values
                             for p in parameter_sampler.sample(g)])\
                 .sort_values(by=parameter_sampler.group.label)
        return Record(name = self.label,
                      method = self.__call__.__doc__,
                      data = data,
                      parameter_group = parameter_sampler.group.label)

    def statistical_measurement(self, parameter_sampler):
        """take a sample and return its statistical summary."""
        s = self.sample(parameter_sampler)
        return Record(phenomenon = self.phenomenon,
                      label = self.label,
                      method = self.__call__.__doc__,
                      data = summary_statistic(s),
                      parameter_group = parameter_sampler.group.label)


class StatisticalMeasurement:
    """A method, augmented with statistical functionality."""
    group_parameters = Field(
        __name__ = "group_parameter",
        __type__ = list,
        __is_valid_value__ = lambda gps: all(issubclass(gp, GroupParameter),
                                             for gp in gps)
        __doc__ = """The GroupParameter types associated with this
        StatisticalMethod."""
    )
    def __init__(self, method, by):
        """...
        """
        self.group_parameters = by
        self.method = method

    def sample(self, model):
        """..."""
        df = parameters.get_values(self.group_parameters)
        measured_values = [self.method(model)(dict(row[1])) for row in df.iterrows()]
        df[self.get_one.label] = measured_values
        df = df.sort_values(by=[gp.label for gp in self.group_parameters])

        return Record(name = self.label,
                      method = self.method.__call__.__doc__, #fix this
                      data = df,
                      parameter_group = parameter_sampler.group.label)

    def __call__(self, model, group_parameter_values=None):
        s = self.sample(model, group_parameter_values)
        return Record(phenomenon = self.phenomenon,
                      label = self.label,
                      method = self.get_one.__doc__,
                      data = summary_statistic(s),
                      parameter_group = parameter_sampler.group.label)



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
