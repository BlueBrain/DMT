"""
Infrastructure for neuroscience analyses reports.
"""

import os
from Cheetah.Template import Template
from dmt.tk.field import Field, lazyfield
from dmt.tk.journal import Logger
from dmt.tk.reporting import Report, Reporter
from dmt.tk.utils import string_utils, get_file_name_base

logger = Logger(client=__file__)

class CircuitAnalysisReport(Report):
    """
    Add some circuit analysis specific attributes to `Report`
    """
    animal = Field(
        """
        Animal species whose brain was modeled.
        """,
        __default_value__="Not Available")
    age = Field(
        """
        Age of the animal.
        """,
        __default_value__="Not Available")
    brain_region = Field(
        """
        Name of the region in the brain that the circuit models.
        """,
        __default_value__="Not Available")
    uri = Field(
        """
        Location of the circuit.
        """,
        __default_value__="Not Available")

    @lazyfield
    def field_values(self):
        """..."""
        fields = super().field_values
        fields.update(dict(
            animal=self.animal,
            age=self.age,
            brain_region=self.brain_region,
            uri=self.uri,
            references=self.references
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
    <br>
    <h2> Figures </h2>
    #for $label_image, $location_image in $images.items()
        <img src=$location_image alt="apologies.png"/>
        #for $line in $captions[$label_image].splitlines()
        <br><strong>$line</strong></br>
        #end for
    <p>$(140 * '-')</p>
    #end for
    </br>
    <p>$(70 * '=')</p>

    <h3>Circuit Analyzed</h3>
        <p>$(70 * '=')</p>
        <p>Animal: $animal</p>
        <p>Age: $age</p>
        <p>Brain Region: $brain_region</p>
        <p>URI: $uri</p>
        <p>$(70 * '=')</p>

    <h3>Introduction</h3>
        <p>$(70 * '=')</p>
        <p>$introduction</p>
        <p>$(70 * '=')</p>

    <h3>Methods</h3>
        <p>$(70 * '=')</p>
        <p>$methods</p>
        <p>$(70 * '=')</p>

    <h3>Results</h3>
        <p>$(70 * '=')</p>
        <p>$results</p>
        <p>$(70 * '=')</p>

    <h3>Discussion</h3>
        <p>$(70 * '=')</p>
        <p>$discussion</p>
        <p>$(70 * '=')</p>

    <h3>References</h3>
        <p>$(70 * '=')</p>
        #for $label, $citation in $references.items()
        <p><strong>$label</strong>: $citation</p>
        #end for
        <p>$(70 * '=')</p>

  </body>

</html>
        """)

    def _get_captions(self, report):
        """
        Create a figure caption.
        """
        return {
            label: figure.caption
            for label, figure in report.figures.items()
        }

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
            references=report.references
            ))
        return template_dict

    def post(self,
            report,
            output_uri=None,
            report_file_name="report.html",
            strict=False,
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
                output_uri)
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
                raise Exception(
                    "Failed to generate HTML for the report: \n\t{}".format(
                        html_error))

            with open(path_report_file, "w") as file_output:
                file_output.write(report_html)

            return output_uri

        except Exception as template_fill_error:
            if strict:
                raise template_fill_error
            logger.warning(
                logger.get_source_info(),
                "Error during filling the report template: \n\t{}".format(
                    template_fill_error))

            return super()._save_text_report(report, output_uri, folder_figures)

        raise RuntimeError(
            "Execution should not have reached here.")
