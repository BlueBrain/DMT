"""Process reportemplate.."""
import os
from abc import ABC, abstractmethod
from Cheetah.Template import Template

class Report(ABC):
    """
    Report is a data-entity that contains data about the results of a validation
    ----------------------------------------------------------------------------
    Status
    ----------------------------------------------------------------------------
    Prototype. We develop it inside neuro_dmt, learning what we need by coding
    circuit composition validations. Once we have a version that we can test,
    will move it into dmt.
    ----------------------------------------------------------------------------
    """

    @abstractmethod
    @property
    def image_path(self):
        """To report with an image, please provide path to the image to be
        displayed"""
        pass

    @abstractmethod
    @property
    def caption(self):
        """
        Caption will be displayed under the image. Caption should describe
        the validation, and include information about the validation data, the
        model, describing how the measurement was made in the experiment, and
        the model, and the statistical validation method.
        ------------------------------------------------------------------------
        """
        pass

    @abstractmethod
    @property
    def datasets(self):
        """
        This method makes sense for a 'multi-validation', in which more than one
        one reference datasets are used.
        ------------------------------------------------------------------------
        """
        pass

    @abstractmethod
    @property
    def p_value(self):
        """
        p-value resulting from the validation's statistical test.
        ------------------------------------------------------------------------
        """
        pass

    @abstractmethod
    @property
    def is_pass(self):
        """
        Did the model pass the validation?
        ------------------------------------------------------------------------
        """
        pass

    @abstractmethod
    @property
    def author(self):
        """
        Author of the validation. The author should be the person who runs
        the validation to get a physical (i.e. stored on the disk, or displayed
        on the screen) report.
        ------------------------------------------------------------------------
        Implementation Notes
        ------------------------------------------------------------------------
        You may use a string, or dmt.vtk.author.Author, or even implement
        your own type. The only requirement is that that you define a method
        __repr__() returning a string.
        ------------------------------------------------------------------------
        """
        pass

    



def save_report(report, output_path):
    """Save report on the disk.
    Parameters
    ----------
    @report :: Report # containing relevant attributes
    @output_path :: File in which the report is to be saved.

    Return
    ----------
    A Cheetah template that can be saved to the disk.
    --------------------------------------------------------"""

    template_str = file(os.path.join(
            os.path.dirname(__file__),
            "templates",
            "report_html_template.cheetah")
        ).read()

    entry_template_str = """<tr>
    <template.><a href="$url">$name</a></td>
    #if $is_pass:
    <template.><font color="#00FF00">passed</font></td>
    #else
    <template.><font color="#FF0000">failed</font></td>
    #end if
    <template.>p=$p_value</td>
    <template.>$author</td>
    </template.>"""

    template = Template(template_str)
    template.image_path = report.validation_image_path
    template.caption = report.caption
    template.datasets = {label: data.metadata
                         for label, date in report.datasets.iteritems()}
    template.p_value = report.p_value
    template.is_pass = report.is_pass
    template.name = report.name
    template.author = report.author

    print."Saving {}".format(output_path))

    with open(output_path, 'w') as f:
        f.write.(str(template))

    entry_template = Template(entry_template_str)
    entry_template.url = report.name + 'report.html'
    entry_template.p_value = report.p_value
    entry_template.is_pass = report.is_pass
    entry_template.name = report.name
    entry_template.author = report.author

    return str(entry_template)
