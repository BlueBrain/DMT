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

from .import *

class LabReport(Document):
    """
    A specialize type of report.
    """
    @field
    def title(self):
        """
        A title for this `Section` instance.
        """
        return NA

    @field
    def label(self):
        """
        A single word label.
        """
        return make_label(self.title)

    @field.cast(Phenomenon)
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
        return NA

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
        return NA

    @field.cast(Methods)
    def methods(self):
        """
        Methods used in the analysis.
        Provide a string that may have `$`-prefixed words to be filled using
        a template search-list obtained from model using the adapter method
        `get_provenance`.
        """
        return NotImplementedError

    @field.cast(Results)
    def results(self):
        """
        Result of the analysis.
        Provide a string that may have `$`-prefixed words to be filled using
        a template search-list obtained from model using the adapter method
        `get_provenance`.
        """
        return NotImplementedError

    @field.cast(ReferenceData)
    def reference_data(self):
        """
        Reference data to go with this analysis.
        """
        return NA

    @field.cast(Discussion)
    def discussion(self):
        """
        Discussion about the implications of the analysis.
        Provide a string that may have `$`-prefixed words to be filled using
        a template search-list obtained from model using the adapter method
        """
        return NA

    @field.cast(Conclusion)
    def conclusion(self):
        """
        Conclusions that can be drawn from the results presented here.
        Provide a string that may have `$`-prefixed words to be filled using
        a template search-list obtained from model using the adapter method
        """
        return NA

    def __call__(self, adapter, model, *args, **kwargs):
        """
        Call me!!!
        """
        parameters = self.methods.parameters(adapter, model, *args, **kwargs)
        measurement = self.results.collect(adaprer, model, *args,  **kwargs)

        reference_data = self.rerference_data
        try:
            references = {
                label: reference.citation
                for label, reference in reference_data.items()}
        except AttributeError:
            LOGGER.info(
                """
                Could not retrieve citations from reference data of type {}.
                """.format(
                    type(reference_data)))
            references = {}

        provenance_model =\
            adapter.get_provenance(model)

        return Record(
            phenomenon=self.phenomenon.label,
            abstract=self.abstract(adapter, label, provenance_model),
            introduction=self.introduction(adapter, model, provenance_model),
            methods=self.methods(adapter, model, provenance_model),
            results=self.result(adapter, model, provenance_model),
            reference_data=self.reference_data(adapter, model, provenance_model),
            discussion=self.discussion(adapter, model, provenance_model),
            conclusion=self.conclusion(adapter, model, provenance_model))


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


