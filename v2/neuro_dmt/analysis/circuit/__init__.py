"""
Brain circuit analyses and validations.
"""

from abc import abstractmethod
import os
import pandas        
from dmt.analysis import Analysis
from dmt.model.interface import InterfaceMeta
from dmt.tk.field import Field, lazyfield
from dmt.tk.reporting import Report, Reporter
from dmt.tk.utils.args import require_only_one_of
from neuro_dmt import terminology

class BrainCircuitAnalysis(
        Analysis):
    """
    A base class for all circuit analyses.
    """
    phenomenon = Field(
        """
        An object whose `.label` is a single word name for the phenomenon 
        analyzed by this `BrainCircuitAnalysis`.
        """)
    AdapterInterface  = Field(
        """
        The interface that will be used to get measurements for the circuit
        model to analyze.
        """,
        __type__=InterfaceMeta)
    measurement_parameters = Field(
        """
        A collection of parameters to measure with.
        This object should have the following methods:
        ~   1. `for_sampling`, returning an iterable of dict like parameters
        ~       to pass to a measurement method as keyword arguments.
        ~   2. `index`, returning a pandas.Index object to be used as an
        ~       index on the measurement.
        """)
    plotter = Field(
        """
        A class or a module that has `plot` method that will be used to
        plot the results of this analysis. The plotter should know how to 
        interpret the data provided. For example, the plotter will have to know
        which columns are the x-axis, and which the y-axis. The `Plotter`
        instance used by this `BrainCircuitAnalysis` instance should have those
        set as instance attributes.
        """,
        __required__=False)
    reporter = Field(
        """
        A class or a module that will report the results of this analysis.
        It is up to the reporter what kind of report to generate. For example,
        the report can be a (interactive) webpage, or a static PDF.
        """,
        __required__=False,
        __examples__=[
            Reporter(path_output_folder=os.getcwd())])
    reference_data = Field(
        """
        A pandas.DataFrame containing reference data to compare with the
        measurement made on a circuit model.
        Each dataset in the dataframe must be annotated with index level
        'dataset', in addition to levels that make sense for the measurements.
        """,
        __default_value__={})

    @property
    def _has_reference_data(self):
        """..."""
        return len(self.reference_data) > 0

    @lazyfield
    def label(self):
        """
        A label for this analysis.
        """
        return "{}_by_{}".format(
            self.phenomenon.label,
            '_'.join(self.names_measurement_parameters))

    def _get_measurement_method(self, adapter=None):
        """
        Makes sense for analysis of a single phenomenon.
        """
        adapter = self._resolve_adapter(adapter)
        measurement_name =\
            self.AdapterInterface.__measurement__
        try:
            return getattr(adapter, measurement_name)
        except AttributeError:
            return getattr(adapter, "get_{}".format(measurement_name))
        raise AttributeError(
            "No adapter attribute to measure {}".format(measurement_name))

    def get_measurement(self,
            circuit_model,
            adapter=None,
            sample_size=None,
            *args, **kwargs):
        """
        Get a statistical measurement.
        """
        assert not sample_size or isinstance(sample_size, int),\
            "Expected int, received {}".format(type(sample_size))
        adapter =\
            self._resolve_adapter(adapter)
        parameter_values =\
            self.measurement_parameters\
                .for_sampling(
                    adapter,
                    circuit_model,
                    size=sample_size)
        get_measurement =\
            self._get_measurement_method(adapter)
        measured_values = pandas\
            .DataFrame(
                [get_measurement(circuit_model, **p, **kwargs)
                 for p in parameter_values],
                columns=[self.phenomenon.label])
        return pandas\
            .concat(
                [self.measurement_parameters.as_dataframe(parameter_values),
                 measured_values],
                axis=1)\
            .assign(
                dataset=adapter.get_label(circuit_model))\
            .set_index(
                ["dataset"] + self.names_measurement_parameters)

    def _with_reference_data(self,
            measurement,
            reference_data={}):
        """
        Append reference datasets.
        """
        reference_data =\
            reference_data\
            if len(reference_data)  else\
               self.reference_data
        measurement_dict = {
            dataset: measurement.xs(dataset, level="dataset")
            for dataset in measurement.reset_index().dataset.unique()}
        measurement_dict.update(reference_data)
        return measurement_dict

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
        return self.measurement_parameters.values.shape[1]

    @property
    def names_measurement_parameters(self):
        """
        What are the names of the parameters that the measurements are made with?

        If measurement parameters cannot provide the variables (a.k.a parameter
        labels or tags), an empty list is returned.
        """
        try:
            return self.measurement_parameters.variables
        except TypeError:
            return []
        return None

    def get_figures(self,
            data,
            caption=None):
        """
        Get a figure for the analysis of `circuit_model`.

        Arguments
        ----------
        `figure_data`: The data frame to make a figure for.
        """
        return {
            self.label: self.plotter.get_figure(data, caption=caption)}

    def get_report(self,
            measurement,
            method_measurement="Not available.",
            figures=None,
            reference_data=None):
        """
        Get a report for the given `measurement`.
        """
        return Report(
            phenomenon=self.phenomenon.label,
            measurement=measurement,
            figures=figures,
            introduction="{}, measured by layer\n{}.".format(
                self.phenomenon.name,
                self.phenomenon.description),
            methods=method_measurement,
            results="Results are presented in the figure.",
            discussion="To be provided after a review of the results")

    def _resolve_adapter_and_model(self,  *args):
        """
        Resolve adapter and model.
        """
        a = len(args)

        if a == 2:
            return (args[1], args[0])

        if a == 1:
            try: 
                return (self.adapter, args[0])
            except AttributeError as error:
                raise TypeError(
                    """
                    With only 1 argument, _resolve_adapter_and_model() assumes
                    that the adapter is defined:
                    {}
                    """.format(error))
        raise TypeError(
            """
            _resolve_adapter_and_model() takes 1 or 2 positional arguments,
            but {} were given.
            """.format(a))

    def _resolve_adapter(self, adapter=None):
        """
        Resolve which adapter to use.
        """
        return adapter if adapter else self.adapter

    def comparison(self,
            alternative,
            reference,
            adapter_alternative=None,
            adapter_reference=None,
            *args, **kwargs):
        """
        Compare an alternative model to a reference model.
        """
        measurement_alternative =\
            self.get_measurement(
                alternative,
                adapter_alternative,
                *args, **kwargs)
        measurement_reference =\
            self.get_measurement(
                reference,
                adapter_reference,
                *args, **kwargs)
        report =\
            self.get_report(
                self._with_reference_data(
                    measurement_alternative,
                    measurement_reference),
                *args, **kwargs)
        try:
            return self.reporter.post(report)
        except AttributeError:
            return report

    def validation(self,
            circuit_model,
            adapter=None,
            *args, **kwargs):
        """
        Validation of a model against reference data.
        """
        assert not self.reference_data.empty,\
            "Validation needs reference data."
        return\
            self.__call__(
                circuit_model,
                adapter,
                *args, **kwargs)

    def __call__(self,
            *args, **kwargs):
        """
        Make this `Analysis` masquerade as a function.

        """
        adapter, circuit_model = self._resolve_adapter_and_model(*args)
        measurement =\
            self.get_measurement(
                circuit_model,
                adapter=adapter,
                sampling_procedure=kwargs.get(
                    "sampling_procedure",
                    terminology.measurement_method.random_sampling))
        measurement_method =\
            self._get_measurement_method(adapter).__doc__
        report =\
            self.get_report(
                measurement,
                method_measurement=measurement_method,
                figures=self.get_figures(
                    data=self._with_reference_data(measurement),
                    caption=measurement_method),
                reference_data=kwargs.get("reference_data", pandas.DataFrame()))

        try:
            return self.reporter.post(report)
        except AttributeError:
            return report
