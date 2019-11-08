from collections.abc import Mapping, Iterable
from collections import OrderedDict
import itertools
import numpy
import pandas
from dmt.tk.field import Field, lazyfield
from dmt.tk.utils import get_label
from ...observation import Observation


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

    @staticmethod
    def load(dataframe):
        """
        Load a dataframe either as a `SampleMeasurement`
        or a `SummaryMeasurement`.
        """
        try:
            return SampleMeasurement.load(dataframe)
        except TypeError as sample_load_error:
            try:
                return SummaryMeasurement.load(dataframe)
            except TypeError as summary_load_error:
                raise TypeError(
                    "Unable to load dataframe: {}\n{}.".format(
                        sample_load_error,
                        summary_load_error))


class SampleMeasurement(Measurement):
    """
    Measurement that contains data on several
    samples for each combination of parameter values.
    """

    __metaclass_base__ = True

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
            data=self.summary().reset_index())

    @classmethod
    def check(cls, dataframe):
        """
        Check whether a dataframe is a sample measurement.
        """
        columns = [get_label(cls.phenomenon)] + [
            parameter for parameter in cls.parameters.keys()]
        return all(
            column in dataframe.columns
            for column in columns)

    @staticmethod
    def _read(dataframe):
        """
        Check dataframe to load as a `Measurement`.
        """
        columns = dataframe.columns
        if len(columns) != 1:
            raise TypeError(
                """
                To load as a `SampleMeasurement` a dataframe should have only
                one column. Received dataframe columns: {}
                """.format(columns))
        index = dataframe.index.names
        if len(index) and None in index:
            raise TypeError(
                """
                To load as a `SampleMeasurement` a dataframe should have
                properly named index. Received dataframe index: {}
                """.format(index))
        return (
            columns[0],
            OrderedDict([(parameter, parameter) for parameter in index]))
 
    @staticmethod
    def load(dataframe):
        """
        Load a dataframe.
        The dataframe is expected to be valid.
        """
        phenomenon, parameters = SampleMeasurement._read(dataframe)
        SampleMeasurementType = type(
            "{}By{}Samples".format(
                phenomenon,
                ''.join(format(p.capitalize() for p in parameters))),
            (SampleMeasurement, ),
            {"phenomenon": phenomenon,
             "parameters": parameters})
        return SampleMeasurementType(
            data=dataframe.reset_index(),
            label="ignore")

    def samples(self, number=20):
        """
        Get a dataframe containing samples for this measurement.
        """
        return self.summary_measurement.samples(number)


