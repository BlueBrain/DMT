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

from abc import abstractmethod
from collections import OrderedDict
from collections.abc import Mapping
import pickle
from pathlib import Path
import re
from Cheetah.Template import Template
import pandas as pd
from dmt.model import AIBase
from dmt.model.interface import interfacemethod
from dmt.data.observation.measurement import\
    collection as measurement_collection
from dmt.data.observation.measurement.collection import\
    primitive_type, series_type, vector_type, summary_type, multi_type
from dmt.tk.journal import Logger
from dmt.tk.parameters import Parameters
from dmt.tk.field import\
    field, Field,\
    lambdafield, LambdaField,\
    lazyfield,\
    NA, Record,\
    WithFields,\
    FieldIsRequired
from dmt.tk.utils.string_utils import make_label
from neuro_dmt import terminology
from .template import TaggedTemplateString

LOGGER = Logger(client=__file__)


class Narrative(WithFields):
    """
    Mixin to provide text of a `DocElem`.
    """
    def __init__(self, text=NA, **kwargs):
        kwargs["text"] = text
        super().__init__(**kwargs)
    # def __init__(self, *args, **kwargs):
    #     if isinstance(self, DocElem) and args:
    #         raise TypeError(
    #             """
    #             A `WithFields` mix in cannot be initialized with arguments.
    #             Use only keyword arguments.
    #             """)
    #     if args:
    #         super().__init__(*args[1:], text=args[0], **kwargs)
    #     else:
    #         super().__init__(**kwargs)

    @field.cast(TaggedTemplateString)
    def text(self):
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

    @interfacemethod
    def get_namespace(adapter, model):
        """
        Get a namepsace to fill the text with.
        """
        raise NotImplementedError

    def save(self, value, path_folder):
        """..."""
        try:
            value_narrative = value.narrative
        except AttributeError:
            value_narrative = value

        path_folder = Path(path_folder)
        path_folder.mkdir(parents=True, exist_ok=True)

        path_file = path_folder.joinpath("narrative.txt")

        with open(path_file, 'w') as output_file:
            output_file.write(value_narrative)

        try:
            save_super = super().save
        except AttributeError:
            return path_file

        return save_super(value, path_folder)

    def __call__(self, adapter, model, namespace=None, **kwargs):
        """...Call Me..."""
        if self.text:
            if not namespace:
                namespace = adapter.get_namespace(model)
            try:
                narrative = self.text.format(**namespace)
            except AttributeError:
                narrative = str(self.text)
        else:
            narrative = str(NA)

        try:
            get_record = super().__call__
        except AttributeError:
            if not isinstance(self, DocElem):
                return narrative
            get_record = lambda *args, **kwargs: Record()
        return get_record(
            adapter, model, **kwargs
        ).assign(
            narrative=narrative
        )


