"""
Tools for reporting analysis results.
"""

from abc import ABC, abstractmethod
import os
from collections.abc import Mapping
import pandas as pd
from dmt.tk.utils import timestamp
from dmt.tk.utils.string_utils import make_name
from dmt.tk.field import Field, lazyfield, WithFields, NA
from dmt.tk.author import Author
from dmt.tk.plotting.figure import Figure
from dmt.tk.utils.string_utils import paragraphs

class Report(WithFields):
    """
    Report base class.
    We follow the principle of IMRAD (Introduction, Methods, Results, and
    Discussion: https://en.wikipedia.org/wiki/IMRAD  )
    """
    author = Field(
        """
        Author of this report.
        """,
        __default_value__=Author.anonymous)
    phenomenon = Field(
        """
        Label for the phenomenon that this report is about.
        """,
        __default_value__=NA)
    figures = Field(
        """
        A dict mapping label to an object with a `.graphic` and `.caption`
        attributes.
        """,
        __default_value__=NA)
    measurement = Field(
        """
        Measurement associated with this `Report`. This should be a dataframe,
        with a properly annotated index.
        """,
        __default_value__=NA)
    introduction = Field(
        """
        Provide the research question, and the tested hypothesis or the
        purpose of the research?
        """,
        __default_value__=NA,
        __as__=paragraphs)
    methods = Field(
        """
        Describe the algorithm / procedure used to compute the results
        or the experimental measurement presented in this `Report`. This
        `Field` will be used in the figure caption.
        """,
        __default_value__=NA,
        __as__=paragraphs)
    sections = Field(
        """
        An ordered list of report sections.
        """,
        __default_value__=NA)
    results = Field(
        """
        Answer to the research question, to be included in the figure caption.
        """,
        __default_value__=NA,
        __as__=paragraphs)
    discussion = Field(
        """
        A longer text describing how the results presented in the report fit
        in the existing knowledge about the topic.
        What might the answer imply and why does it matter? How does it fit in
        with what other researchers have found? What are the perspectives
        for future research?
        """,
        __default_value__=NA,
        __as__=paragraphs)
    references = Field(
        """
        References for this analysis report.
        """,
        __default_value__=NA)

    @lazyfield
    def field_values(self):
        """..."""
        try:
            name_phenomenon = self.phenomenon.name
        except AttributeError:
            name_phenomenon = make_name(self.phenomenon, separator='_')
        return {
            "author": self.author,
            "phenomenon": name_phenomenon,
            "figures": self.figures,
            "introduction": self.introduction,
            "methods": self.methods,
            "results": self.results,
            "discussion": self.discussion,
            "references": self.references,
            "sections": self.sections}


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

    def get_output_location(self,
            report,
            path_output_folder=None,
            output_subfolder=None,
            with_time_stamp=True):
        """
        Where should the report be saved.
        Create the folder if it does not exist.
        """
        path_parent =\
            path_output_folder if path_output_folder\
            else self.path_output_folder
        if not os.path.exists(path_parent):
            os.makedirs(path_parent)
        path_report_folder =\
            os.path.join(
                path_parent,
                report.phenomenon)
        if output_subfolder is not None:
            path_report_folder =\
                os.path.join(
                    path_report_folder,
                    output_subfolder)
        if with_time_stamp:
            daytime =\
                timestamp()
            path_report_folder =\
                os.path.join(
                    path_report_folder,
                    daytime.day,
                    daytime.time)

        if not os.path.exists(path_report_folder):
            os.makedirs(path_report_folder)
        return path_report_folder

    def get_figures_location(self,
            path_output_folder):
        """
        Get a folder that will contain figures for a report.
        """
        path_figures_folder = os.path\
            .join(path_output_folder, "figures")
        if not os.path.exists(path_figures_folder):
            os.makedirs(path_figures_folder)

        return path_figures_folder

    @staticmethod
    def _flattened_columns(dataframe):
        """
        Flatten MultiIndexed columns...
        """
        return pd.DataFrame(
            dataframe.values,
            columns=pd.Index([
                '_'.join(t) if isinstance(t, tuple) else t
                for t in dataframe.columns.values]))

    def _get_file_path(self, folder_files, label_file, format_file):
        """..."""
        raise NotImplementedError(
            """Is this a stub leftover?""") 

    def _save_figures(self, report, output_folder, format_file=".png"):
        """..."""
        if format_file[0] != '.':
            format_file = '.' + format_file
        figures_folder =\
            self.get_figures_location(output_folder)
        figure_locations = {}
        for label, figure in report.figures.items():
            location =\
                os.path.join(figures_folder, "{}{}".format(label, format_file))
            figure.save(location, dpi=100)
            figure_locations[label] = location

        return (figures_folder, figure_locations)


    def _save_text_report(self, report, output_folder, folder_figures):
        """..."""
        def __write(output_file, attribute, text=""):
            section_end = 70 *'-'
            underline = len(attribute) * '-'
            output_file.write(
                "{}\n{}\n{}\n{}\n".format(
                    attribute.upper(),
                    underline,
                    text if text else getattr(report, attribute),
                    section_end))

        with open(os.path.join(output_folder, "report.txt"),'w') as output_file:
            __write(
                output_file, "introduction")
            __write(
                output_file, "methods")
            __write(
                output_file, "results")
            __write(
                output_file, "discussion")
            __write(
                output_file, "figures", folder_figures)
            __write(
                output_file, "figure captions",
                "\n".join(
                    "({}). {}".format(label, figure.caption)
                    for label, figure in report.figures.items()))

    def save(self,
            report,
            path_output_folder=None,
            output_subfolder=None,
            with_time_stamp=True):
        """
        Save report at the path provided.
        """
        output_folder =\
                self.get_output_location(
                    report,
                    path_output_folder=path_output_folder,
                    output_subfolder=output_subfolder,
                    with_time_stamp=with_time_stamp)

        folder_figures, _ =\
            self._save_figures(report, output_folder)

        self._save_measurement(report, output_folder)

        self._save_text_report(report, output_folder, folder_figures)

        for section in self.sections:
            self.save(
                section,
                path_output_folder=output_folder,
                with_time_stamp=False)

        return output_folder

    def _save_measurement(self, report, output_folder):
        """..."""
        try:
            self._flattened_columns(report.measurement.reset_index()).to_csv(
                os.path.join(
                    output_folder,
                    "{}.csv".format(report.phenomenon)))
        except AttributeError:
            pass


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
