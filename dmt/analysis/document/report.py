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
A type of document.
"""

from dmt.tk.utils.string_utils import make_label
from .import *

def _get_label(x):
    try:
        return x.label
    except AttributeError:
        return make_label(x)
    return None

class LabReport(Document):
    """
    A specialize type of report.
    """
    @lazyfield
    def sections(self):
        """A list of sections in this report."""
        return OrderedDict([
            (section.label, section)
            for section in [
                    self.abstract,
                    self.introduction,
                    self.methods,
                    self.results,
                    self.discussion,
                    self.conclusion]
            if section is not NA])

    @classmethod
    def get_class_sections(cls):
        """..."""
        return [
            cls.abstract,
            cls.introduction,
            cls.methods,
            cls.results,
            cls.discussion,
            cls.conclusion]

    @lazyfield
    def label(self):
        """
        A single word label.
        """
        return make_label(self.title)

    #@field.cast(Phenomenon)
    def phenomenon(self):
        """
        Phenomenon studied in this lab-report. 
        """
        return NA

    @field.cast(Abstract)
    def abstract(self):
        """
        Abstract of what, and how of this analysis.
        Provide a string that may have `$`-prefixed words to be filled using
        a template search-list obtained from model using the adapter method
        `get_provenance`.
        """
        #raise FieldIsRequired
        return None

    @field.cast(Introduction)
    def introduction(self):
        """
        Introduction to the analysis.
        Provide at least a  string that may have `$`-prefixed words to be filled 
        using a template search-list obtained from model using the adapter 
        method `get_provenance`.

        To include data and, an illustration in addition to a narrative,
        provide either a `Section` with these attributes, or a dictionary
        with keys `narrative`, `data`, and `illustration`.
        """
        #raise FieldIsRequired
        return None

    @field.cast(Methods)
    def methods(self):
        """
        Methods used in the analysis.
        Provide a string that may have `$`-prefixed words to be filled using
        a template search-list obtained from model using the adapter method
        `get_provenance`.
        """
        #raise FieldIsRequired
        return None

    @field.cast(Results)
    def results(self):
        """
        Result of the analysis.
        Provide a string that may have `$`-prefixed words to be filled using
        a template search-list obtained from model using the adapter method
        `get_provenance`.
        """
        #raise FieldIsRequired
        return None

    @field.cast(Section)
    def discussion(self):
        """
        Discussion about the implications of the analysis.
        Provide a string that may have `$`-prefixed words to be filled using
        a template search-list obtained from model using the adapter method
        """
        return None

    @field.cast(Section)
    def conclusion(self):
        """
        Conclusions that can be drawn from the results presented here.
        Provide a string that may have `$`-prefixed words to be filled using
        a template search-list obtained from model using the adapter method
        """
        return None

    def save(self, value_report, path_parent):
        """
        """
        path_report = path_parent.joinpath("report")
        path_report.mkdir(parents=False, exist_ok=True)

        self.abstract.save(value_report.abstract, path_report)
        self.introduction.save(value_report.introduction, path_report)
        self.methods.save(value_report.methods, path_report)
        self.results.save(value_report.results, path_report)

        return path_report

    def __call__(self, adapter, model, *args, **kwargs):
        """
        Call me!!!
        """
        return Record(
            phenomenon=_get_label(self.phenomenon),
            abstract=self.abstract(adapter, model),
            introduction=self.introduction(adapter, model),
            methods=self.methods(adapter, model),
            results=self.results(adapter, model))
            #discussion=self.discussion(adapter, model),
            #conclusion=self.conclusion(adapter, model))


    @classmethod
    def load_analysis(cls, analysis):
        """
        Load an analysis as a chapter.

        The code is deprecated.

        TODO: Update the code 
        """
        #self.analysis = analysis

        def method_measurement(adapter, model, *args, **kwargs):

            return analysis.get_measurment_method(adapter)

            return cls(
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


    def analysis(self):
        """
        Export an Analysis
        """
        raise NotImplementedError


