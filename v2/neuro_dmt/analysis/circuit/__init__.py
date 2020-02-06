"""
Brain circuit analyses and validations.
"""

import os
from dmt.tk.journal import Logger
from dmt.data.observation.measurement.collection\
    import primitive_type as primitive_type_measurement_collection
from dmt.analysis.structured import StructuredAnalysis
from dmt.model.interface import InterfaceMeta
from dmt.tk.field import Field, LambdaField, lazyfield
from dmt.tk.author import Author
from dmt.tk.parameters import Parameters
from dmt.tk.reporting import Reporter
from dmt.tk.utils.string_utils import paragraphs
from neuro_dmt import terminology
from neuro_dmt.analysis.reporting import\
    CircuitAnalysisReport,\
    CircuitProvenance

LOGGER = Logger(client=__file__, level="DEBUG")

class BrainCircuitAnalysis(
        StructuredAnalysis):
    """
    A base class for all circuit analyses.
    """
    phenomenon = Field(
        """
        An object providing the phenomenon analyzed.
        """)

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
                    paragraphs(
                        self.sample_measurement.__method__)
            except AttributeError:
                _adapter_measurement_method.__method__ =\
                    "Not provided in the sample measurement method."

            return _adapter_measurement_method
        else:
            return\
                paragraphs(
                    self._get_adapter_measurement_method(adapter))

        raise RuntimeError(
            "Unreachable point in code.")

    def get_measurement(self,
            circuit_model,
            adapter=None,
            *args, **kwargs):
        """
        Get a statistical measurement.
        """
        adapter =\
            self._resolve_adapter(adapter)
        using_random_samples=\
            self.sampling_methodology == terminology.sampling_methodology.random
        parameter_values =\
            self.measurement_parameters\
                .for_sampling(
                    adapter,
                    circuit_model,
                    size=self.sample_size if using_random_samples else 1)
        get_measurement =\
            self._get_measurement_method(adapter)
        measured_values = self\
            .measurement_collection(
                (p, get_measurement(circuit_model,
                                    sampling_methodology=self.sampling_methodology,
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
            provenance_circuit={}):
        """
        Get a report for the given `measurement`.
        """
        reference_data =\
            reference_data if reference_data is not None\
            else self.reference_data

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
                for label, reference in reference_data.items()},
            provenance_model=provenance_circuit)

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
                **kwargs)
        reference_data =\
            kwargs.pop(
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
                provenance_circuit=adapter.get_provenance(circuit_model))

        try:
            return self.reporter.post(report)
        except AttributeError:
            return report
