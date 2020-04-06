# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Brain circuit analyses and validations.
"""

import os
from tqdm import tqdm
import pandas as pd
from dmt.tk.journal import Logger
from dmt.data.observation.measurement.collection import\
    primitive_type as primitive_type_measurement_collection
from dmt.data.observation.measurement.collection import\
    series_type as series_type_measurement_collection
from dmt import analysis
from dmt.model.interface import InterfaceMeta
from dmt.tk.field import NA, Field, LambdaField, lazyfield, Record
from dmt.tk.author import Author
from dmt.tk.parameters import index_tree
from dmt.tk.utils.string_utils import paragraphs, make_label
from neuro_dmt import terminology
from neuro_dmt.analysis.reporting import\
    CircuitAnalysisReport

LOGGER = Logger(client=__file__, level="DEBUG")


class StructuredAnalysis(
        analysis.StructuredAnalysis):
    """
    A base class for all circuit analyses.
    """
    add_columns = Field(
        """
        A callable that accepts a measurement (a `pandas.DataFrame`)
        and adds columns...
        """,
        __default_value__=lambda measurement: measurement)
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
    sampling_methodology = Field(
        """
        A tag indicating whether this analysis will make measurements on
        random samples drawn from a relevant population of circuit constituents,
        or on the entire population. The circuit constituents population to be
        measured will be determined by a query.
        """,
        __default_value__=terminology.sampling_methodology.random) 
    processing_methodology = Field(
        """
        How to make measurements?
        `batch` :: Process all the parameter sets as a batch.
        ~          A single measurement on all the parameter sets will be
        ~          dispatched to the plotter and attached to the report.
        ~          Thus a single report will be saved at the end of the
        ~          analysis run.
        `serial` :: Process a single parameter set at a time.
        ~           For each parameter set, make a measurement, generate a
        ~           figure and attach to the report.
        ~           Save the report and return a dict mapping parameter set
        ~           to its report.
        """,
        __default_value__=terminology.processing_methodology.batch)
    phenomenon = Field(
        """
        An object providing the phenomenon analyzed.
        """)
    reference_data = Field(
        """
        A pandas.DataFrame containing reference data to compare with the
        measurement made on a circuit model.
        Each dataset in the dataframe must be annotated with index level
        'dataset', in addition to levels that make sense for the measurements.
        """,
        __default_value__=NA)
    report = Field(
        """
        A callable to generate a report using fields used in
        `StructuredAnalysis.get_report(...) method.`
        """,
        __default_value__=CircuitAnalysisReport)

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
                return '-'.join(parameter_label)
            raise TypeError(
                "Parameter labels should be either string or tuple of strings.")

        names_parameters =\
            self.names_measurement_parameters
        return\
            self.phenomenon.label\
            if not self.names_measurement_parameters else\
               "-by-".join((
                   self.phenomenon.label,
                   '_'.join(_as_label(label) 
                            for label in self.names_measurement_parameters)))

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

    def get_measurement_method(self, adapter):
        """
        Makes sense for analysis of a single phenomenon.

        Some changes below provide backward compatibility.
        """
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
                            adapter, circuit_model, **kwargs)
                except (TypeError, AttributeError, KeyError) as error_adapter_model:
                    try:
                        return\
                            self.sample_measurement(
                                adapter, circuit_model, **kwargs)
                    except Exception as error_model_adapter:
                        raise TypeError(
                            """
                            sample_measurement(...) failed with arguments
                            (model, adapter) and (adapter, model):
                            \t {}
                            \t {}
                            """.format(
                                error_adapter_model,
                                error_model_adapter))

            try:
                _adapter_measurement_method.__method__ =\
                    paragraphs(self.sample_measurement.__method__)
                        
            except AttributeError:
                _adapter_measurement_method.__method__ =\
                    "Measurement method description not provided."

            return\
                _adapter_measurement_method
        else:
            method =\
                self._get_adapter_measurement_method(adapter)
            if not hasattr(method, "__method__"):
                method.__method__ =\
                    "Measurement method description not provided."

        raise RuntimeError(
            "Unreachable point in code.")


    @lazyfield
    def description_measurement(self):
        """
        This attribute will be NA if the method is implemented and
        described in the adapter.
        """
        try:
            return self.sample_measurement.__method__
        except AttributeError:
            return NA
        raise RuntimeError("Execution cannot reach here.")


    def parameter_sets(self,
            adapter,
            circuit_model):
        """
        Get parameter sets from self.Parameters
        """
        using_random_samples =\
            self.sampling_methodology == terminology.sampling_methodology.random
        return\
            self.measurement_parameters(
                    adapter,
                    circuit_model,
                    sample_size=self.sample_size if using_random_samples else 1)

    def _get_measurement_serially(self,
            circuit_model,
            adapter,
            *args, **kwargs):
        """
        Compute the measurement, on parameter set at a time...
        """
        get_measurement =\
            self.get_measurement_method(adapter)

        for p in tqdm(self.parameter_sets(adapter, circuit_model)):
            measured_value =\
                get_measurement(
                    circuit_model,
                    sampling_methodology=self.sampling_methodology,
                    **p, **kwargs)

            if isinstance(measured_value, pd.DataFrame):
                measured_value =\
                    measured_value[self.phenomenon.label]

            if not isinstance(measured_value, pd.Series):
                try:
                    measured_value =\
                        pd.Series(
                            measured_value,
                            name=self.phenomenon.label)
                except ValueError:
                    measured_value =\
                        pd.Series(
                            [measured_value],
                            name=self.phenomenon.label)

            measured_value =\
                series_type_measurement_collection([(p, measured_value)]
                ).rename(columns={"value": self.phenomenon.label})

            data =\
                self.add_columns(
                    measured_value.reset_index(
                    ).assign(dataset=adapter.get_label(circuit_model),
                    ).set_index(["dataset"] + measured_value.index.names))
            yield\
                Record(
                    parameter_set=p,
                    data=data,
                    method=get_measurement.__method__)
            
    def get_measurement(self,
            adapter, circuit_model,
            *args,
            **kwargs):
        """
        Get a statistical measurement.
        """
        get_measurement =\
            self.get_measurement_method(adapter)

        measured_values =\
            self.measurement_collection(
                (p, get_measurement(circuit_model,
                                    sampling_methodology=self.sampling_methodology,
                                    **p, **kwargs))
                for p in tqdm(self.parameter_sets(adapter, circuit_model))
            ).rename(columns={"value": self.phenomenon.label})
        measurement =\
            self.add_columns(
                measured_values
                .reset_index()
                .assign(dataset=adapter.get_label(circuit_model))
                .set_index(["dataset"] + measured_values.index.names))
        return\
            Record(
                data=measurement,
                method=get_measurement.__method__)

    @lazyfield
    def description_reference_data(self):
        """
        TODO: return a string describing the reference data.
        """
        return NA

    def append_reference_data(self,
            measurement,
            reference_data={},
            **kwargs):
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

    def _with_reference_data(self,
            measurement,
            reference_data={}):
        """
        Deprecated
        """
        return self.append_reference_data(measurement, reference_data)

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
            measurement_model,
            reference_data,
            caption=None):
        """
        Get a figure for the analysis of `circuit_model`.

        Arguments
        ----------
        `figure_data`: The data frame to make a figure for.
        """
        plotting_data =\
            self.append_reference_data(
                measurement_model.data,
                reference_data)
        return\
            self.figures(
                plotting_data,
                caption=caption)

    def get_report(self,
            label,
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
            label=label,
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

    def __call__(self,
            adapter, model,
            author=Author.anonymous,
            **kwargs):
        """
        Make this `Analysis` masquerade as a function.

        """
        reference_data =\
            kwargs.pop(
                "reference_data",
                self.reference_data)
        provenance_circuit =\
            adapter.get_provenance(model)

        def _get_label(measurement_serial):
            return\
                '-'.join("{}_{}".format(make_label(key), make_label(value))
                         for key, value in index_tree.as_unnested_dict(
                                 measurement_serial.parameter_set.items()))\
                   .replace('{', '')\
                   .replace('}', '')\
                   .replace("'", "")

        if self.processing_methodology == terminology.processing_methodology.serial:
            return (
                Record(
                    label=_get_label(measurement),
                    sub_report=self.get_report(
                        self.label,
                        measurement.data,
                        author=author,
                        figures=self.get_figures(
                            measurement,
                            reference_data,
                            caption=measurement.method),
                        reference_data=reference_data,
                        provenance_circuit=provenance_circuit))
                for measurement in self._get_measurement_serially(
                        model, adapter, **kwargs))
        measurement =\
            self.get_measurement(
                adapter,
                model,
                **kwargs)
        report =\
            self.get_report(
                self.label,
                measurement.data,
                author=author,
                figures=self.get_figures(
                    measurement,
                    reference_data,
                    caption=measurement.method),
                reference_data=reference_data,
                provenance_circuit=provenance_circuit)

        try:
            return self.reporter.post(report)
        except AttributeError:
            return report


BrainCircuitAnalysis = StructuredAnalysis
