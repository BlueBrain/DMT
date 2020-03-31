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
Infrastructure for neuroscience analyses reports.
"""

import os
from collections.abc import Mapping, Generator
from collections import OrderedDict
from Cheetah.Template import Template
from dmt.tk.utils import timestamp
from dmt.tk.field import Field, LambdaField, lazyfield
from dmt.tk.journal import Logger
from dmt.tk.reporting import Report, Reporter
from dmt.tk.utils import string_utils, get_file_name_base
from dmt.tk.utils.string_utils import make_name, make_label
from dmt.tk.field import Field, WithFields, NA
from dmt.tk.utils.string_utils import paragraphs

LOGGER = Logger(client=__file__)


class CircuitProvenance(WithFields):
    """
    Provenance of a circuit.
    """
    label = Field(
        """
        A label that names the circuit model.
        """,
        __default_value__="")
    authors = Field(
        """
        A list of authors who built the circuit model.
        """,
        __default_value__=["Not Available"])
    date_release = Field(
        """
        When the circuit model was released in its final form.
        """,
        __default_value__="YYYYMMDD")
    uri = Field(
        """
        URI from where the circuit model can be loaded.
        """,
        __default_value__="https://www.example.com")
    animal = Field(
        """
        The animal whose brain was modeled.
        """,
        __default_value__="Not Available")
    age = Field(
        """
        Age of the animal at which its brain was modeled.
        """,
        __default_value__="XYZ Weeks")
    brain_region = Field(
        """
        Brain region that was modeled.
        """,
        __default_value__="Somatosensory Cortex (SSCx)")


class CircuitAnalysisReport(Report):
    """
    Add some circuit analysis specific attributes to `Report`
    """
    provenance_model = Field(
        """
        Either a `class CircuitProvenance` instance or a dict providing values
        for the fields of `class CircuitProvenance`.
        """,
        __as__=CircuitProvenance)
    figures = Field(
        """
        A dict mapping label to an object with a `.graphic` and `.caption`
        attributes.
        """,
        __default_value__={})
    references = Field(
        """
        References of literature cited in this report.
        """,
        __type__=Mapping,
        __default_value__={})
    content = LambdaField(
        """
        All text as a single string.
        """,
        lambda self: (self.abstract +
                      self.introduction +
                      self.methods +
                      self.results +
                      self.discussion))

    @lazyfield
    def field_values(self):
        """..."""
        try:
            name_phenomenon = self.phenomenon.name
        except AttributeError:
            name_phenomenon = make_name(self.phenomenon, separator="-")
        return\
            dict(
                circuit=OrderedDict((
                    ("animal", self.provenance_model.animal),
                    ("age", self.provenance_model.age),
                    ("brain_region", self.provenance_model.brain_region),
                    ("uri", self.provenance_model.uri),
                    ("references", self.references),
                    ("date_release", self.provenance_model.date_release),
                    ("authors", '; '.join(
                        "{}. {}".format(i+1, a) 
                        for i, a in enumerate(self.provenance_model.authors))))),
                author=self.author,
                phenomenon=name_phenomenon,
                label=make_label(self.label, separator='-'),
                title=make_name(self.label, separator='-'),
                abstract=self.abstract,
                introduction=self.introduction,
                methods=self.methods,
                results=self.results,
                content=self.content,
                discussion=self.discussion)


class CheetahReporter(Reporter):
    """
    Report with a cheetah template.
    """
    width_page = Field(
        """
        Width of the page on which the report will be displayed.
        """,
        __default_value__=0)
    under_line_type=Field(
        """
        Type of line to underline section titles.
        """,
        __default_value__='-')
    end_line_type=Field(
        """
        Type of line to demark sections or chapters in the report. 
        """,
        __default_value__='=')
    template_main = Field(
        """
        Template for Cheetah that will be used to create an HTML report
        for the report's main.
        """,
        __default_value__="""
        <html>
          <body>
            #if $title_main_report
              <h1>$title (<A HREF=$path_main_report>$title_main_report Analysis</A>)</h1>
            #else
              <h1>$title Analysis</h1>
              <p>$endline</p>
              <h2> Author </h2>
                <h3> $author_name </h3>
                <h3> Affiliation: $author_affiliation </h3>
            #end if
            <p>$endline</p>

            #if $circuit
              <h2>Circuit Analyzed</h2>
                <p>$underline</p>
                #for $key, $value in $circuit.items()
                  <p><strong>$key</strong>: $value</p>
                  <p>$underline</p>
                #end for
              <p>$endline</p>
            #end if

            <h2>Abstract</h2>
              <p>$underline</p>
              #for $line in $abstract
                <p>$line</p>
              #end for
            <p>$endline</p>

            <h2>Introduction</h2>
              <p>$underline</p>
              #for $line in $introduction
                <p>$line</p>
              #end for
            <p>$endline</p>

            <h2>Methods</h2>
              <p>$underline</p>
              #for $line in $methods
                <p>$line</p>
              #end for
            <p>$endline</p>

            <h2>Results</h2>
              <p>$underline</p>
              #for $line in $results
                <p>$line</p>
              #end for

              #if $images
                <h3>Figures</h3>
                <br>{}</br>
              #end if
            <p>$endline</p>

            #if $sections
              <h2>Sections</h2>
                <p>$underline</p>
                #for $index, $section in enumerate($sections.items())
                  <p>$(index+1): <strong><A HREF=$section[1]>$section[0]</A></strong></p>
                #end for
              <p>$endline</p>
            #end if

            #if $chapters
              <h2>Chapters</h2>
                <p>$underline</p>
                #for $index, $chapter in enumerate($chapters.items())
                  <p>$(index+1): <strong><A HREF=$chapter[1]>$chapter[0]</A></strong></p>
                #end for
              <p>$endline</p>
            #end if

            <h2>Discussion</h2>
              <p>$underline</p>
              #for $line in $discussion
                <p>$line</p>
              #end for
              <p>$endline</p>

            #if $references
              <h2>References</h2>
                <p>$underline</p>
                #for $label, $citation in $references.items()
                  <p><strong>$label</strong>: $citation</p>
                #end for
              <p>$endline</p>
            #end if

          #if $title_main_report
            <p>Back to <A HREF=$path_main_report>$title_main_report Analysis</A></p>
          #end if
        </body>
      </html>
        """)
    template_figures = Field(
        """
        Template for figures...
        """,
        __default_value__="""
        #for $label_image, $location_image in $images.items()
          <img src=$location_image alt="apologies.png"/>
        <p>
           <strong>$label_image.capitalize():</strong>
           #for $line in $captions[$label_image]
             $line
           #end for
        </p>
        #end for
        """)
    template_section = Field(
        """
        Template for Cheetah that will be used to create an HTML report
        for a main report's sections.
        """,
        __default_value__="""
        <html>
          </body>
            <h2><strong><A HREF=$path_main_report>$title_main_report Analysis</A></strong></h2>

            #if $section_index
              <h3>$section_index: $title</h3>
            #else
              <h3>$title</h3>
            #end if
            <p>$underline</p>

            <h4>Figures</h4>
              <br>{}</br>

            #for $line in $content
              <p>$line</p>
            #end for
            <p>$endline</p>
          </body>
        </html>
        """)
    template = LambdaField(
        """
        The template to use...
        """,
        lambda self: self.template_main)

    def get_html_template(self, report):
        """
        HTML template for sections.
        """
        if report.figures:
            return\
                self.template.format(self.template_figures)
        return self.template

    def _get_captions(self, report):
        """
        Create a figure caption.
        """
        return {
            label: figure.caption
            for label, figure in report.figures.items()}

    def dict_template(self,
            report,
            figure_locations,
            path_main_report=None,
            title_main_report=None,
            chapters=NA,
            chapter_index=None,
            sections=NA,
            section_index=None):
        """
        Fill in the template.
        """
        template_dict ={
            field: value
            for field, value in report.field_values.items()}

        LOGGER.debug(
            "CheetahReporter.dict_template(..)",
            "report field values",
            "{}".format(template_dict))

        if chapter_index is not None or section_index is not None:
            template_dict["circuit"] = None

        def _make_name(label):
            return\
                string_utils.make_name(
                    label,
                    separator='_',
                    keep_original_capitalization=True)
        template_dict.update(dict(
            underline=self.width_page * self.under_line_type,
            endline=self.width_page * self.end_line_type,
            author_name=report.author.name,
            author_affiliation=report.author.affiliation,
            images={
                _make_name(label): location
                for label, location in figure_locations.items()},
            captions={
                _make_name(label): figure.caption
                for label, figure in report.figures.items()},
            references=report.references,
            sections=sections,
            chapters=chapters))
        if path_main_report is not None:
            template_dict["title_main_report"] =\
                title_main_report if title_main_report is not None\
                else "Main Report"
            template_dict["path_main_report"] = path_main_report
            template_dict["title"] = make_name(report.label, separator='-')
            if section_index is not None:
                template_dict["section_index"] = section_index + 1
            if chapter_index is not None:
                template_dict["chapter_index"] = chapter_index + 1
        else:
            template_dict["title_main_report"] = None
            template_dict["path_main_report"] = None


        return template_dict

    def _post_sections(self,
            report,
            output_uri,
            report_file_name,
            path_main_report,
            title_main_report):
        """
        Report sections of this report!
        """
        if report.sections:
            section_reporter =\
                self.with_fields(
                    template=self.template_section)
            return OrderedDict(
                (make_name(section.label, separator='-'),
                 os.path.join(
                     section_reporter.post(section,
                                           path_output_folder=output_uri,
                                           report_file_name=report_file_name,
                                           path_main_report=path_main_report,
                                           title_main_report=title_main_report,
                                           section_index=index,
                                           with_time_stamp=False),
                     report_file_name))
                for index, section in enumerate(report.sections))
        return NA

    def _post_chapters(self,
            report,
            output_uri,
            report_file_name,
            path_main_report,
            title_main_report):
        """
        Report chapters of this report!
        """
        if report.chapters:
            chapter_reporter =\
                self.with_fields(
                    template=self.template_main)
            return OrderedDict(
                (make_name(chapter.label, separator='-'),
                 os.path.join(
                     chapter_reporter.post(chapter,
                                           path_output_folder=output_uri,
                                           report_file_name=report_file_name,
                                           path_main_report=path_main_report,
                                           title_main_report=title_main_report,
                                           chapter_index=index,
                                           with_time_stamp=False),
                     report_file_name))
                for index, chapter in enumerate(report.chapters))
        return NA

    def post(self,
            report,
            template=None,
            path_output_folder=None,
            output_subfolder=None,
            report_file_name="report.html",
            strict=False,
            with_time_stamp=True,
            path_main_report=None,
            title_main_report=None,
            section_index=None,
            chapter_index=None,
            *args, **kwargs):
        """
        Post the report.

        output_uri : Uniform resource identifier where the report should be
        ~            posted.
        strict : If `True`, a backup text report will not be generated.
        """
        if isinstance(report, Generator):
            output_uri = {}
            if with_time_stamp:
                daytime = timestamp()
                time_stamp =\
                    os.path.join(
                        daytime.day, daytime.time)
            else:
                time_stamp = None

            for subreport in report:
                if output_subfolder is not None:
                    folder_subreport =\
                        os.path.join(subreport.label, output_subfolder)
                else:
                    folder_subreport=\
                        subreport.label
                output_uri[subreport.label] =\
                    self.post(
                        subreport.sub_report,
                        template=template,
                        path_output_folder=path_output_folder,
                        output_subfolder=folder_subreport,
                        report_file_name=report_file_name,
                        strict=strict,
                        with_time_stamp=time_stamp,
                        path_main_report=path_main_report,
                        title_main_report=title_main_report,
                        section_index=section_index,
                        chapter_index=chapter_index,
                        *args, **kwargs)

            return output_uri

        LOGGER.debug(
            """.post(report={},
                   template={},
                   path_output_folder={},
                   output_subfolder={},
                   report_file_name={},
                   strict={},
                   with_time_stamp={},
                   path_main_report={},
                   title_main_report={},
                   section_index={},
                   chapter_index={})""".format(
                       report,
                       template,
                       path_output_folder,
                       output_subfolder,
                       report_file_name,
                       strict,
                       with_time_stamp,
                       path_main_report,
                       title_main_report,
                       section_index,
                       chapter_index))
        if section_index is not None and chapter_index is not None:
            raise TypeError(
                """
                `CheetahReporter.post(...)` cannot a report that is both a
                chapter and a section.
                """)
        output_uri =\
            self.get_output_location(
                report,
                path_output_folder=path_output_folder,
                output_subfolder=output_subfolder,
                with_time_stamp=with_time_stamp)
        LOGGER.status(
            LOGGER.get_source_info(),
            "Post report {} at".format(report.label),
            "\t {}".format(output_uri))
        base_file_name =\
            get_file_name_base(report_file_name)
        path_report_file =\
            os.path.join(
                output_uri,
                "{}.html".format(base_file_name))

        folder_figures, locations_figures =\
            self._save_figures(report, output_uri)

        self._save_sections(report, output_uri)

        self._save_chapters(report, output_uri)

        self._save_measurement(report, output_uri)

        sections =\
            self._post_sections(
                report,
                output_uri,
                report_file_name,
                path_main_report=path_report_file,
                title_main_report=report.label)
        chapters =\
            self._post_chapters(
                report,
                output_uri,
                report_file_name,
                path_main_report=path_report_file,
                title_main_report=report.label)

        template_html =\
            self.get_html_template(report)

        dict_template =\
            self.dict_template(report,
                                 locations_figures,
                                 path_main_report=path_main_report,
                                 title_main_report=title_main_report,
                                 chapters=chapters,
                                 chapter_index=chapter_index,
                                 sections=sections,
                                 section_index=section_index)
        LOGGER.debug(
            "FILLED TEMPLATE",
            '\n'.join(
                "{}: {}".format(k, v) for k, v in dict_template.items()))
        try:
            report_template_filled =\
                Template(template_html, searchList=dict_template)
                                                    
            try:
                report_html = str(report_template_filled)
            except Exception as html_error:
                LOGGER.alert(
                    LOGGER.get_source_info(),
                    """
                    Failed to generate HTML for the report:
                    {}
                    \t{}
                    """.format(
                        type(html_error),
                        html_error))
                raise html_error

            with open(path_report_file, "w") as file_output:
                file_output.write(report_html)

        except Exception as template_fill_error:
            LOGGER.warning(
                LOGGER.get_source_info(),
                """
                Error during filling the report template:
                {}
                \t{}""".format(
                    type(template_fill_error),
                    template_fill_error))
            if strict:
                raise template_fill_error

            super()._save_text_report(
                report, output_uri, folder_figures)

        return output_uri
