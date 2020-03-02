"""
Infrastructure for neuroscience analyses reports.
"""

import os
from collections.abc import Mapping
from Cheetah.Template import Template
from dmt.tk.field import Field, lazyfield
from dmt.tk.journal import Logger
from dmt.tk.reporting import Report, Reporter
from dmt.tk.utils import string_utils, get_file_name_base
from dmt.tk.field import Field, WithFields

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

    references = Field(
        """
        References of literature cited in this report.
        """,
        __type__=Mapping,
        __default_value__={})

    @lazyfield
    def field_values(self):
        """..."""
        fields = super().field_values
        fields.update(dict(
            animal=self.provenance_model.animal,
            age=self.provenance_model.age,
            brain_region=self.provenance_model.brain_region,
            uri=self.provenance_model.uri,
            references=self.references,
            date_release=self.provenance_model.date_release,
            authors_circuit=self.provenance_model.authors
        ))
        return fields

class CheetahReporter(Reporter):
    """
    Report with a cheetah template.
    """
    template = Field(
        """
        Cheetah report that will be used to create an HTML report.
        """,
        __default_value__="""
<html>
  <body>

    <h1>$phenomenon Analysis</h1>
    <h2> Author </h2>
    <h3> $author_name </h3>
    <h3> Affiliation: $author_affiliation </h3>

    <h2>Circuit Analyzed</h2>
        <p>$(70 * '=')</p>
        <p>Animal: $animal</p>
        <p>Age: $age</p>
        <p>Brain Region: $brain_region</p>
        <p>URI: $uri</p>
        <p>Author: $authors_circuit</p>

    <h2>Introduction</h2>
        <p>$(70 * '=')</p>
        #for $line in $introduction
          <p>$line</p>
        #end for

    <h2>Methods</h2>
        <p>$(70 * '=')</p>
        #for $line in $methods
        <p>$line</p>
        #end for

    <h2>Results</h2>
        <p>$(70 * '=')</p>
        #for $line in $results
          <p>$line</p>
        #end for
    <br>
    <p>$(70 * '-')</p>
    #for $label_image, $location_image in $images.items()
        <img src=$location_image alt="apologies.png"/>
        <h3>Caption</h3>
        #for $line in $captions[$label_image]
          $line
        #end for
    #end for
    </br>

    <h2>Discussion</h2>
        <p>$(70 * '=')</p>
        #for $line in $discussion
          <p>$line</p>
        #end for

    <h2>References</h2>
        <p>$(70 * '=')</p>
        #for $label, $citation in $references.items()
          <p><strong>$label</strong>: $citation</p>
        #end for

  </body>

</html>
        """)

    def _get_captions(self, report):
        """
        Create a figure caption.
        """
        return {
            label: figure.caption
            for label, figure in report.figures.items()}

    def filled_template(self, report, figure_locations):
        """
        Fill in the template.
        """
        template_dict = report.field_values
        def _make_name(label):
            return\
                string_utils.make_name(
                    label,
                    separator='_',
                    keep_original_capitalization=True)
        template_dict.update(dict(
            author_name=report.author.name,
            author_affiliation=report.author.affiliation,
            images={
                _make_name(label): location
                for label, location in figure_locations.items()},
            captions={
                _make_name(label): figure.caption
                for label, figure in report.figures.items()},
            references=report.references))
        return template_dict

    def post(self,
            report,
            path_output_folder=None,
            output_subfolder=None,
            report_file_name="report.html",
            strict=False,
            with_time_stamp=True,
            *args, **kwargs):
        """
        Post the report.

        output_uri : Uniform resource identifier where the report should be
        ~            posted.
        strict : If `True`, a backup text report will not be generated.
        """
        output_uri =\
            self.get_output_location(
                report,
                path_output_folder=path_output_folder,
                output_subfolder=output_subfolder,
                with_time_stamp=with_time_stamp)
        base_file_name =\
            get_file_name_base(report_file_name)
        path_report_file =\
            os.path.join(
                output_uri,
                "{}.html".format(base_file_name))

        folder_figures, locations_figures =\
            self._save_figures(report, output_uri)

        self._save_measurement(report, output_uri)

        try:
            report_template_filled =\
                Template(
                    self.template,
                    searchList=self.filled_template(report, locations_figures))
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

        if report.sections:
            for section in report.sections:
                self.post(
                    section,
                    path_output_folder=output_uri,
                    with_time_stamp=False)

        return output_uri
