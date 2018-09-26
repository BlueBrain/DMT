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
from dmt.vtk.measurement.parameter import Parameter
from dmt.vtk.measurement.parameter.random \
    import RandomVariate, ConditionedRandomVariate
from dmt.vtk.utils.logging import with_logging, Logger
    

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

 

@with_logging(Logger.level.STUDY)
class StatisticalMeasurement:
    """Make statistical measurements."""
    random_variate = Field(
        __name__ = "random_variate",
        __type__ = RandomVariate,
        __doc__  = """A random variate can be sampled."""
    )
    sample_size = Field(
        __name__="sample_size",
        __type__=int,
        __doc__="""Number of samples to be drawn for each statistical measurement."""
    )
    def __init__(self, random_variate, sample_size=20):
        """..."""
        self.random_variate = random_variate
        self.sample_size = sample_size

    def sample(self, method, size=20, *args, **kwargs):
        """..."""
        params = self.random_variate.sample(size=size, *args, **kwargs)
        self.logger.debug(
            "StatisticalMeasurement.sample(...) params index: {}"\
            .format(params.index)
        )
        data = [method(**row[1]) for row in params.iterrows()]
        measurement = pd.DataFrame({method.label: data}, index=params.index)
        self.logger.debug(
            "StatisticalMeasurement.sample(...) measurement.index: {}"\
            .format(measurement.index)
        )
        return measurement

    def __call__(self, method, *args, **kwargs):
        """call me"""
        data = summary_statistic(self.sample(
            method,
            size=kwargs.get("size", self.sample_size),
            *args, **kwargs
        ))
        levels = data.index.names
        if len(levels) == 1:
            return Record(phenomenon=method.phenomenon,
                          label=method.label,
                          method=method_description(method),
                          data=data,
                          units=method.units,
                          parameter=levels[0])

        return Record(phenomenon=method.phenomenon,
                      label=method.label,
                      method=method_description(method),
                      data=data,
                      units=method.units,
                      parameter_groups=levels)


def method_description(measurement_method):
    """Description of the measurement's method.

    Parameters
    ----------------------------------------------------------------------------
    measurement_method :: Method
    """
    return measurement_method.__call__.__doc__

def summary_statistic(measurement_sample,
                      parameter_columns=[],
                      measurement_columns=[]):
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
