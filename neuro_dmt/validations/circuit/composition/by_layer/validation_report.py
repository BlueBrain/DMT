"""Report by layer composition validations."""

import os
from Cheetah.Template import Template
from dmt.vtk.reporting import Report
from dmt.vtk.utils.exceptions import RequiredKeywordArgumentError
from dmt.vtk.utils.descriptor import Field
from dmt.vtk.phenomenon import Phenomenon
from dmt.vtk.author import Author
from dmt.vtk.utils.utils import get_file_name_base
from dmt.vtk.utils.logging import Logger, with_logging

@with_logging(Logger.level.STUDY)
class ValidationReport(Report):
    """A class to be used to report all of our composition validations.
    The html produced by the Cheetah Template used here will display a plot for
    the validation, with a caption, metadata about the authors and their
    affiliation, and the status of the validation.

    Notes
    ----------------------------------------------------------------------------
    Associated Cheetah template must be placed  in a directory named templates
    in the same directory as this file.
    """

    validated_phenomenon = Field(
        __name__ = "validated_phenomenon",
        __type__ = Phenomenon,
        __doc__  = """Phenomenon that was validated."""
    )
    validation_image_name = Field(
        __name__ = "validation_image_name",
        __type__ = str,
        __doc__  = """Name of the file in which validation image has been saved."""
    )
    validation_image_dir = Field(
        __name__ = "validation_image_dir",
        __type__ = str,
        __doc__  = """Location of the image produced by the validation."""
    )
    author = Field(
        __name__ = "author",
        __type__ = Author,
        __doc__  = """Author of this validation. If a group has authored,
        please create a group user as author."""
    )
    caption = Field(
        __name__ = "caption",
        __type__ = str,
        __doc__ = "Caption to go with the plot."
    )
    validation_datasets = Field(
        __name__ = "validation_datasets",
        __type__ = dict,
        __doc__ = """List of metadata, one element for each dataset used by the
        validation. Please take a look at documentation of the validation."""
    )
    is_pass = Field(
        __name__ = "is_pass",
        __type__ = bool,
        __doc__  = """Are the model's predictions for the validated phenomenon
        valid when compared against the experimental measurements."""
    )
    is_fail = Field(
        __name__ = "is_fail",
        __type__ = bool,
        __doc__  = """If the validation did not pass, did it fail? It might
        have been inconclusive."""
    )
    pvalue = Field(
        __name__ = "p_value",
        __type__ = float,
        __doc__ = """P-value for observing the model measurement, when compared
        against the experimental data in the first validation dataset."""
    )

    def __init__(self, *args, **kwargs):
        """initialize!"""
        template = kwargs.get("template")
        if template is not None:
            self.template = template
        else:
            template_loc\
                = kwargs.get("template_loc",
                             os.path.join(os.path.dirname(__file__),
                                          "templates",
                                          "validation_with_plot.cheetah") )
            with open(template_loc, 'r') as f:
                self.template = f.read()
                         
        super(ValidationReport, self).__init__(*args, **kwargs)

    def save(self, output_dir_path=None, report_file_name="report.html"):
        """Save report to disc, as an html.

        Parameters
        ------------------------------------------------------------------------
        output_dir_path :: String #directory where report artefacts should go
        report_file_name :: String #name of the file to use for this report

        Implementation Notes
        ------------------------------------------------------------------------
        Try to create a (html) string using its class' template and save that
        tothe disc. If this fails, call 'Report._save_default'.
        """
        file_name_base = get_file_name_base(report_file_name)
        file_name = file_name_base + ".html"
        output_dir_path = os.path.join(
            output_dir_path if output_dir_path else os.getcwd(),
            "report"
        )
        if not os.path.exists(output_dir_path):
            os.makedirs(output_dir_path)
        report_file_path = os.path.join(output_dir_path, file_name)

        self.logger.debug(
            self.logger.get_source_info(),
            "Saving report to {} ".format(report_file_path))

        try:
            #the following is ugly
            #Cheetah template are not exactly the same attributes as this report
            template_dict = self.__report_dict__
            template_dict['validated_phenomenon']\
                = self.validated_phenomenon.name
            template_dict['author_name']\
                = self.author.name
            template_dict['author_affiliation']\
                = self.author.affiliation

            t = Template(self.template, searchList=self.__report_dict__)
            try:
                report_html = str(t)
            except Exception as ex_html:
                raise Exception("""WARNING!!!
                While generating html: {}.\n""".format(ex_html))
                
            with open(report_file_path, 'w') as f:
                f.write(str(t))

            return report_file_path

        except Exception as ex: #convert the following to a warning
            self.logger.alert(
                self.logger.get_source_info(),
                """WARNING!!!
                While loading the template {}.
                Will proceed to save a text report""".format(ex))

            return self._save_default(output_dir_path, file_name_base)

