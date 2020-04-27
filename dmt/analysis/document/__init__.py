# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published
#  by the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A  PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License 
# along with DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Document an analysis.
"""

import re
from Cheetah.Template import Template
from dmt.model import AIBase
from dmt.model.interface import interfacemethod
from dmt.data.observation.measurement import\
    collection as measurement_collection
from dmt.tk.journal import Logger
from dmt.tk.parameters import Parameters
from dmt.tk.field import\
    field, Field,\
    lambdafield, LambdaField,\
    lazyfield,\
    NA, Record,\
    WithFields
from dmt.tk.utils.string_utils import make_label
from neuro_dmt import terminology

LOGGER = Logger(client=__file__)


class Narrative(WithFields, AIBase):
    """
    Text of a document.
    """
    @field
    def content(self):
        """
        Either of:
        1. Callable returning a text.
        ~  The arguments of the call are up to the implementation.
        ~  `(adapter, model)` will be passed, along with keyword arguments.
        ~  So the implementation's signature should be:
        ~  `adapter -> model -> *args -> **kwargs -> text`
        2. Text that can be used as a `Cheetah Template`.
        ~  A word prefixed by a `$` tag will be searched in a `searchList`,
        ~  a mapping `tag -> value`.
        ~  This mapping will be generated from `(adapter, model)` passed to
        ~  the `__call__` method or can be passed directly to the `__call__`
        ~  method.
        """
        return NA

    def __init__(self, content=NA, **kwargs):
        """
        Check keyword arguments and initialize.

        TODO: Remove this initializer to allow `figures` be a class method,
        ~     that takes `(adapter, model)` and returns a graphics.
        """
        super().__init__(content=content, **kwargs)

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

    def __call__(self, adapter, model, *args, **kwargs):
        """...Call Me..."""
        if not self.content:
            return NA

        try:
            return self.content(adapter, model, *args, **kwargs)
        except TypeError:
            pass

        try:
            if not '$' in self.content:
                return self.content
        except TypeError:
            pass
        try:
            provenance = kwargs["provenance"]
        except KeyError:
            provenance = adapter.get_provenance(model)

        try:
            return str(Template(self.content, provenance))
        except Exception as error:
            LOGGER.warn(
                LOGGER.get_source_info(),
                "Could not fill the template.",
                "{}".format(error))

        return self.content


class Data(WithFields, AIBase):
    """
    An object to carry document data.

    TODO: figure out what we want from a `Data` object.

    """
    @field
    def value(self):
        """
        Either:
        1. `Callable` on `(adapter, model)`
        ~   that returns a `pandas.DataFrame`.
        2. `pandas.DataFrame` with parameters in the index,
        ~  and measurement values in columns.
        """
        return NA

    def __init__(self, value=NA, **kwargs):
        """
        Check keyword arguments and initialize.

        TODO: Remove this initializer to allow `figures` be a class method,
        ~     that takes `(adapter, model)` and returns a graphics.
        """
        super().__init__(value=value, **kwargs)

    def __call__(self,
            adapter, model,
            parameters=None,
            collection=measurement_collection.primitive_type,
            **kwargs):
        """
        Call me

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
        if callable(self.value):
            if parameters is not None:
                try:
                    parameter_sets = parameters(adapter, model, **kwargs)
                except TypeError:
                    parameter_sets = (row for _, row in parameters.iterrows())

                data = collection(
                    (p, value(adapter, model, **p, **kwargs))
                    for p in parameter_sets)
            else:
                try:
                    data =\
                        self.value(adapter, model, **kwargs)
                except TypeError:
                    data =\
                        self.value(**kwargs)
            return data

        return self.value


