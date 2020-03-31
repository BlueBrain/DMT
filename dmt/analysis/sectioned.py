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
A circuit analysis with sections.
Each section corresponds to a section in the report that will be produced when
a `SectionedAnalysis` instance is called on a `(model, adapter)` pair.
"""
import os
import pandas as pd
from Cheetah.Template import Template
from collections.abc import Mapping, Iterable
from collections import OrderedDict, namedtuple
from tqdm import tqdm
import warnings
from dmt.tk.journal import Logger
from dmt.analysis import Analysis
from dmt.model.interface import InterfaceMeta, interfacemethod
from dmt.data.observation.measurement\
    import collection as measurement_collection
from dmt.tk.field import NA, Field, LambdaField, lazyfield, WithFields, Record
from dmt.tk.author import Author
from dmt.tk.parameters import Parameters
from dmt.tk.stats import Statistics
from dmt.tk.plotting import BasePlotter
from dmt.tk.reporting import Report, Reporter
from dmt.tk.reporting.section import Section as ReportSection
from dmt.tk.utils.string_utils import paragraphs
from dmt.tk.collections.dataframes import make_dataframe_hashable
from dmt.tk import terminology
from dmt.tk.utils.string_utils import make_label


LOGGER = Logger(client=__file__)


class Narrative(WithFields):
    """
    Text of a section.
    """
    content = Field(
        """
        A text that can be used as a `Cheetah Template` that uses words
        prefixed by a `$` tags to be filled in from a mapping.
        This mapping will be obtained from a `(adapter, model)` pair to produce
        a story about the model.
        Note that a string without any `$` prefixed words will also do, and
        may be used if you fill in the model specific details by hand.

        Or a callable on `(adapter, circuit)`
        """)

    @interfacemethod
    def get_provenance(adapter, model):
        """
        Get a provenance describing the model,
        mapping attributes such as the model's authors, release-date,
        the modeled system etc.
        This mapping should contain (at least) all the keys used in the content 
        of this `Narrative` instance.
        """
        raise NotImplementedError

    def __init__(self, content=NA, *args, **kwargs):
        """..."""
        super().__init__(*args, content=content, **kwargs)

    def __call__(self, adapter, model, *args, **kwargs):
        """..."""
        if not self.content:
            return NA

        try:
            return self.content(adapter, model, *args, **kwargs)
        except TypeError:
            pass

        LOGGER.ignore(
            "fill template {}".format(self.content),
            "adapter: {}".format(adapter),
            "model: {}".format(model))
        try:
            return\
                str(Template(
                    self.content,
                    adapter.get_provenance(model)))
        except Exception as error:
            LOGGER.warn(
                "Could not fill the template:",
                "{}".format(error))
        return self.content


class Data(WithFields):
    """..."""
    measurement = Field(
        """
        Either of: 1. a `pandas.DataFrame` with the parameters in the index,
        ~             measurement values in columns
        ~          2. a callable on `(adapter, model)`  pair that returns such
        ~             a `pandas.DataFrame`.
        """)

    def __init__(self, m=NA, *args, **kwargs):
        """..."""
        super().__init__(*args, measurement=m, **kwargs)

    def __call__(self,
            adapter, model,
            parameters=None,
            collection=measurement_collection.primitive_type,
            **kwargs):
        """
        Arguments
        -----------
        parameters :: Parameter sets to compute the measurement.
        ~             Either of:
        ~             1. A `pandas.DataFrame` with each row providing
        ~                a single parameter set. Column names of this
        ~                dataframe will be used to query the model for a
        ~                value of the measured phenomenon for each parameter set.
        ~             2. A callable on `(adapter, model)` that returns such a
        ~                dataframe.
        ~             3. None, in which case it will be assumed that either
        ~                the this `Section`'s attribute `data` is either a
        ~               `pandas.DataFrame` or returns one when called on
        ~                `(adapter, model)`
        """
        if isinstance(self.measurement, (pd.DataFrame,)):
            return self.measurement

        if isinstance(self.measurement, Mapping):
            return self.measurement

        if not self.measurement:
            return pd.DataFrame()

        assert callable(self.measurement)

        if parameters is not None:
            try:
                parameter_sets =\
                    parameters(adapter, model, **kwargs)
            except TypeError:
                parameter_sets =(
                    row for _, row in parameters.iterrows())
            data =\
                collection(
                    (p, self.measurement(adapter, model, **p, **kwargs))
                    for p in tqdm(parameter_sets)
                ).assign(dataset=adapter.get_label(model)
                ).reset_index(
                ).set_index(["dataset", "region", "layer"])
        else:
            try:
                data =\
                    self.measurement(adapter, model, **kwargs)
            except TypeError:
                data =\
                    self.measurement(**kwargs)
        return data


class Illustration(WithFields):
    """..."""
    figures = Field(
        """
        Either of : 1. a single graphic (.png, .pdf)
        ~           2. a mapping of {label-->graphic}
        ~           3. a callable on measurement data, and / or (adapter, model)
        ~              that produces graphics...
        """)

    def __init__(self, figures=NA, *args, **kwargs):
        """..."""
        super().__init__(*args, figures=figures, **kwargs)

    def __call__(self, adapter, model, data, *args, **kwargs):
        """

        Arguments
        ------------

        """
        if not self.figures:
            return {"figure": NA}
        try:
            figures =\
                self.figures(data, adapter, model, *args, **kwargs)
        except TypeError:
            figures = self.figures

        return\
            figures if isinstance(figures, Mapping)\
            else {"figure": figures}


class Section(WithFields):
    """
    A section of an analysis, that must be callable on a
    `(circuit_model, adapter)` pair.
    """
    title = Field(
        """
        A title for this `Section` instance.
        """,
        __default_value__=NA)
    label = LambdaField(
        """
        A single word tag.
        """,
        lambda self: make_label(self.title))
    narrative = Field(
        """
        A formattable string providing a story about a model, that can
        be formatted using adapter calls on the model.
        """,
        __default_value__=NA,
        __as__=Narrative)
    data = Field(
        """
        Either a `pandas.DataFrame` or a callable on a `(adapter, model)` pair
        that can produce a `pandas.DataFrame`.
        """,
        __default_value__=NA,
        __as__=Data)
    illustration = Field(
        """
        Either a mapping {label->graphic} in `.png/.pdf` format, or a callable 
        on a `(adapter, model)` pair that can produce such a mapping.
        """,
        __default_value__=NA,
        __as__=Illustration)

    def __init__(self, *args, **kwargs):
        """
        TODO: interpret arguments to initialize...
        """
        super().__init__(*args, **kwargs)

    def __call__(self,
            adapter, model,
            **kwargs):
        """Call Me"""
        data =\
            self.data(adapter, model, **kwargs)
                      
        LOGGER.ignore(
            "Section {}".format(self.label),
            "data {}".format(data) )
        if isinstance(data, pd.DataFrame):
            measurement =\
                data.rename(columns={"value": self.label})
        elif isinstance(data, Mapping):
            measurement ={
                dataset: dataframe.rename(columns={"value": self.label})
                for dataset, dataframe in data.items()}
        else:
            LOGGER.alert(
                LOGGER.get_source_info(),
                "Cannot handle data of type: {}".format(type(data)))
            measurement = {}
            
        return Record(
            title=self.title,
            label=self.label,
            narrative=self.narrative(adapter, model),
            data=measurement,
            illustration=self.illustration(
                adapter, model, measurement, **kwargs))


class Chapter(WithFields):
    """
    An analysis with sections.
    When called on a `(circuit, adapter)` pair, each section will be output
    as a section in a report.
    """
    title = Field(
        """
        A title for this `Section` instance.
        """,
        __default_value__=NA)
    label = LambdaField(
        """
        A single word tag.
        """,
        lambda self: make_label(self.title))
    phenomenon = Field(
        """
        Phenomenon studied in this chapter.
        """)
    abstract = Field(
        """
        Abstract of what, and how of this analysis.
        Provide a string that may have `$`-prefixed words to be filled using
        a template search-list obtained from model using the adapter method
        `get_provenance`.
        """,
        __as__=Narrative,
        __default_value__=NA)
    introduction = Field(
        """
        Introduction to the analysis.
        Provide at least a  string that may have `$`-prefixed words to be filled 
        using a template search-list obtained from model using the adapter 
        method `get_provenance`.

        To include data and, an illustration in addition to a narrative,
        provide either a `Section` with these attributes, or a dictionary
        with keys `narrative`, `data`, and `illustration`.
        """,
        __as__=Section,
        __default_value__=NA)
    methods = Field(
        """
        Methods used in the analysis.
        Provide a string that may have `$`-prefixed words to be filled using
        a template search-list obtained from model using the adapter method
        `get_provenance`.
        """,
        __as__=Section,
        __default_value__=NA)
    parameters = Field(
        """
        Parameters used to compute the measurement associated with this analysis.
        """,
        __as__=Section,
        __default_value__=NA)
    measurement = Field(
        """
        A section with a callable providing measurement on `(adapter, model)`
        """,
        __as__=Section)
    results = Field(
        """
        Result of the analysis.
        Provide a string that may have `$`-prefixed words to be filled using
        a template search-list obtained from model using the adapter method
        `get_provenance`.
        """,
        __as__=Section,
        __default_value__=NA)
    reference_data = Field(
        """
        Reference data to go with this analysis.
        """,
        __as__=Section,
        __default_value__=NA)
    discussion = Field(
        """
        Discussion about the implications of the analysis.
        Provide a string that may have `$`-prefixed words to be filled using
        a template search-list obtained from model using the adapter method
        `get_provenance`.
        """,
        __as__=Narrative,
        __default_value__=NA)

    def __init__(self, analysis):
        """
        Initialize a `Chapter` instance with an analysis.
        """
        self.analysis = analysis

        def method_measurement(adapter, model, *args, **kwargs):
            return analysis.get_measurment_method(adapter)

        super().__init__(
            title=analysis.phenomenon.label,
            phenomenon=analysis.phenomenon,
            abstract=analysis.abstract,
            introduction=analysis.introduction,
            methods=analysis.methods,
            parameters=Section(
                data=lambda *a, **kw: pd.DataFrame(
                    analysis.parameters.for_sampling(*a, **kw))),
            measurement=Section(
                title=analysis.phenomenon.name,
                label=analysis.phenomenon.label,
                narrative=analysis.description_measurement,
                data=method_measurement),
            reference_data=Section(
                title="Reference Data",
                label=analysis.phenomenon.label,
                narrative=analysis.description_reference_data,
                data=analysis.reference_data),
            results=Section(
                title="Results",
                narrative=analysis.results,
                data=analysis.append_reference_data,
                illustration=analysis.figures))

    def __call__(self, adapter, model, *args, **kwargs):
        """.."""
        parameters =\
            self.parameters(adapter, model,
                            *args, **kwargs)
        measurement =\
            self.measurement(adapter, model,
                             parameters=parameters.data,
                             **kwargs)
        reference_data =\
            self.reference_data(adapter, model)
        try:
            references ={
                label: reference.citation
                for label, reference in reference_data.items()}
        except AttributeError:
            LOGGER.info(
                """
                Could not retrieve citations from reference data of type {}.
                """.format(
                    type(reference_data)))

            references = {}

        results =\
            self.results(
                adapter, model,
                measurement=measurement.data,
                reference_data=reference_data.data)
        return Record(
            phenomenon=self.phenomenon.label,
            abstract=self.abstract(adapter, model),
            introduction=self.introduction(adapter, model),
            methods=self.methods(adapter, model),
            reference_data=reference_data,
            measurement=measurement,
            results=results,
            discussion=self.discussion(adapter, model),
            references=references)


class StructuredAnalysis(Analysis):
    """
    An analysis structured with chapters and sections.
    """
    author = Field(
        """
        An object describing the author of this `SectionAnalysis` instance.
        """,
        __default_value__=Author.anonymous)
    phenomenon=Field(
        """
        The (group) phenomenon analyzed.
        """)
    abstract = Field(
        """
        Abstract of what, and how of this analysis.
        Provide a string that may have `$`-prefixed words to be filled using
        a template search-list obtained from model using the adapter method
        `get_provenance`.
        """,
        __as__=Narrative,
        __default_value__=NA)
    introduction = Field(
        """
        Introduction to the analysis.
        Provide at least a  string that may have `$`-prefixed words to be filled 
        using a template search-list obtained from model using the adapter 
        method `get_provenance`.

        To include data and, an illustration in addition to a narrative,
        provide either a `Section` with these attributes, or a dictionary
        with keys `narrative`, `data`, and `illustration`.
        """,
        __as__=Section,
        __default_value__=NA)
    AdapterInterface = Field(
        """
        A class written as a subclass of `Interface` that declares and documents
        the methods required of the adapter by this analysis.
        You may provide the adapter interface either at instantiation of a
        `SectionedAnalysis`, or define it inside a `SectionedAnalysis` subclass,
        or mark methods with the decorator @interfacemethod in the subclass' body.
        """,
        __type__=InterfaceMeta)
    chapters = Field(
        """
        A list of chapters.
        """)
    report = Field(
        """
        A callable that will generate a report for a chapter in this analysis.
        The callable should be able to take arguments listed in `get_report(...)`
        method defined below.
        """,
        __default_value__=Report)

    def _report(self, chapter, provenance_model):
        """
        Get report for a chapter.

        Arguments
        ------------
        chapter :: A `Record` instance produced by calling this analysis'
        ~         `Chapter` instances.
        """
        return\
            self.report(
                author=self.author,
                phenomenon=chapter.phenomenon,
                abstract=chapter.abstract,
                introduction=chapter.introduction.narrative,
                methods=chapter.methods.narrative,
                measurement=chapter.measurement.data,
                figures=chapter.results.illustration,
                results=chapter.results.narrative,
                discussion=chapter.discussion,
                references=chapter.references,
                provenance_model=provenance_model)

    def __call__(self,  adapter, model, **kwargs):
        """..."""
        provenance =\
            adapter.get_provenance(model)
        if len(self.chapters) == 1:
            chapter =\
                self.chapters[0]
            return\
                self._report(
                    chapter(adapter, model, **kwargs),
                    provenance)
        chapter_reports =[
            self._report(chapter(adapter, model, **kwargs), provenance)
            for chapter in self.chapters]
        return\
            self.report(
                author=self.author,
                phenomenon=self.phenomenon.label,
                abstract=self.abstract(adapter, model),
                introduction=self.introduction(adapter, model),
                chapters=chapter_reports,
                provenance_model=provenance)
