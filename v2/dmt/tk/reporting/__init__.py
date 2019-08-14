"""
Tools for reporting analysis results.
"""

from abc import ABC, abstractmethod
import os
from dmt.tk.field import Field, lazyproperty, WithFields
from dmt.tk.plotting.figure import Figure

class Report(WithFields):
    """
    Report base class.
    We follow the principle of IMRAD (Introduction, Methods, Results, and
    Discussion: https://en.wikipedia.org/wiki/IMRAD  )
    """
    figures = Field(
        """
        A dict mapping label to an object with a `.graphic` and `.caption`
        attributes.
        """)
    measurement = Field(
        """
        Measurement associated with this `Report`. This should be a dataframe,
        with a properly annotated index.
        """,
        __required__=False)
    introduction = Field(
        """
        Provide the research question, and the tested hypothesis or the
        purpose of the research?
        """,
        __default_value__="Not provided")
    methods = Field(
        """
        Describe the algorithm / procedure used to compute the results
        or the experimental measurement presented in this `Report`. This
        `Field` will be used in the figure caption.
        """,
        __default_value__="Not provided")
    results = Field(
        """
        Answer to the research question, to be included in the figure caption.
        """,
        __default_value__="Not provided")
    discussion = Field(
        """
        A longer text describing how the results presented in the report fit
        in the existing knowledge about the topic.
        What might the answer imply and why does it matter? How does it fit in
        with what other researchers have found? What are the perspectives
        for future research?
        """,
        __default_value__="Not provided")


    pass


class Reporter(WithFields):
    """
    Abstract base class.
    A `Reporter` will be able to process reports.
    """

    path_output_folder = Field(
        """
        Path to the output folder.
        """,
        __default_value__=os.getcwd())

    def get_output_folder(self,
            path_output_folder=None):
        """
        Create the folder if it does not exist.
        """
        path_output_folder = path_output_folder\
            if path_output_folder else\
               self.path_output_folder

        if not os.path.exists(path_output_folder):
            os.makedirs(path_output_folder)

        return path_output_folder

    def get_figures_folder(self,
            path_output_folder=None):
        """
        Get a folder that will contain figures for a report.
        """
        output_folder = self\
            .get_output_folder(
                path_output_folder=path_output_folder)
        path_figures_folder = os.path\
            .join(output_folder, "figures")
        if not os.path.exists(path_figures_folder):
            os.makedirs(path_figures_folder)

        return path_figures_folder

    def save(self,
            report,
            path_output_folder=None):
        """
        Save report at the path provided.
        """
        output_folder = self.get_output_folder(path_output_folder)
        figures_folder = self.get_figures_folder(output_folder)

        def __write(output_file, attribute, text=""):
            section_end = 70 *'-'
            underline = len(attribute) * '-'
            output_file.write(
                "{}\n{}\n{}\n{}\n".format(
                    attribute.upper(),
                    underline,
                    text if text else getattr(report, attribute),
                    section_end))

        with open(os.path.join(output_folder, "report.txt"), 'w') as output_file:
            __write(
                output_file, "introduction")
            __write(
                output_file, "methods")
            __write(
                output_file, "results")
            __write(
                output_file, "discussion")
            __write(
                output_file, "figures", figures_folder)
            __write(
                output_file, "figure captions",
                "\n".join(
                    "({}). {}".format(label, figure.caption)
                    for label, figure in report.figures.items()))

        try:
            report.measurement.to_csv(
                os.path.join(
                    output_folder, "measurement.csv"))
        except AttributeError:
            pass

        for label, figure in report.figures.items():
            figure.save(
                os.path.join(
                    figures_folder,
                    label)
                , dpi=100)

        return output_folder


    def post(self,
            report,
            *args, **kwargs):
        """
        Behavior of a `Reporter` is defined by how it posts a report.
        A `Reporter` may post to a website, to a database, or simply
        save to a folder on the harddisk.

        The default behavior is to save the report to the disk as a text file
        and a figure file.
        """
        return self.save(report, *args, **kwargs)