class Illustration(WithFields, AIBase):
    """
    Illustrate a document.

    TODO: code tests for how an `Illustration`'s  behavior.
    """
    @field
    def figures(self):
        """
        One of :
        ~ 1. single graphic (.png, .pdf)
        ~ 2. callable{ (data,adapter,model,*args,**kwargs)->graphic}
        ~ 3. mapping{
        ~      label->Either[
        ~        graphic,
        ~        callable{ (data,adapter,model,*args,**kwargs)->graphic }]}
        """
        return NA

    def __init__(self, figures=NA, **kwargs):
        """
        Check keyword arguments and initialize.

        TODO: Remove this initializer to allow `figures` be a class method,
        ~     that takes `(adapter, model)` and returns a graphics.
        """
        super().__init__(figures=figures, **kwargs)

    def __call__(self, adapter, model, data=None, *args, **kwargs):
        """
        Get an illustration...
        """
        try:
            graphic = self.figures(data, adapter, model, *args, **kwargs)
            return {"figure": graphic}
        except TypeError:
            figures = {}
            for label, figure in self.figures.items():
                try:
                    data_figure = data[label]
                except TypeError:
                    LOGGER.warn(
                        LOGGER.get_source_info(),
                        """
                        Data type {} for an illustration with
                        multi-figures.  Ideally, use a mapping with
                        same keys as `self.figures`:
                        \t {}.
                        Will attempt by using the entire data object
                        for figure {}.
                        """.format(
                            type(data),
                            list(self.figures.keys()),
                            label))
                    data_figure = data
                    pass
                except KeyError:
                    LOGGER.warn(
                        LOGGER.get_source_info(),
                        """
                        No data for figure {}.
                        Will attempt by using the entire data object.
                        """.format(label))
                    data_figure = data
                    pass
                
                try:
                    figures[label] =\
                        figure(data_figure, adapter, model, *args, **kwargs)
                except TypeError:
                    figures[label] = figure
                return figures
                
        return self.figures


class Document(WithFields, AIBase):
    """
    A document accompanying an analysis, that can be called on
    `(adapter, model)`.

    `Document` is organized as an hierarchy, represented as a tree of nested
    structs.

    TODO: Decide what a document should contain...
    ~     1. `Document` is abstract description of what a document should be
    ~     2. `Document` will serve as a base class
    ~     3. A `Document` instance (not of a base-class) can be the root of
    ~        hierarchically organized document.
    """
    @field
    def narrative(self):
        """
        Story of the document.
        """
        return NA

    @field
    def data(self):
        """
        Data associated with the document.
        """
        return NA

    @field
    def illustration(self):
        """
        Figures associated with the document.
        """
        return NA


class Section(Document):
    """
    A leaf in a document hierarchy.

    TODO: code a test-case to develop behavior of a `Section`
    """
    @field
    def title(self):
        """
        A title for this `Section` instance.
        """
        return NA

    @lambdafield
    def label(self):
        """
        A single word tag.
        """
        return make_label(self.title)

    @field.cast(Data)
    def data(self):
        """
        Either a `pandas.DataFrame` or a callable on a `(adapter, model)` pair
        that can produce data.
        """
        return NA

    @field.cast(Narrative)
    def narrative(self):
        """
        A formattable string that provides a story about a model.
        Or a callable on `(adapter, model)` that can produce such a
        string.
        """
        return NA

    @field.cast(Illustration)
    def illustration(self):
        """
        Either a mapping `(label -> graphic)`,
        or a callable on `(adapter, model)` that can produce such a mapping.
        """
        return NA

    def __init__(self, *args, **kwargs):
        """
        TODO: interpret arguments to initialize with
        """
        super().__init__(*args, **kwargs)

    def __call__(self, adapter, model, *args, **kwargs):
        """
        Call me to get a section document ...
        """
        data = self.data(adapter, model, **kwargs)
        return Record(
            title=self.title,
            label=self.label,
            data=data,
            narrative=self.narrative(adapter, model, data=data, **kwargs),
            illustration=self.illustration(adapter, model, data=data, **kwargs))


class Abstract(DocumentElement):
    def __init__(self, content, **kwargs):
        super().__init__(
            title="Abstract",
            label="abstract",
            narrative=content,
            data=NA,
            illustration=NA,
            **kwargs)
    

