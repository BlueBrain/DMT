"""
Brain circuit analyses and validations.
"""

from abc import abstractmethod
import os
import pandas        
from dmt.data.observation.measurement.collection\
    import primitive_type as primitive_type_measurement_collection
from dmt.analysis import Analysis
from dmt.model.interface import InterfaceMeta
from dmt.data.observation.measurement.collection import\
    primitive_type as primitive_type_measurement_collection
from dmt.tk.field import Field, LambdaField, lazyfield
from dmt.tk.author import Author
from dmt.tk.parameters import Parameters
from dmt.tk.reporting import Report, Reporter
from dmt.tk.utils.args import require_only_one_of
from neuro_dmt import terminology
from neuro_dmt.analysis.reporting import CircuitAnalysisReport

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
    abstract = LambdaField(
        """
        A short description of the analysis.
        """,
        lambda self: self.phenomenon.description)
    introduction = Field(
        """
        A scientific introduction to this analysis, that will be used to
        produce a report. 
        """,
        __default_value__="Not provided.")
    methods = Field(
        """
        Describe the algorithm / procedure used to computer the results or
        the experimental measurement presented in this analysis.
        """,
        __default_value__="Not provided.")
    AdapterInterface  = Field(
        """
        The interface that will be used to get measurements for the circuit
        model to analyze.
        """,
        __type__=InterfaceMeta)
    sample_measurement = Field(
        """
        A callable that maps
        (adapter, model, **parameters, **customizations) ==> measurement.
        where
        parameters : parameters for the measurement
        customizations : that specify the method used to make a measurement.
        """,
        __required__=False)
    measurement_parameters = Field(
        """
        A collection of parameters to measure with.
        This object should have the following methods:
        ~   1. `for_sampling`, returning an iterable of dict like parameters
        ~       to pass to a measurement method as keyword arguments.
        ~   2. `index`, returning a pandas.Index object to be used as an
        ~       index on the measurement.
        """,
        __as__=Parameters,
        __required__=False)
    measurement_collection = Field(
        """
        A callable that will collect measurements passed as an iterable.
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
        __required__=False)
    report = Field(
        """
        A callable that will generate a report. The callable should be able to
        take arguments listed in `get_report(...)` method defined below.
        """,
        __default_value__=CircuitAnalysisReport)
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
        def _as_label(parameter_label):
            if isinstance(parameter_label, str):
                return parameter_label
            if isinstance(parameter_label, tuple):
                return '_'.join(parameter_label)
            raise TypeError(
                "Parameter labels should be either string or tuple of strings.")

        return "{}_by_{}".format(
            self.phenomenon.label,
            '_'.join(
                _as_label(parameter_label) 
                for parameter_label in self.names_measurement_parameters))

    def _get_adapter_measurement_method(self, adapter):
        """..."""
        measurement_name =\
            self.AdapterInterface.__measurement__
        assert measurement_name[0] != '_'
        assert measurement_name[0:4] != "get"
        try:
            return\
                getattr(adapter, measurement_name)
        except AttributeError as error:
            try:
                return\
                    getattr(adapter, "get_{}".format(measurement_name))
            except AttributeError as error_get:
                raise AttributeError(
                    """
                    No adapter attribute (w/o prefix `get_`)to measure {}:
                    \t{}
                    \t{}.
                    """.format(
                        measurement_name,
                        error,
                        error_get))
            raise RuntimeError(
                "Unreachable point in code.")
        raise RuntimeError(
            "Unreachable point in code.")

    def _get_measurement_method(self, adapter=None):
        """
        Makes sense for analysis of a single phenomenon.

        Some changes below provide backward compatibility.
        """
        adapter = self._resolve_adapter(adapter)
        if hasattr(self, "sample_measurement"):
            def _adapter_measurement_method(
                    circuit_model,
                    **kwargs):
                """
                Make sample measurement method behave as if it was defined on
                the adapter.

                Arguments
                ===============
                kwargs :  keyword arguments containing keywords providing the
                parameter set to make the measurement, as well other arguments
                that may affect how the measurement will be made (for example,
                deterministic or stochastic, or the number of samples to
                measure for a single set of parameters.)
                """
                return\
                    self.sample_measurement(
                        circuit_model, adapter, **kwargs)

            try:
                _adapter_measurement_method.__method__ =\
                    self.sample_measurement.__method__
            except AttributeError:
                _adapter_measurement_method.__method__ =\
                    "Not provided in the sample measurement method."

            return _adapter_measurement_method
        else:
            return self._get_adapter_measurement_method(adapter)

        raise RuntimeError(
            "Unreachable point in code.")

    def get_measurement(self,
            circuit_model,
            adapter=None,
            sampling_methodology=terminology.sampling_methodology.random,
            sample_size=20,
            *args, **kwargs):
        """
        Get a statistical measurement.
        """
        assert not sample_size or isinstance(sample_size, int),\
            "Expected int, received {}".format(type(sample_size))
        adapter =\
            self._resolve_adapter(adapter)
        using_random_samples=\
            sampling_methodology == terminology.sampling_methodology.random
        parameter_values =\
            self.measurement_parameters\
                .for_sampling(
                    adapter,
                    circuit_model,
                    size=sample_size if using_random_samples else 1)
        get_measurement =\
            self._get_measurement_method(adapter)
        measured_values = self\
            .measurement_collection(
                (p, get_measurement(circuit_model,
                                    sampling_methodology=sampling_methodology,
                                    **p, **kwargs))
                for p in parameter_values)\
            .rename(columns={"value": self.phenomenon.label})
        measurement =\
              measured_values.reset_index()\
                             .assign(
                                 dataset=adapter.get_label(circuit_model))\
                             .set_index(
                                 ["dataset"] + measured_values.index.names)
        try:
            method = get_measurement.__method__
        except AttributeError:
            method = "Measurement method description not provided."

        return dict(
            data=measurement,
            method=method)

    def _with_reference_data(self,
            measurement,
            reference_data={}):
        """
        Append reference datasets.

        Arguments
        ===========
        reference_data :: dict mapping dataset label to an object with
        attributes <data :: DataFrame, citation :: String>
        """
        reference_data =\
            reference_data\
            if len(reference_data)  else\
               self.reference_data
        measurement_dict = {
            dataset: measurement.xs(dataset, level="dataset")
            for dataset in measurement.reset_index().dataset.unique()}
        measurement_dict.update({
            label: dataset.data
            for label, dataset in reference_data.items()})
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
        try:
            return self.plotter.get_figures(data, caption=caption)
        except AttributeError:
            return {
                "figure": self.plotter.get_figure(data, caption=caption)}
        raise RuntimeError(
            """
            Execution of `get_figures(...)` should not reach here.
            """)

    def get_report(self,
            measurement,
            author=Author.anonymous,
            figures=None,
            reference_data=None,
            **provenance_circuit):
        """
        Get a report for the given `measurement`.
        """
        reference_data =\
            reference_data if reference_data is not None\
            else self.reference_data

        provenance_circuit["authors_circuit"] =\
            provenance_circuit.pop("authors", ["Not Available"])
        return self.report(
            author=author,
            phenomenon=self.phenomenon.label,
            abstract=self.abstract,
            introduction=self.introduction.format(**provenance_circuit),
            methods=self.methods,
            measurement=measurement,
            figures=figures,
            results="Results are presented in the figure.",
            discussion="To be provided after a review of the results",
            references={
                label: reference.citation
                for label, reference in self.reference_data.items()},
            **provenance_circuit)

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
            *args,
            sampling_methodology=terminology.sampling_methodology.random,
            author=Author.anonymous,
            **kwargs):
        """
        Make this `Analysis` masquerade as a function.

        """
        adapter, circuit_model = self._resolve_adapter_and_model(*args)
        measurement =\
            self.get_measurement(
                circuit_model,
                adapter=adapter,
                sampling_methodology=sampling_methodology,
                **kwargs)
        reference_data =\
            kwargs.get(
                "reference_data",
                self.reference_data)
        report =\
            self.get_report(
                measurement["data"],
                author=author,
                figures=self.get_figures(
                    data=self._with_reference_data(
                        measurement["data"],
                        reference_data),
                    caption=measurement["method"]),
                reference_data=reference_data,
                **adapter.get_provenance(circuit_model))

        try:
            return self.reporter.post(report)
        except AttributeError:
            return report
