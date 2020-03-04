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

    def __call__(self, adapter, model):
        """..."""
        if not self.content:
            return NA
        try:
            return\
                str(Template(
                    self.content,
                    adapter.get_provienance(adapter, model)))
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

    def __call__(self, adapter, model, *args, **kwargs):
        """..."""
        if not self.measurement:
            return pd.DataFrame()
        try:
            return self.measurement(adapter, model, *args, **kwargs)
        except TypeError:
            return self.measurement


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

    def __call__(self, adapter, model, data=None, *args, **kwargs):
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
    measurement = Field(
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

    def get_measurement(self,
                adapter, model,
                parameters=None,
                collect=measurement_collection.primitive_type,
                *args, **kwargs):
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
        if parameters is not None:
            try:
                parameter_values =\
                    parameters(adapter, model, *args, **kwargs)
            except TypeError:
                parameter_values =(
                    row for _, row in parameters.iterrows())
            measurement =\
                collect(
                    (p, self.measurement(adapter, model, **p, **kwargs))
                    for p in tqdm(parameter_values))
        else:
            measurement =\
                self.measurement(adapter, model, *args, **kwargs)
        return\
            measurement.rename(columns={"value": self.title})\
            if self.title else\
               measurement

    def __call__(self, model, adapter, parameters=None, *args, **kwargs):
        """Call Me"""
        measurement =\
            self.get_measurement(
                adapter, model, parameters, *args, **kwargs)
        return Record(
            narrative=self.narrative(
                adapter, model, *args, **kwargs),
            data=measurement,
            illustration=self.illustration(
                adapter, model, measurement, *args, **kwargs))


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

    author = Field(
        """
        An object describing the author of this `SectionAnalysis` instance.
        """,
        __default_value__=Author.anonymous)
    AdapterInterface = Field(
        """
        A class written as a subclass of `Interface` that declares and documents
        the methods required of the adapter by this analysis.
        You may provide the adapter interface either at instantiation of a
        `SectionedAnalysis`, or define it inside a `SectionedAnalysis` subclass,
        or mark methods with the decorator @interfacemethod in the subclass' body.
        """,
        __type__=InterfaceMeta)
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
    results = Field(
        """
        Result of the analysis.
        Provide a string that may have `$`-prefixed words to be filled using
        a template search-list obtained from model using the adapter method
        `get_provenance`.
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