class Introduction(Section):
    """
    Handles introduction to the document.
    """
    def __init__(self, content, data=NA, figures=NA, **kwargs):
        """..."""
        super().__init__(
            title="Introduction",
            label="introduction",
            narrative=content,
            data=data,
            illustration=figures,
            **kwargs)


class Methods(Section):
    """
    Describe the phenomenon studied in this analysis,
    quantitatively and computationally:
    1. What measurement is made?
    2. What parameters are used.
    """

    class Sample(WithFields):
        """
        Specify how a sample of measurements is made.
        """
        size = Field(
            """
            Number of samples to measure for each set of the measurement
            parameters. This field will be relevant when the measurements
            are made on random samples. When the measurement is exhaustive,
            the whole population of (relevant) circuit constituents will be
            measured.
            """,
            __default_value__=20)
        methodology = Field(
            """
            Abstract tag indicating whether this analysis will make
            measurements on random samples draw from a relevant population of
            circuit  components, or on the entire relevant population.
            """,
            __default_value__=terminology.sampling_methodology.random)

    sample = Field(
        """
        An instance of `Methods.Sample`.
        """,
        __as__=Sample)

    processing = Field(
        """
        Specify how measurements should be made.
        `batch` :: Process all the parameters as a batch.
        ~          A single measurement on all the parameters sets will be
        ~          dispatched downstream. This should lead to a single
        ~          report document.
        `serial`:: Process a single parameter set at a time.
        ~          For each parameter set, make a measurement, dispatch it
        ~          downstream to generate a figure / report...
        ~          This will lead to a composite report...
        
        TODO :: What should the role of `batch` vs `serial` be? Descriptions
        above made sense in the case of `StructuredAnalysis` and need to be
        updated.
        """)

    @field.cast(Parameters)
    def parameters(self):
        """
        Parameter sets to measure with,
        or a callable that produces such parameters...
        """
        return NA

    def get_parameters(self, adapter, model, **kwargs):
        using_random_samples =\
            self.sample.methodology == terminology.sampling_methodology.random
        return\
            self.parameters(
                adapter, model,
                sample_size=self.sample.size if using_random_samples else 1)

    @field
    def measurement(self):
        """
        Measure a model phenomenon for a single set of parameters.

        Arguments
        ---------------
        parameters : paramters for the measurements
        customizations : that specify the method used to make a measurement
        """
        return NA


class Results(Section):
    """
    Describe results of measuring the phenomenon,
    quantitatively and computationally:
    1. How the measurement is assembled.
    2. What the implications of the observed results are.
    """
    chapter = Field(
        """
        The `Chapter` instance holding this `Results` instance.
        """)
    collection = Field(
        """
        A callable that will collect measurements passed as an iterable.
        The default value assumes that the each measurement will return an
        elemental value such as integer, or floating point number.
        """,
        __default_value__=measurement_collection.primitive_type)
    
    def collect(self, adapter, model, *args, **kwargs):
        """
        Collect the results.
        """
        # methods =\
        #     self.chapter.methods(adapter, model, *args, **kwargs)
        value =\
            self.chapter.methods.measurement
        measurement =\
            self.collection(
                (p, value(adapter, model,
                          sampling_methodology=methods.sample.methodology,
                          **p, **kwargs))
                for p in tqdm(methods.get_parameters(adapter, model))
            ).rename(
                columns={"value": self.chapter.phenomenon.label})
        dataset=\
            adapter.get_label(model)
        return\
            Record(
                data=pd.concat([measurement], keys=[dataset], names=["dataset"]),
                method=self.chapter.methods.narrative(adapter, model, **kwargs))
        

class RefefenceData(Section):
    pass


class Discussion(Section):
    pass


class Conclusion(Section):
    pass


class Chapter(DocumentElement):
    """
    An analysis with sections.
    When called on a `(circuit, adapter)` pair, each section will be output
    as a section in a report.
    """

    sections = Field(
    "list of sections.")   

