"""
A report should be able to handle sections.
"""

import os
from collections.abc import Mapping
import numpy as np
import pandas as pd
from matplotlib import pylab as plt
from dmt.tk.author import Author
from dmt.tk.reporting import Report
from dmt.tk.plotting import golden_figure
from dmt.tk.plotting.figure import Figure
from dmt.tk.collections import Record
from dmt.tk.field import NA
from dmt.tk.utils.string_utils import make_label
from ..import CircuitAnalysisReport, CheetahReporter, CircuitProvenance

def test_post():
    """
    Reporter should be able to post a report with sections.
    """
    provenance =\
        CircuitProvenance(
            label="Test",
            authors=3*[Author.anonymous],
            date_release="XXXXXXXX",
            uri="UnknownLocation",
            animal="UnkownAnimal",
            age="UnknownAge",
            brain_region="UnknownBrainArea")

    def _section(label, subsections=NA):
        """
        Each section will generate it's own 'CircuitAnalysisReport` instance,
        just as we will implement `Report.sections` as a list of independent
        reports.
        """
        figure, axes =\
            golden_figure(14, 12)
        xs = np.linspace(0., 1., 100)
        ys = np.cumsum(np.random.uniform(size=100))
        measurement =\
            pd.DataFrame({"x": xs, "y": ys}).set_index(["x"])
        plt.plot(xs, ys)
        
        return\
            CircuitAnalysisReport(
                author=Author.anonymous,
                phenomenon="{}".format(label),
                abstract="""
                Abstract {}
                """.format(label),
                introduction="""
                Introduce {}
                """.format(label),
                methods="""
                Methods {}
                """.format(label),
                measurement=measurement,
                figures={
                    "random_walk_{}".format(label): Figure(
                        figure,
                        caption="""
                        Each random walk step size is uniformly drawn from [0, 1).
                        The individual steps are added up cummulatively to obtain
                        the location of the walk at a given time.
                        """.format(label))},
                results="""
                Results {}
                """.format(label),
                discussion="""
                Discussion {}
                """.format(label),
                references={"{}".format(label): "https://www.example.org/label".format(label)},
                sections=subsections,
                provenance_model=provenance)

    report_main =\
        _section("Composition",
                 subsections=[_section(make_label(phenomenon, separator='-'))
                              for phenomenon in ("Cell Density by Layer",
                                                 "Inhibitory Fractions by Layer",
                                                 "Mtype Cell Density by Layer",
                                                 "Fiber Density by Layer",
                                                 "Marker Density by Cortical Depth",
                                                 "Cell Density by Layer")])

    reporter =\
        CheetahReporter(
            path_output_folder=os.path.join(os.getcwd(), "random_walks"))
    path_report =\
        reporter.post(report_main)
    return\
        Record(
            provenance=provenance,
            report=report_main,
            reporter=reporter,
            path_report=path_report)
