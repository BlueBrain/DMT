"""
An `Analysis` structured with components.
"""

import os
import pandas as pd
from collections.abc import Mapping, Iterable
from collections import OrderedDict, namedtuple
from tqdm import tqdm
import warnings
from dmt.tk.journal import Logger
from dmt.data.observation.measurement.collection\
    import primitive_type as primitive_type_measurement_collection
from dmt.analysis import Analysis
from dmt.model.interface import InterfaceMeta
from dmt.tk.field import Field, LambdaField, lazyfield, WithFields
from dmt.tk.author import Author
from dmt.tk.parameters import Parameters
from dmt.tk.stats import Statistics
from dmt.tk.plotting import Plotter
from dmt.tk.reporting import Report, Reporter
from dmt.tk.utils.string_utils import paragraphs
from dmt.tk.collections.dataframes import make_dataframe_hashable
from dmt.tk import terminology


def nothing(*args, **kwargs):
    return None

def always_pass(*args, **kwargs):
    return True

NP = "Not-Provided"

LOGGER = Logger(client=__file__)

class StructuredAnalysis(Analysis):
    """
    An analysis structured as individual components that each handle an
    independent responsibility.
    """
    author = Field(
        """
        An object describing the author.
        """,
        __default_value__=Author.anonymous)
    AdapterInterface = Field(
        """
        An class written as a subclass of `InterfaceMeta` that declares and
        documents the methods required of the adapter by this analysis.
        """,
        __type__=InterfaceMeta)
    abstract = LambdaField(
        """
        A short description of this analysis.
        """,
        lambda self: self.phenomenon.description)
    introduction = Field(
        """
        A scientific introduction to this analysis.
        """,
        __default_value__="Not provided.")
    methods = Field(
        """
        A description of the algorithm / procedure used to compute the results,
        and the experimental measurement reported in this analysis.
        """)
    sampling_methodology = Field(
        """
        A tag indicating whether this analysis will make measurements on
        random samples drawn from a relevant population of circuit constituents,
        or on the entire population. The circuit constituents population to be
        measured will be determined by a query.
        """,
        __default_value__="Not Provided")
    sample_size = Field(
        """
        Number of samples to measure for each set of the measurement parameters.
        This field will be relevant when the measurements are made on random
        samples. When the measurement is exhaustive, the whole population of
        (relevant) circuit constituents will be measured.
        """,
        __default_value__=20)
    sample_measurement = Field(
        """
        A callable that maps
        `(adapter, model, **parameters, **customizations) ==> measurement`
        where
        parameters : paramters for the measurements
        customizations : that specify the method used to make a measurement

        This field may also be implemented as a method in a subclass.
        """,
        __required__=False)
    measurement_parameters = Field(
        """
        An object providing a collection of parameters to measure with.
        This object may be of  type:
        1. either `pandas.DataFrame`,
        2. or `adapter, model -> Collection<MeasurementParameters>`,
        3. or dmt.tk.Parameters.
        """,
        __as__=Parameters,
        __default_value__=nothing)
    measurement_collection = Field(
        """
        A callable that will collect measurements passed as an iterable.
        The default value assumes that the each measurement will return an
        elemental value such as integer, or floating point number.
        """,
        __default_value__=primitive_type_measurement_collection)
    plotter = Field(
        """
        A class instance or a module that has `plot` method that will be used to
        plot the results of this analysis. The plotter should know how to 
        interpret the data provided. For example, the plotter will have to know
        which columns are the x-axis, and which the y-axis. The `Plotter`
        instance used by this `BrainCircuitAnalysis` instance should have those
        set as instance attributes.
        """,
        __as__=Plotter,
        __required__=False)
    stats = Field(
        """
        An object that provides a statistical summary for the measurements
        made in this analysis. This object may be just a function that takes
        this analysis' measurements as an argument.
        """,
        __as__=Statistics,
        __default_value__=nothing)
    verdict = Field(
        """
        An object that provies a verdict on the measurements made in this
        analysis. This object may be just a function that takes this analysis'
        measurements as an argument.
        """,
        __default_value__=always_pass)
    results = Field(
        """
        A callable on relevant parameters that will return results for a
        run of this analysis.
        """,
        __default_value__=lambda *args, **kwargs: """
        Results are presented in the figure.
        """)
    reference_data = Field(
        """
        A pandas.DataFrame containing reference data to compare with the
        measurement made on a circuit model.
        Each dataset in the dataframe must be annotated with index level
        'dataset', in addition to levels that make sense for the measurements.
        """,
        __default_value__={})
    report = Field(
        """
        A callable that will generate a report. The callable should be able to
        take arguments listed in `get_report(...)` method defined below.
        """,
        __default_value__=Report)
    reporter = Field(
        """
        A class or a module that will report the results of this analysis.
        It is up to the reporter what kind of report to generate. For example,
        the report can be a (interactive) webpage, or a static PDF.
        """,
        __required__=False,
        __examples__=[
            Reporter(path_output_folder=os.getcwd())])
    
    Measurement = namedtuple("Measurement", ["method", "dataset", "data"])

    # TODO: The methods below are from HD's alpha StructuredAnalysis
    #       This must be refactored...
    # TODO: this probably should not be public....
    def adapter_method(self):
        """
        get the measuremet marked on the AdapterInterface
        """
        measurement_name = self.AdapterInterface.__measurement__
        try:
            return getattr(self.adapter, measurement_name)
        except AttributeError:
            return getattr(self.adapter, "get_{}".format(measurement_name))

    @lazyfield
    def label(self):
        """
        A label for this analysis.
        """
        return "{}_by_{}".format(
            self.phenomenon.label,
            '_'.join(self.names_measurement_parameters))

    # TODO: parallelize model measuring?
    def get_model_measurements(self, adapter, model, sample_size=None):
        """
        Get a statistical measurement.
        """
        assert not sample_size or isinstance(sample_size, int),\
            "Expected int, received {}".format(type(sample_size))
        try:
            method = self.measurement_method
        except AttributeError:
            method = self.adapter_method()
        parameters = self._parameters.for_sampling(
            adapter, model, size=self.samples_per_measurement)
        # TODO: test parameter order is preserved
        measurements = make_dataframe_hashable(
            pd.DataFrame(parameters).assign(
                **{self.phenomenon:
                   [method(adapter, model, **p)
                    for p in tqdm(parameters)]}))
        return measurements

    @property
    def number_measurement_parameters(self):
        """
        How many parameters are the measurements made with?
        For example, if the measurement parameters are region, layer,
        the number is two.

        The implementation below uses the implementation of
        `self.measurement_parameters`. However, if you change the type of that
        component, you will have to override However, if you change the type of that
        component, you will have to override.
        """
        return self._parameters.values.shape[1]

    @property
    def names_measurement_parameters(self):
        """
        What are the names of the parameters that the measurements are made with?

        If measurement parameters cannot provide the variables (a.k.a parameter
        labels or tags), an empty list is returned.
        """
        try:
            return self._parameters.variables
        except TypeError:
            return []
        return None

    @property
    def phenomenon(self):
        try:
            return self.measurement_method.phenomenon
        except AttributeError:
            try:
                return self.AdapterInterface.phenomenon
            except AttributeError:
                return NOT_PROVIDED

    @property
    def _parameters(self):
        if self.measurement_parameters is not NOT_PROVIDED:
            return Parameters(self.measurement_parameters)
        elif self.reference_data is not NOT_PROVIDED:
            return Parameters(self.reference_data.drop(
                columns=[self.phenomenon]))
        else:
            raise ValueError(
                """
                {} has neither measurement_parameters nor reference_data
                provide one or the other
                """.format(self))

    def with_fields(self, **kwargs):
        for field in self.get_fields():
            if field not in kwargs:
                try:
                    kwargs[field] = getattr(self, field)
                except AttributeError:
                    pass
        return self.__class__(**kwargs)

    def validation(self, circuit_model, adapter=None, *args, **kwargs):
        """
        Validation of a model against reference data.
        """
        assert not self.reference_data.empty,\
            "Validation needs reference data."
        if adapter is None:
            return self((adapter, circuit_model))
        else:
            return self(circuit_model)

    def _get_report(self, measurements):
        try:
            fig = self.plotter(measurements, phenomenon=self.phenomenon)
        except Exception as e:
            import traceback
            fig = """"
            Plotting failed:
            {},
            {}
            returning raw measurments""".format(e, traceback.format_exc())
            warnings.warn(Warning(fig))

        try:
            len(fig)
        except TypeError:
            fig = [fig]
        # TODO: until field is fixed, this will raise for empty docstrings
        # TEMPORARY workaround:
        if self.measurement_method.__doc__ is None:
            self.measurement_method.__doc__ = ''
        report = Report(
            figures=fig,
            measurement=measurements,
            phenomenon=self.phenomenon,
            methods=self.measurement_method.__doc__)
        report.stats = self.stats(report)
        report.verdict = self.verdict(report)
        return report

    def __call__(self,
                 *models):
        """
        perform an analysis of 'models'

        """
        measurements = OrderedDict()
        if self.reference_data is not NOT_PROVIDED:
            measurements[
                _label(self.reference_data, default='reference_data')] =\
                    make_dataframe_hashable(self.reference_data)

        for i, model in enumerate(models):

            if isinstance(model, tuple):
                adapter, model = model
            else:
                adapter = self.default_adapter

            measurements[_label(model, default='model', i=i)] =\
                self.get_model_measurements(adapter, model)

        report = self._get_report(measurements)

        if self.reporter is not NOT_PROVIDED:
            self.reporter.post(report)

        return report


def _label(obj, default, i=''):
    """
    get the label for obj if it has one, otherwise get default
    of default + str(i)
    """
    try:
        if isinstance(obj.label, str):
            return obj.label
        # TODO: support iterable, getting first elem?
        #       would make things really easy for dataframes
        #       with a 'label' column
        raise ValueError("label must be str, recieved: {}"
                         .format(obj.label))
    except AttributeError:
        return default + str(i)
