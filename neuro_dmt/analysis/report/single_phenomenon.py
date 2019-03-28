
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
class AnalysisReport(
        Report):
    """A class to be used to report all of our composition validations.
    The html produced by the Cheetah Template used here will display a plot for
    the validation, with a caption, metadata about the authors and their
    affiliation, and the status of the validation.

    Notes
    ---------------------------------------------------------------------------
    Associated Cheetah template must be placed  in a directory named templates
    in the same directory as this file."""

    author=\
        Field(
            __name__ = "author",
            __type__ = Author,
            __doc__  = """Author of this validation. If a group has authored,
            please create a group user as author.""")
    phenomenon=\
        Field(
            __name__ = "phenomenon",
            __type__ = Phenomenon,
            __doc__  = """Phenomenon that was validated / analyzed.""")
    figure=\
        Field.Optional(
            __name__="figure",
            __type__=object,
            __doc__="A plot figure")
    caption=\
        Field(
            __name__ = "caption",
            __type__ = list,
            __typecheck__=Field.typecheck.collection(str),
            __doc__ = "Caption to go with the plot.")

    def __init__(self,
            default_template="report.cheetah",
            *args, **kwargs):
        """initialize!"""
        if "template" in kwargs:
            self.template\
                = kwargs["template"]
        else:
            template_loc\
                = kwargs.get(
                    "template_loc",
                    os.path.join(
                        os.path.dirname(__file__),
                        "templates",
                        default_template) )
            with open(template_loc, 'r') as template_file:
                self.template=\
                    template_file.read()
                         
        super().__init__(
            *args, **kwargs)

    def save(self,
            output_dir_path=None,
            report_file_name="report.html"):
        """Save report to disc, as an html.

        Parameters
        -----------------------------------------------------------------------
        output_dir_path :: String #directory where report artefacts should go
        report_file_name :: String #name of the file to use for this report

        Implementation Notes
        ------------------------------------------------------------------------
        Try to create a (html) string using its class' template and save that
        tothe disc. If this fails, call 'Report._save_default'.
        """
        output_dir_path=\
            self.get_output_location(
                output_dir_path=output_dir_path)
        self.save_measurement(
            output_dir_path)
        file_name_base= \
            get_file_name_base(
                report_file_name)
        report_file_name= \
            file_name_base + ".html"
        report_file_path=\
            os.path.join(
                output_dir_path,
                report_file_name)
        plot_file_name= \
            file_name_base + ".png"
        plot_file_path=\
            os.path.join(
                output_dir_path,
                plot_file_name)

        self.logger.debug(
            self.logger.get_source_info(),
            "Saving report to {} ".format(report_file_path))

        self.logger.info(
            self.logger.get_source_info(),
            "Generating {}".format(plot_file_path))

        try:
            self.figure.savefig(
                plot_file_path, dpi=100)
        except AttributeError as attribute_error:
            self.logger.alert(
                self.logger.get_source_info(),
                """Missing figure (Field) in {} instance."""\
                .format(self.__class__.__name__),
                """Error caught: {}"""\
                .format(attribute_error))
        try:
            #the following is ugly
            #
            #Cheetah template are not exactly the same attributes as this report
            template_dict = self.__report_dict__
            template_dict.update(dict(
                image_name=plot_file_name,
                phenomenon=self.phenomenon.name,
                author_name=self.author.name,
                author_affiliation=self.author.affiliation))
            report_template\
                = Template(
                    self.template,
                    searchList=template_dict)
            try:
                report_html = str(report_template)
            except Exception as ex_html:
                raise Exception(
                    """WARNING!!! While generating html: {}.\n"""\
                    .format(ex_html))
                
            with open(report_file_path, 'w') as f:
                f.write(report_html)

            return report_file_path

        except Exception as ex: #convert the following to a warning
            self.logger.alert(
                self.logger.get_source_info(),
                """WARNING!!!
                While loading the template {}.
                Will proceed to save a text report""".format(ex))

            return self._save_default(
                output_dir_path,
                file_name_base)


class AnalysisMultiFigureReport(
        AnalysisReport):
    """For analysis that produce multiple figures."""
    figure=\
        Field(
            __name__="figure",
            __type__=dict,
            __doc__="""A dict mapping label to figure""")

    def __init__(self,
            *args, **kwargs):
        """Initialize Me"""
        super().__init__(
            default_template="multi_report.cheetah",
            *args, **kwargs)


    def save(self,
            output_dir_path=None,
            report_file_name="report.html"):
        """..."""
        output_dir_path=\
            self.get_output_location(
                output_dir_path=output_dir_path)
        file_name_base=\
            get_file_name_base(
                report_file_name)
        report_file_name= \
            file_name_base + ".html"
        report_file_path=\
            os.path.join(
                output_dir_path,
                report_file_name)
        self.logger.debug(
            self.logger.get_source_info(),
            "Saving report to {} ".format(report_file_path))

        def __plot_file_name(
                figure_label):
            """..."""
            return os.path.join(
                "{}_{}.png".format(
                    file_name_base,
                    figure_label))

        for figure_label, figure in self.figure.items():
            plot_file_path=\
                os.path.join(
                    output_dir_path,
                    __plot_file_name(figure_label))
            self.logger.info(
                self.logger.get_source_info(),
                "Generating {}".format(
                    plot_file_path))
            figure.savefig(
                plot_file_path)
        try:
            template_dict=\
                self.__report_dict__
            template_dict.update(dict(
                image_names=[
                    __plot_file_name(figure_name)
                    for figure_name in self.figure.keys()],
                phenomenon=self.phenomenon.name,
                author_name=self.author.name,
                author_affiliation=self.author.affiliation))
            self.logger.debug(
                self.logger.get_source_info(),
                "create a template with dict {}".format(template_dict))
            report_template=\
                Template(
                    self.template,
                    searchList=template_dict)
            try:
                report_html=\
                    str(report_template)
            except Exception as ex_html:
                raise Exception(
                    """WARNING !!! While generating html : {}.\n"""\
                    .format(ex_html))

            with open(report_file_path, 'w') as f:
                f.write(report_html)

            return report_file_path

        except Exception as ex:
            self.logger.alert(
                self.logger.get_source_info(),
            """WARNING!!! While loading the template {}.
            Will proceed to save a text report""".format(ex))

            return self._save_default(
                output_dir_path,
                file_name_base)