class Data(WithFields):
    """
    Mixin to hold data of a `DocElem`.

    TODO: figure out what we want from a `Data` object.

    """
    class Collector(WithFields):
        """
        Collect a measurement...
        """
        label = Field(
            """
            Single word string to name the measurement column.
            """,
            __default_value__="value")
        sample_size = Field(
            """
            Number of repetitions for each set of parameter values.
            """,
            __default_value__=1)
        @field.cast(Parameters)
        def parameters(self):
            """
            Parameter sets to measure with.
            Or a callable that produces such parameters...
            """
            raise FieldIsRequired

        @field
        def method(self, *args, **kwargs):
            """
            That makes a measurement.
            """
            raise FieldIsRequired

        @field
        def collection(self):
            """
            A policy to collect the measurements over all parameter sets
            """
            return measurement_collection.primitive_type

        def __call__(self, adapter, model, *args, **kwargs):
            """
            Collect a measurement
            """
            return\
                self.collection(
                    (p, self.method(adapter, model, **p, **kwargs))
                    for p in self.parameters(
                            adapter, model,
                            sample_size=self.sample_size,
                            **kwargs)
                ).rename(
                    columns={"value": self.label}
                )


    @field
    def measurement(self):
        """
        Either:
        1. `Callable` on `(adapter, model)`
        ~   that returns a `pandas.DataFrame`.
        2. `pandas.DataFrame` with parameters in the index,
        ~  and measurement values in columns.
        """
        return NA

    @staticmethod
    def _is_null_data(value):
        """..."""
        if isinstance(value, (pd.DataFrame, pd.Series)):
            return value.empty
        try:
            return len(value) == 0
        except TypeError:
            pass
        if value is None or value is NA:
            return True
        return False

    def __init__(self, measurement=NA, **kwargs):
        kwargs["measurement"] = measurement
        super().__init__(**kwargs)

    def save(self, value, path_folder, *args, **kwargs):
        """..."""
        def _flattened_columns(dataframe):
            """
            Flatten MultiIndexed columns...
            """
            return pd.DataFrame(
                dataframe.values,
                columns=pd.Index([
                    '_'.join(t) if isinstance(t, tuple) else t
                    for t in dataframe.columns.values]))

        try:
            save_super = super().save
        except AttributeError:
            save_super = None

        if self.measurement is NA or self.measurement is None:
            if save_super:
                return save_super(value, path_folder)
            return None

        try:
            value_data = value.data
        except AttributeError:
            # if isinstance(self, DocElem):
            #     if save_super:
            #         return save_super(value, path_folder)
            #     return None
            value_data = value


        if self._is_null_data(value_data):
            if not save_super:
                return None
            return save_super(value, path_folder)

        if isinstance(value_data, Mapping):
            path_data = Path(path_folder).joinpath("data")
            path_data.mkdir(parents=True, exist_ok=True)
            for label, sub_data in value_data.items():
                if isinstance(sub_data, pd.DataFrame):
                    _flattened_columns(
                        sub_data.reset_index()
                    ).to_csv(
                        path_data.joinpath("{}.csv".format(label)),
                        index=False, index_label=False
                    )
                else:
                    path_file = path_folder.joinpath("{}.pickle".format(label))
                    with open(path_file, 'w') as jar:
                        pickle.dump(sub_data, jar)
        else:
            path_folder = Path(path_folder)
            path_folder.mkdir(parents=True, exist_ok=True)
            if isinstance(value_data, pd.DataFrame):
                _flattened_columns(
                    value_data.reset_index()
                ).to_csv(
                    path_folder.joinpath("data.csv"),
                    index=False, index_label=False
                )
            else:
                path_file = path_folder.joinpath("data.pickle")
                with open(path_file, 'w') as jar:
                    pickle.dump(value_data, jar)

        if not save_super:
            return path_folder
        return save_super(value, path_folder)

    def __call__(self,
            adapter, model,
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
        try:
            get_super_record = super().__call__
        except AttributeError:
            get_super_record = None

        if callable(self.measurement):
            data = self.measurement(adapter, model, **kwargs)
        elif isinstance(self.measurement, Mapping):
            data = {}
            for label, sub_measurement in self.measurement.items():
                if callable(sub_measurement):
                    data[label] = sub_measurement(adapter, model, **kwargs)
                else:
                    data[label] = sub_measurement
        else:
            data = self.measurement

        if not get_super_record:
            if isinstance(self, DocElem):
                if self._is_null_data(data):
                    return Record()
                return Record(data=data)
            if self._is_null_data(data):
                return None
            return data

        super_record = get_super_record(adapter, model, **kwargs)
        if self._is_null_data(data):
            return super_record
        return super_record.assign(data=data)


class Illustration(WithFields):
    """
    Illustrate a document.

    Mixin to provide figures to a `DocElem`.

    TODO: code tests for how an `Illustration`'s  behavior.
    """
    @field
    def figures(self):
        """
        One of :
        ~ 1. single graphic (.png, .pdf)
        ~ 2. callable{ (data, *args, **kwargs)->graphic}
        ~ 3. mapping{
        ~      label->Either[
        ~        graphic,
        ~        callable{ (data, *args,**kwargs)->graphic }]}
        """
        return NA

    @field.cast(TaggedTemplateString)
    def caption(self):
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


    def __init__(self, figures_and_caption=NA, *args, **kwargs):
        """
        Arguments
        ----------------
        figures :: Either a figure,
        ~          or a Mapping{caption, figures}
        ~          or a Record{caption, figures}
        """
        print(figures_and_caption)
        if figures_and_caption is not NA:
            try:
                figures_and_caption = figures_and_caption.field_dict
            except AttributeError:
                pass
            try:
                if "figures" in figures_and_caption:
                    kwargs.update(figures_and_caption)
                else:
                    raise TypeError(
                        """
                        `figures` not provided in the argument {}
                        """.format(figures_and_caption))
            except TypeError:
                kwargs["figures"] = figures_and_caption
                    
            kwargs.update(figures_and_caption)
        super().__init__(*args, **kwargs)

    @interfacemethod
    def get_namespace(adapter, model):
        """
        Get a namepsace to fill the caption.
        """
        raise NotImplementedError

    def save(self, value, path_folder, *args, **kwargs):
        """..."""
        try:
            save_super = super().save
        except AttributeError:
            save_super = None

        if not self.figures:
            if save_super:
                return save_super(value, path_folder)
            return None

        try:
            value_illustration = value.illustration
        except AttributeError:
            value_illustration = value

        path_folder = Path(path_folder).joinpath("illustration")
        path_folder.mkdir(parents=True, exist_ok=True)

        name_file_caption = "caption.txt"
        path_caption = path_folder.joinpath(name_file_caption)
        with open(path_caption, 'w') as output_file:
            output_file.write(str(value_illustration.caption))

        for label, figure in value_illustration.figures.items():
            if isinstance(figure, Mapping):
                path_group_figures =\
                    path_folder.joinpath(label)
                path_group_figures.mkdir(parents=True, exist_ok=True)
                for sub_label, sub_figure in figure.items():
                    path_graphic =\
                        path_group_figures.joinpath(sub_label + ".png")
                    sub_figure.save(path_graphic)
            else:
                path_graphic =\
                    path_folder.joinpath(label + ".png")
                figure.save(path_graphic, dpi=100)

        if not save_super:
            return path_folder
        return save_super(value, path_folder)


    def _get_figures(self, adapter, model, *args, **kwargs):
        """..."""
        data = kwargs.pop("data", None)
        if data is None:
            try:
                data = self.measurement
            except AttributeError:
                pass

        if callable(self.figures):
            if not data:
                raise TypeError(
                    """
                    Argument `data` is required for a callable figure.
                    """)
            if callable(data):
                value_data = data(adapter, model, *args, **kwargs)
            else:
                value_data = data

            figures =\
                self.figures(
                    value_data, *args,
                    adapter=adapter,
                    model=model,
                    **kwargs)

        elif isinstance(self.figures, Mapping):
            figures = {}
            for label, figure in self.figures.items():
                if callable(figure):
                    if not data:
                        raise TypeError(
                            """
                            Argument `data` is required for a callable figure.
                            """)
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

                    if callable(data_figure):
                        value_data = data_figure(adapter, model, label=label)
                    else:
                        value_data = data_figure
                        
                    figures[label] =\
                        figure(
                            value_data, *args,
                            adapter=adapter,
                            model=model,
                            **kwargs)
                else:
                    figures[label] = figure
        else:
            raise ValueError(
                """
                Illustration.figures type {}.
                It should either be a callable, or a mapping.
                """.format(type(self.figures)))

        return figures

    def _get_caption(self, adapter, model, *args, **kwargs):
        """..."""
        namespace = kwargs.get("namespace", None)
        if self.caption:
            if not namespace:
                namespace = adapter.get_namespace(model)
            try:
                return self.caption.format(**namespace)
            except:
                return str(self.caption)
        else:
            return str(NA)

    def __call__(self,
            adapter, model, *args,
            **kwargs):
        """
        Get an illustration...

        Arguments
        -----------------
        """
        try:
            get_super_record = super().__call__
        except AttributeError:
            get_super_record = None


        figures = self._get_figures(adapter, model, *args, **kwargs)
        caption = self._get_caption(adapter, model, *args, **kwargs)

        if not figures and not caption:
            record = None
        else:
            record = Record(figures=figures, caption=caption)

        if not get_super_record:
            if isinstance(self, DocElem):
                if record:
                    return Record(illustration=record)
                return Record()
            return record

        super_record = get_super_record(adapter, model, **kwargs)
        if record:
            return super_record.assign(illustration=record)
        return super_record


class DocElem(WithFields, AIBase):
    """..."""
    title = Field(
        """
        Title of this document element.
        """)
    label = LambdaField(
        """
        A single word tag for this document element.
        """,
        lambda self: make_label(self.title))

    @field
    def parent(self):
        """
        Parent `DocElem` that contains this one.
        """
        raise FieldIsRequired

    @field
    def children(self):
        """
        A sequence of `DocElem`s that are contained in this one.
        """
        return tuple()

    def save(self, record, path):
        """Save this `DocElem`"""
        try:
            save_super = super().save
        except AttributeError:
            return path
        return save_super(record, Path(path).joinpath(self.label))

    def __call__(self, adapter, model, *args, **kwargs):
        """..."""
        try:
            get_record = super().__call__
        except AttributeError:
            return Record(title=self.title, label=self.label)
        return get_record(
            adapter, model, *args, **kwargs
        ).assign(
            title=self.title, label=self.label
        )
            

class Document(WithFields):
    """
    The root document
    """
    title = Field(
        """
        Title of this document element.
        """)

    def __init__(self, title, *args, **kwargs):
        super().__init__(title=title, *args, **kwargs)

    @field
    def elements(self):
        """
        An ordered sequence of elements contained in this document.
        """
        return OrderedDict()
