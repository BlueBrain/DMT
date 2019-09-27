"""
Brain circuit analyses and validations.
"""

from abc import abstractmethod
import os
import pandas        
from dmt.analysis import Analysis
from dmt.model.interface import InterfaceMeta
from dmt.tk.field import Field, lazyproperty
from dmt.tk.reporting import Report, Reporter
from dmt.tk.utils.args import require_only_one_of

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
        __default_value__=pandas.DataFrame())

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
            sample_size=None):
        """
        Get a statistical measurement.
        """
        assert not sample_size or isinstance(sample_size, int),\
            "Expected int, received {}".format(type(sample_size))
        adapter = self._resolve_adapter(adapter)
        return pandas\
            .DataFrame(
                [self._get_measurement_method(adapter)(circuit_model, **p)
                 for p in self.measurement_parameters.for_sampling(sample_size)],
                columns=[self.phenomenon.label],
                index=self.measurement_parameters.index(sample_size))\
            .reset_index()\
            .assign(
                dataset=adapter.get_label(circuit_model))\
            .set_index(
                ["dataset"] + self.measurement_parameters.variables)

    def _with_reference_data(self,
            measurement,
            reference_data=pandas.DataFrame()):
        """
        Append reference datasets.
        """
        reference_data =\
            reference_data\
            if reference_data.empty  else\
               self.reference_data
        return\
            measurement\
            if reference_data.empty else\
               pandas.concat([measurement, reference_data])

    def _append_reference_data(self,
                measurement):
        """
        """
        if self.reference_data.empty:
            return measurement
        return pandas.concat([
            measurement\
            .reset_index()\
            .assign(
                dataset=self.adapter.get_label())])

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

        The implementation below uses the implementation of
        `self.measurement_parameters`. However, if you change the type of that
        component, you will have to override However, if you change the type of that
        component, you will have to override.
        """
        return list(self.measurement_parameters.values.columns.values)

    def get_figures(self,
            measurement=None,
            caption=None):
        """
        Get a figure for the analysis of `circuit_model`.

        Arguments
        ----------
        `measurement`: The data frame to make a figure for.
        """
        return {
            self.phenomenon.label: self.plotter.get_figure(
                measurement.reset_index(),
                caption=caption)}

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
                reference,
                adapter_reference,
                *args, **kwargs)
        measurement_reference =\
            self.get_measurement(
                alternative,
                adapter_alternative,
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
                sample_size=kwargs.get("sample_size", None))
        measurement_method = self._get_measurement_method(adapter).__doc__
        report =\
            self.get_report(
                self._with_reference_data(
                    measurement),
                method_measurement=measurement_method,
                figures=self.get_figures(
                    measurement=measurement,
                    caption=measurement_method),
                reference_data=kwargs.get("reference_data", pandas.DataFrame()))

        try:
            return self.reporter.post(report)
        except AttributeError:
            return report
