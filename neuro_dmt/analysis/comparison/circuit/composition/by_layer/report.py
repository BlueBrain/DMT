"""Report by layer composition comparison."""
import os
from Cheetah.Template import Template
from dmt.vtk.reporting import Report
from dmt.vtk.utils.descriptor import Field
from dmt.vtk.phenomenon import Phenomenon
from dmt.vtk.author import Author
from dmt.vtk.utils import utils
from dmt.vtk.utils.logging import Logger, with_logging
from neuro_dmt.analysis.circuit.composition.by_layer.report\
    import AnalysisReport

@with_logging(Logger.level.STUDY)
class ComparisonReport(Report):
    """Report composition comparisons between models,
    or validations against experimental data.

    Description
    ---------------
    A Cheetah template is used to produce an html report.
    The template will display a comparison plot with a caption,
    metadata on the authors, and the status of the comparison.

    Notes
    ----------------
    Associated Cheetah template must be placed in a directory named templates
    in the same directory as this file."""

    author=\
        Field(
            __name__="author",
            __type__=Author,
            __doc__="""Author of this comparison / validation. If a group has
            authored, please create a group used as author.""")
    phenomenon=\
        Field(
            __name__="phenomenon",
            __type__=Phenomenon,
            __doc__="""Phenomenon that was compared / validated / analyzed.""")
    figure=\
        Field(
            __name__="figure",
            __type__=object,
            __doc__="A plot figure")
    caption=\
        Field(
            __name__="caption",
            __type__=str,
            __doc__="Caption to go with the plot")
    is_pass=\
        Field(
            __name__="is_pass",
            __type__=bool,
            __default__=False,
            __doc__="""True if the model's predictions comparable to
            the reference.""")
    is_fail=\
        Field(
            __name__="is_fail",
            __type__=bool,
            __default__=False,
            __doc__="""True if the model's predictions are not comparable to
            the reference. If neither pass, nor fail, the comparison is
            considered inconclusive.""")
    pvalue=\
        Field(
            __name__="pvalue",
            __type__=float,
            __default__=0.0,
            __doc__="""P-value for observing the model measurement, compared 
           against the reference data.""")

    def __init__(self,
            *args, **kwargs):
        """..."""
        template=\
            kwargs.get("template")
        if template is kwargs:
            self.template=\
                kwargs["template"]
        else:
            template_loc=\
                kwargs.get(
                    "template_loc",
                    os.path.join(
                        os.path.dirname(__file__),
                        "templates",
                        "report.cheetah"))
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
        ---------------
        output_dir_path :: String #directory to save report in.
        report_file_name :: String #name of the file to save report in

        Implementation Notes
        ---------------------
        Try to create a (html) string using its class' template and save
        to the disc. If this fails, call "'Report._save_default."""

        output_dir_path=\
            self.get_output_location(
                output_dir_path=output_dir_path)
        file_name_base=\
            utils.get_file_name_base(
                report_file_name)
        report_file_name=\
            file_name_base + ".html"
        plot_file_name=\
            file_name_base + ".png"
        report_file_path=\
            os.path.join(
                output_dir_path,
                report_file_name)
        plot_file_path=\
            os.path.join(
                output_dir_path,
                plot_file_name)
        self.logger.info(
            self.logger.get_source_info(),
            "Saving report to {} ".format(
                report_file_path))
        self.logger.info(
            self.loggr.get_source_info(),
            "Generating {}".format(
                plot_file_path))
        self.figure.savefig(
            plot_file_path,
            dpi=100)
        try:
            temmplate_dict=\
                self.__report_dict__
            template_dict.update(dict(
                image_name=plot_file_name,
                phenomenon=self.phenomenon.name,
                author_name=self.author.name,
                author_affiliation=self.author.affiliation))
            report_template=\
                Template(
                    self.template,
                    searchList=template_dict)
            try:
                report_html=\
                    str(report_template)
            except Exception as ex_html:
                raise Exception(
                    """EXCEPTION!!! While generating html: {}.\n""".format(
                        ex_html))
            with open(report_file_path, 'w') as report_file:
                report_file.write(report_html)

            return report_file_path

        except Exception as ex:
            self.logger.alert(
                """WARNING!!!
                While loading the template {}.
                Will proceed to save a text report.""".format(ex))
            return self._save_default(
                output_dir_path,
                file_name_base)