class SummaryMeasurement(Measurement):
    """
    A statistical summary of sample measurements assumes sampling.
    """

    __metaclass_base__ = True

    @classmethod
    def check_validity(cls, data_value):
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
        phenomenon =\
            get_label(cls.phenomenon)
        assert phenomenon in  column_values_1,\
            "Required column {} not found in {}".format(
                phenomenon, column_values_1)
        assert "mean" in data_value[phenomenon].columns.values
        assert "std" in data_value[phenomenon].columns.values

        super().check_validity(cls, data_value)

        return True

    @classmethod
    def check(cls, data_value):
        """
        Check, but not validate --- i.e. do not raise.
        """
        try:
            return cls.check_validity(data_value)
        except AssertionError:
            pass
        return False

    def _read(dataframe):
        """
        Check dataframe to load as a `Measurement`.
        """
        columns = dataframe.columns.values
        if len(columns) != 2:
            raise typeerror(
                """
                to load as a `summarymeasurement` a dataframe should have a
                multi-indexed two level column. received dataframe columns: {}
                """.format(columns))
        if not all(isinstance(c, tuple) for c in columns):
            raise typeerror(
                """
                to load as a `summarymeasurement` a dataframe should have a
                multi-indexed two level column containing two-tuples.
                received dataframe columns: {}
                """.format(columns))
        try:
            phenomenon, statistic = columns[0]
        except ValueError:
            raise TypeError(
                """
                To load as a `SummaryMeasurement` a dataframe should have a
                multi-indexed two level column containing two-tuples.
                Received dataframe columns: {}
                """.format(columns))
        try:
            phenomenon_2, statistic_2 = columns[1]
        except ValueError:
            raise TypeError(
                """
                To load as a `SummaryMeasurement` a dataframe should have a
                multi-indexed two level column containing two-tuples.
                Received dataframe columns: {}
                """.format(columns))

        if phenomenon_2 != phenomenon:
            raise TypeError(
                """
                To load as a `SummaryMeasurement` a dataframe should have a
                multi-indexed two level column containing two-tuples, with
                the same phenomenon names as the first element.
                Received dataframe columns: {}
                """.format(columns))

        if "mean" not in (statistic, statistic_2):
            raise TypeError(
                """
                To load as a `SummaryMeasurement` a dataframe should have a
                multi-indexed two level column containing two-tuples.
                One of the second levels should be "mean"
                Received dataframe columns: {}
                """.format(columns))
        if "std" not in (statistic, statistic_2):
            raise TypeError(
                """
                To load as a `SummaryMeasurement` a dataframe should have a
                multi-indexed two level column containing two-tuples.
                One of the second levels should be "std"
                Received dataframe columns: {}
                """.format(columns))

        index = dataframe.index.names
        if len(index) and None in index:
            raise TypeError(
                """
                To load as a `SampleMeasurement` a dataframe should have
                properly named index. Received dataframe index: {}
                """.formnat(index))
        return (
            columns[0][0],
            OrderedDict([(parameter, parameter) for parameter in index]))

    @staticmethod
    def load(dataframe):
        """
        Load a dataframe as a `SummaryMeasurement`.
        """
        if not isinstance(dataframe.columns, pandas.MultiIndex):
            raise TypeError(
                """
                To load as a `SummaryMeasurement` a dataframe should have a
                two-level columns. Received dataframe columns: {}
                """.format(dataframe.columns))
        phenomenon, parameters = SummaryMeasurement._read(dataframe)
        dataframe_phenomenon = dataframe[phenomenon]
        if "mean" not in dataframe_phenomenon.columns:
            raise TypeError(
                """
                To load as a `SummaryMeasurement` a dataframe should have
                "mean" as a column at the second level.
                """)
        if "std" not in dataframe_phenomenon.columns:
            raise TypeError(
                """
                To load as a `SummaryMeasurement` a dataframe should have
                "std" as a column at the second level.
                """)
        SummaryMeasurementType = type(
            "{}By{}Summary".format(
                phenomenon,
                ''.join(format(p.capitalize() for p in parameters))),
            (SummaryMeasurement, ),
            {"phenomenon": phenomenon,
             "parameters": parameters})
        return SummaryMeasurementType(
            data=dataframe.reset_index(),
            label="ignore")

    def summary(self):
        """
        A `pandas.DataFrame` representing a summary measurement.
        """
        return self.data

    def samples(self, size=20, _filter=lambda x: x):
        """
        Generate `<size>` samples for each combination of parameters in this
        `SummaryMeasurement`.
        """
        def _sample(row):
            """
            Create a sample from one row of the summary dataframe
            """
            def __one():
                phenomenon = get_label(self.phenomenon)
                return _filter(
                    numpy.random.normal(
                        row[phenomenon]["mean"],
                        row[phenomenon]["std"]))

            return numpy.array([__one() for _ in range(size)])

        return pandas\
            .concat([
                self._get_sample_parameters(index_values, size).assign(
                    **{get_label(self.phenomenon): _sample(row)})
                for index_values, row in self.dataframe.iterrows()])\
            .set_index(self.parameters_list)

    def SampleType(cls):
        """
        A class that provides samples for the measurement of this
        `Measurement`'s phenomenon.
        """
        return type(
            "{}SampleMeasurement".format(
                cls.__name__\
                   .strip("Measurement")\
                   .strip("_measurement")),
            (SampleMeasurement,),
            {"phenomenon": cls.phenomenon,
             "parameters": cls.parameters})

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
        return pandas.DataFrame([], columns=aggregators)
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

def _check_sample(dataframe, variables):
    """
    Check that dataframe represents a sample measurement.
    """
    raise NotImplementedError

def _check_summary(dataframe, variables):
    """
    Check that dataframe represents a summary measurement.
    """
    raise NotImplementedError

def get_samples(dataframe, number=20):
    """
    Create a dataframe corresponding to samples generated from a 
    dataframe.

    Arguments
    --------------
    dataframe: Either a dataframe containing samples, or a summary.
    """
    measurement = Measurement.load(dataframe)
    return dataframe\
        if isinstance(measurement, SampleMeasurement) else\
           measurement.samples(number)

def get_summary(dataframe):
    """
    Create a dataframe corresponding to a statistical summary measurement.

    Arguments
    --------------
    dataframe: Either a dataframe containing samples, or a summary.
    """
    measurement = Measurement.load(dataframe)
    return dataframe\
        if isinstance(measurement, SummaryMeasurement) else\
           measurement.summary()

def Summary(MeasurementClass):
    """
    SummaryMeasurement subclass from measurement class.
    """
    return MeasurementClass.SummaryType()

def concat(
        data,
        loader=lambda dataframe: dataframe,
        label_dataset="dataset"):
    """
    Concat dataframes passed in iterable data.
    Each dataframe in data must be case as the required type.

    Arguments
    ---------------
    data :: A Mapping name_dataset -> dataframe
    The dataframes may have an indexThe dataframes may have an index

    Returns
    ---------------
    A single dataframe --- with a default index (integers...)
    If all the dataframes in `data` have the same index names,
    the returned dataframe will have the 
    """
    indices_names = {
        tuple(dataframe.index.names)
        for _, dataframe in data.items()}
    if isinstance(data, Mapping):
        combined_dataframe = pandas.concat([
            loader(dataframe).reset_index().assign(**{label_dataset: dataset})
            for dataset, dataframe in data.items()])
        return\
            combined_dataframe.set_index(
                [label_dataset,] + list(indices_names.pop()))\
            if len(indices_names) == 1 else\
               combined_dataframe
    if isinstance(data, Iterable) and not isinstance(data, str):
        return pandas.concat([
            loader(dataframe) for dataframe in data])
    return loader(data)

def concat_as_samples(data, nsamples=20):
    """
    Concat as sample measurements.
    """
    return concat(data, loader=lambda d: get_samples(d, number=nsamples))

def concat_as_summaries(data):
    """
    Concat as summary dataframes.
    """
    return concat(data, loader=get_summary)


