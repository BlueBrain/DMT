import numpy
import pandas
from ..observation import *


class Measurement(
        Observation):
    """
    Measurement is an Observation of a phenomenon described by a numerical
    variable.
    By default, a `Measurement` instance is expected to contain several
    samples for each combination of parameter values.
    """
    __metaclass_base__ = True

    @lazyfield
    def parameters_list(self):
        """
        List of parameter labels.
        """
        return list(self.parameters.keys())

    def _get_sample_parameters(self,
            parameters_values,
            sample_size):
        """
        Get a pandas.DataFrame that represents the parameters
        to make a sample of measurements.

        Arguments
        ------------
        parameters_values :: A tuple representing a (data-frame) row.
        sample_size :: int

        Result
        ------------
        A dataframe that repeats `parameters_values` `sample_size`
        number of times.
        """
        if not isinstance(parameters_values, tuple):
            parameters_values = tuple([parameters_values])

        assert len(parameters_values) == len(self.parameters_list)

        return pandas.DataFrame(
            sample_size * [dict(zip(self.parameters_list, parameters_values))])

    @lazyfield
    def summary(self):
        """
        A statistical summary of the data in this measurement.
        """
        return self\
            .dataframe\
            .groupby(self.parameters_list)\
            .agg(["size", "mean", "std"])

    @classmethod
    def SummaryType(cls):
        """
        A class that summarizes measurement of this Measurement's phenomenon.
        """
        return type(
            "{}SummaryMeasurement".format(
                cls.__name__\
                   .strip("Measurement")\
                   .strip("_measurement")),
            (SummaryMeasurement,),
            {"phenomenon": cls.phenomenon,
             "parameters": cls.parameters})

    @lazyfield
    def summary_measurement(self):
        """
        This `Measurement`, but with summary statistics, instead of all
        the samples.
        """
        type_summary_measurement = self.SummaryType()
        return type_summary_measurement(
            object_of_observation=self.object_of_observation,
            procedure=self.procedure,
            label=self.label,
            provenance=self.provenance,
            citation=self.citation,
            uri=self.uri,
            data=self.summary.reset_index())


class SummaryMeasurement(Measurement):
    """
    A statistical summary of sample measurements assumes sampling.
    """

    __metaclass_base__ = True

    def check_validity(self, data_value):
        """
        Check the validity of data in data_value.

        1. Check that all parameters are available in 'data_value'.
        ~  All Observations will have parameters, so we can check their
        ~  validity here.
        2. Check that all the observed variables are in 'data_value'.
        ~  By default, we assume that this Observation's phenomenon provides
        ~  the variable name that labels it's associated data in a dict
        ~  or a data-frame. However, if a statistical summary is provided as
        ~  data, we should expect 'mean' and 'error' as the observed variables. 

        Arguments
        ---------------
        data_value :: Either a list of dicts or a pandas dataframe
        """
        assert isinstance(data_value, pandas.DataFrame)
        assert isinstance(data_value.columns, pandas.MultiIndex)
        column_values_1 = {
            measurement_label
            for measurement_label, _ in data_value.columns.values}
        assert get_label(self.phenomenon) in  column_values_1
        column_values_2 = {
            summary_label
            for _, summary_label in data_value.columns.values}
        assert "mean" in column_values_2
        assert "std" in column_values_2


        try:
            super().check_validity(data_value)
        except MissingObservationParameter as error:
            raise error
        except MissingObservedVariable as error:
            try:
                self._check_variables(data_value, ["mean", "error"])
            except ValueError as error:
                raise MissingObservedVariable(*error.args)
            finally:
                pass
        finally:
            pass

        return True

    def samples(self, size=20):
        """
        Generate `<size>` samples for each combination of parameters in this
        `SummaryMeasurement`.
        """
        def sample(row):
            def __one():
                m = numpy.random.normal(
                    row[self.phenomenon.label]["mean"],
                    row[self.phenomenon.label]["std"])
                return m if m > 0 else __one()
            
            return numpy.array([__one() for _ in range(size)])

        return pandas\
            .concat([
                self._get_sample_parameters(index_values, size).assign(
                    **{self.phenomenon.label: sample(row)})
                for index_values, row in self.dataframe.iterrows()])\
            .set_index(self.parameters_list)

    @lazyfield
    def summary(self):
        """
        A statistical summary of the data in this measurement.
        """
        return self.dataframe


def summary_statistic(
        measurement_sample,
        parameter_columns=[],
        measurement_columns=[]):
    """
    Summarize a data-frame that contains observations on multiple samples.

    Type of the returned data-frame depends on the type of
    'measurement_columns'. Thus this method can accommodate more than one
    parameter columns in the measurement to be summarized, as well as it can
    summarize more than one measurement columns.
    """
    aggregators = ["size", "mean", "std"]
    if measurement_sample.shape[0] == 0:
        return pd.DataFrame([], columns=aggregators)
    if not parameter_columns:
        return\
            measurement_sample\
            .groupby(level=measurement_sample.index.names)\
            .agg(aggregators)
    summary=\
        measurement_sample\
        .groupby(parameter_columns)\
        .agg(aggregators)
    measurement_columns =\
        measurement_columns if measurement_columns\
        else summary.columns.levels[0]

    return\
        summary[measurement_columns[0]] if len(measurement_columns) == 1\
        else summary[measurement_columns]

def _check_sample_measurement(dataframe, variables):
    """
    Check that dataframe represents a sample measurement.
    """
    raise NotImplementedError

def _check_summary_measurement(dataframe, variables):
    """
    Check that dataframe represents a summary measurement.
    """
    raise NotImplementedError

def generate_samples(
        measurement_summary,
        measurement_variables,
        nsamples=20):
    """
    Create a dataframe corresponding to samples generated from a summary
    dataframe
    """
    pass


def Summary(MeasurementClass):
    """
    SummaryMeasurement subclass from measurement class.
    """
    return MeasurementClass.SummaryType()
