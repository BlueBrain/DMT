"""
Brain circuit analyses and validations.
"""

import os
from tqdm import tqdm
from dmt.tk.journal import Logger
from dmt.data.observation.measurement.collection\
    import primitive_type as primitive_type_measurement_collection
from dmt import analysis
from dmt.model.interface import InterfaceMeta
from dmt.tk.field import Field, LambdaField, lazyfield
from dmt.tk.author import Author
from dmt.tk.utils.string_utils import paragraphs
from neuro_dmt import terminology
from neuro_dmt.analysis.reporting import\
    CircuitAnalysisReport

LOGGER = Logger(client=__file__, level="DEBUG")


class StructuredAnalysis(
        analysis.StructuredAnalysis):
    """
    A base class for all circuit analyses.
    """
    figures = LambdaField(
        """
        An alias for `Field plotter`, which will be deprecated.
        A class instance or a module that has `plot` method that will be used to
        plot the results of this analysis. The plotter should know how to 
        interpret the data provided. For example, the plotter will have to know
        which columns are the x-axis, and which the y-axis. The `Plotter`
        instance used by this `BrainCircuitAnalysis` instance should have those
        set as instance attributes.
        """,
        lambda self: self.plotter)
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
                try:
                    return\
                        self.sample_measurement(
                            circuit_model, adapter, **kwargs)
                except (TypeError, AttributeError) as error_model_adapter:
                    try:
                        return\
                            self.sample_measurement(
                                adapter, circuit_model, **kwargs)
                    except Exception as error_adapter_model:
                        raise TypeError(
                            """
                            sample_measurement(...) failed with arguments
                            (model, adapter) and (adapter, model):
                            \t {}
                            \t {}
                            """.format(
                                error_model_adapter,
                                error_adapter_model))

            try:
                _adapter_measurement_method.__method__ =\
                    paragraphs(
                        self.sample_measurement.__method__)
            except AttributeError:
                _adapter_measurement_method.__method__ =\
                    "Not provided in the sample measurement method."

            return\
                _adapter_measurement_method
        else:
            return\
                self._get_adapter_measurement_method(adapter)

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
            self.measurement_parameters(
                    adapter,
                    circuit_model,
                    sample_size=self.sample_size if using_random_samples else 1)
        get_measurement =\
            self._get_measurement_method(adapter)
        measured_values = self\
            .measurement_collection(
                (p, get_measurement(circuit_model,
                                    sampling_methodology=self.sampling_methodology,
                                    **p, **kwargs))
                for p in tqdm(parameter_values))\
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

        return {
            "data": measurement,
            "method": method}

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

        def _get_data(dataset):
            try:
                return dataset.data
            except AttributeError:
                return dataset

        measurement_dict.update({
            label: _get_data(dataset)
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
        try:
            return self.measurement_parameters.number
        except:
            return np.nan

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
        return self.figures(data, caption=caption)

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
        try:
            reference_citations ={
                label: reference.citation
                for label, reference in reference_data.items()}
        except AttributeError:
            LOGGER.info(
                """
                Could not retrieve citations from reference data of type {}.
                """.format(
                    type(reference_data)))

            reference_citations = {}

        return self.report(
            author=author,
            phenomenon=self.phenomenon.label,
            abstract=self.abstract,
            introduction=self.introduction(provenance_circuit)["content"],
            methods=self.methods(provenance_circuit)["content"],
            measurement=measurement,
            figures=figures,
            results=self.results(provenance_circuit)["content"],
            discussion=self.discussion(provenance_circuit)["content"],
            conclusion=self.conclusion(provenance_circuit)["content"],
            references=reference_citations,
            provenance_model=provenance_circuit)

    def _resolve_adapter(self, adapter=None):
        """
        Resolve which adapter to use.
        """
        return adapter if adapter else self.adapter

    def __call__(self,
            model,
            adapter=None,
            author=Author.anonymous,
            **kwargs):
        """
        Make this `Analysis` masquerade as a function.

        """
        measurement =\
            self.get_measurement(
                model,
                adapter=adapter,
                **kwargs)
        reference_data =\
            kwargs.pop(
                "reference_data",
                self.reference_data)
        provenance_circuit =\
            adapter.get_provenance(model)
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
                provenance_circuit=provenance_circuit)

        try:
            return self.reporter.post(report)
        except AttributeError:
            return report


BrainCircuitAnalysis = StructuredAnalysis
