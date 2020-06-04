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

from Cheetah.Template import Template
from dmt.tk.author import Author
from dmt.tk.utils.string_utils import make_label, paragraphs
from neuro_dmt.analysis.reporting import CheetahReporter
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
    author = Field(
        """
        Author(s) of the report.
        """,
        __default_value__=Author.anonymous)
    reporter = Field(
        """
        An object that will hold attributes generated for a (adapter, model)
        """,
        __default_value__=Record)

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
        path_report = path_parent.joinpath(self.label)
        path_report.mkdir(parents=False, exist_ok=True)

        return Record(
            _=path_report,
            abstract=self.abstract.save(
                value_report.abstract, path_report),
            introduction=self.introduction.save(
                value_report.introduction, path_report),
            methods=self.methods.save(
                value_report.methods, path_report),
            results=self.results.save(
                value_report.results, path_report))


    def __call__(self, adapter, model, *args, **kwargs):
        """
        Call me!!!
        """
        return Record(
            author=self.author,
            phenomenon=_get_label(self.phenomenon),
            label=self.label,
            abstract=self.abstract(adapter, model),
            introduction=self.introduction(adapter, model),
            methods=self.methods(adapter, model),
            results=self.results(adapter, model))
            #discussion=self.discussion(adapter, model),
            #conclusion=self.conclusion(adapter, model))

    
    def post(self, report, path_output):
        """
        Post a report that was generated by this `LabReport` instance
        applied to some (adapter, model)

        Arguments
        ---------------
        report :: Results of this `LabReport` applied to some `(adapter, model)`
        uri :: Location where the report will be posted.
        """
        template="""
        <html>
          <body>
            #if $title_main_report
              <h1>$title (<A HREF=$path_main_report>$title_main_report</A>)</h1>
            #else
              <h1>$title</h1>
              <hr>
              <h2> Author </h2>
              <hr style="width:50%;text-align:left;margin-left:0">
                <h3> $author_name </h3>
                <h3> Affiliation: $author_affiliation </h3>
            #end if
            <hr style="height:2px;border-width:0;color:gray;background-color:gray">

            <h2>Abstract</h2>
            <hr style="width:50%;text-align:left;margin-left:0">
              #for $line in $abstract
                 <p>$line</p>
              #end for
            <hr style="height:2px;border-width:0;color:gray;background-color:gray">

            <h2>Introduction</h2>
            <hr style="width:50%;text-align:left;margin-left:0">
            #for $line in $introduction
                <p>$line</p>
            #end for

            #if $introduction_images
              <h3>Figures</h3>
              <hr style="width:50%;text-align:left;margin-left:0">
              #for $label, $figures in $introduction_images.items()
                #for $figure_label, $location in $figures.items():
                   <p>
                   <strong>($figure_label.capitalize()):</strong>
                   <img src=$location alt="apologies.png">
                   <hr style="height:1px;border-width:0;color:gray;background-color:gray;width:50%;text-align:left;margin-left:0">
                   </p>
                #end for
                <p>
                  <strong>$label.capitalize():</strong>
                  #for $line in $introduction_captions[label]
                    $line
                  #end for
                <hr style="height:3px;border-width:0;color:gray;background-color:gray">
                </p>
              #end for
            #end if
            <hr style="height:2px;border-width:0;color:gray;background-color:gray">

            <h2>Methods</h2>
            <hr style="width:50%;text-align:left;margin-left:0">
            #for $line in $methods
               <p>$line</p>
            #end for
            <p>Measurements were made on the circuit model as follows:</p>
            #for label, description in $methods_measurements.items():
              <p>
                <strong>$label.capitalize():</strong>
                #for $line in $description
                  $line
                #end for
              </p>
            #end for
            <hr style="height:2px;border-width:0;color:gray;background-color:gray">

            <h2>Results</h2>
            <hr style="width:50%;text-align:left;margin-left:0">
            #for $line in $results
                <p>$line</p>
            #end for

            #if $results_images
              <h3>Figures</h3>
              <hr style="width:50%;text-align:left;margin-left:0">
              #for $label, $figures in $results_images.items()
                #for $figure_label, $location in $figures.items():
                   <p>
                   <strong>($figure_label.capitalize()):</strong>
                   <img src=$location alt="apologies.png">
                   <hr style="height:1px;border-width:0;color:gray;background-color:gray;width:50%;text-align:left;margin-left:0">
                   </p>
                #end for
                <p>
                  <strong>$label.capitalize():</strong>
                  #for $line in $results_captions[label]
                    $line
                  #end for
                <hr style="height:3px;border-width:0;color:gray;background-color:gray">
                </p>
              #end for
            #end if
            <hr style="height:2px;border-width:0;color:gray;background-color:gray">

            #if $results_tables
              <h3>Tables</h3>
              <hr style="width:50%;text-align:left;margin-left:0">
              #for $label, $table in $results_tables.items():
                 <p>
                 <strong>($label.capitalize*()):</strong>
                 #for $line in $table:
                   $line
                 #end for
                 </p>
              #end for
           #end if
          <h3>Source</h3>
          <p>
          This report was prepared using
          <a href=https://github.com/BlueBrain/DMT>DMT</a>
          </p>
          </body>
        </html>
        """
        path_artefacts = self.save(report, path_output)

        template_dict = {
            field: value
            for field, value in report.field_dict.items()
        }
        template_dict["title"] = self.title
        #TODO: move template stuff to its own class...
        width_page = 70
        under_line_type = '-'
        end_line_type = '='

        template_dict.update(dict(
            underline=width_page * under_line_type,
            longunderline=2 * width_page * under_line_type,
            endline=width_page * end_line_type,
            author_name=report.author.name,
            author_affiliation=report.author.affiliation))

        if self.parent != self.parent:
            template_dict["title_main_report"] = self.parent.title
        else:
            template_dict["title_main_report"] = None

        abstract = report.abstract
        template_dict["abstract"] =\
            paragraphs(abstract.narrative)

        introduction = report.introduction 
        template_dict["introduction"] =\
            paragraphs(introduction.narrative)
        try:
            illustration_introduction = introduction.illustration
        except AttributeError:
            illustration_introduction = {}

        introduction_images = {}
        introduction_captions = {}
        for label, illustration in introduction.illustration.items():
            introduction_captions[label] =\
                paragraphs(illustration.caption)

        for label, figures in path_artefacts.introduction\
                                            .illustration\
                                            .items():
            if isinstance(figures, Mapping):
                introduction_images[label] = OrderedDict([
                    (sub_label, sub_figure_path.relative_to(path_artefacts._))
                    for sub_label, sub_figure_path in figures.items()
                ])
            else:
                introduction_images[label] = figures.relative_to(path_artefacts._)
                
        template_dict["introduction_images"] = introduction_images
        template_dict["introduction_captions"] = introduction_captions


        methods = report.methods
        template_dict["methods"] =\
            paragraphs(methods.narrative)

            
        try:
            methods_measurements = methods.measurements
        except AttributeError:
            methods_measurements = {}

        template_dict["methods_measurements"] = OrderedDict([
            (label, paragraphs(description))
            for label, description in methods_measurements.items()
        ])
        results = report.results 
        template_dict["results"] =\
            paragraphs(results.narrative)
        try:
            illustration_results = results.illustration
        except AttributeError:
            illustration_results = {}

        results_images = {}
        results_captions = {}
        for label, illustration in results.illustration.items():
            results_captions[label] =\
                paragraphs(illustration.caption)

        for label, figures in path_artefacts.results\
                                            .illustration\
                                            .items():
            if isinstance(figures, Mapping):
                results_images[label] = OrderedDict([
                    (sub_label, sub_figure_path.relative_to(path_artefacts._))
                    for sub_label, sub_figure_path in figures.items()
                ])
            else:
                results_images[label] = figures.relative_to(path_artefacts._) 

        template_dict["results_images"] = results_images
        template_dict["results_captions"] = results_captions


        results_tables = {}
        for label, table in results.tables.items():
            results_tables[label] = table.to_html(classes=label).split('\n')

        template_dict["results_tables"] = results_tables
        
        try:
            report_template_filled =\
                Template(template, searchList=template_dict)
        except Exception as template_fill_error:
            self.logger.alert(
                self.logger.get_source_info(),
                """
                Error filling the report template:
                {}
                \t{}
                """.format(
                    type(template_fill_error),
                    template_fill_error))
            return path_saved_artefacts

        try:
            report_html = str(report_template_filled)
        except Exception as html_error:
            self.logger.alert(
                self.logger.get_source_info(),
                """
                Failed to generate HTML for the report:
                {}
                \t{}
                """.format(
                    type(html_error),
                    html_error))
            raise html_error

        path_file =\
            path_artefacts._.joinpath("report.html")
        with open(path_file, 'w') as file_ptr:
            file_ptr.write(report_html)
        return path_file


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


