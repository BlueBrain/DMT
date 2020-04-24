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
A simple structured documented analysis.

TODO: rethink what a simple structured document should be.
"""

import os
from abc import ABC, abstractmethod, abstractproperty
from collections.abc import Mapping, Iterable
from collections import OrderedDict, namedtuple
import pandas as pd
from Cheetah.Template import Template
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



