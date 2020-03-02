import os
from collections.abc import Mapping
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import pytest as pyt
from dmt.tk.author import Author
from dmt.tk.reporting import Report
from dmt.tk.plotting import golden_figure
from dmt.tk.plotting.figure import Figure
from dmt.tk.collections import Record
from ..import CircuitAnalysisReport, CheetahReporter, CircuitProvenance


def test_template_filling():
    """
    Test that a `CheetahReporter` instance can fill a template.
    """
    report = Report(
        figures={"example": Figure(plt.axes(), caption="Not provided")})

    reporter = CheetahReporter("example_analysis")
    filled_template = reporter.filled_template(report, {"NA": "not-available"})
    assert isinstance(filled_template, Mapping), type(filled_template)

def test_post():
    """
    Reporter should be able to post the report to a location.
    """
    figure, axes =\
        golden_figure(14, 12)
    xs = np.linspace(0., 1., 100)
    ys = np.cumsum(np.random.uniform(size=100))
    measurement =\
        pd.DataFrame({"x": xs, "y": ys}).set_index(["x"])
    plt.plot(xs, ys)

    provenance =\
        CircuitProvenance(
            label="Test",
            authors=3*[Author.anonymous],
            date_release="XXXXXXXX",
            uri="UnknownLocation",
            animal="UnkownAnimal",
            age="UnknownAge",
            brain_region="UnknownBrainArea")
    report =\
        CircuitAnalysisReport(
            author=Author.anonymous,
            phenomenon="unknown",
            abstract="""
            This is an abstract.
            """,
            introduction="""
            This is an introduction.
            A single paragraph can have lines ending in at most a single endline
            marker. If you insert two line breaks, such as follows

            a new paragraph should start...
            """,
            measurement=measurement,
            figures={
                "random_walk_1": Figure(
                    figure,
                    caption="""
                    Random Walk
                    ================
                    Each random walk step size is uniformly drawn from [0, 1).
                    The individual steps are added up cummulatively to obtain
                    the location of the walk at a given time.
                    """)},
            methods="""
            Describe how.
            """,
            results="""
            Test results are good.
            """,
            discussion="""
            No need to discuss.
            """,
            references={"xyz": "https://www.xxx.yyy.zzz/qqq"},
            provenance_model=provenance)
    reporter =\
        CheetahReporter(
            path_output_folder=os.path.join(
                os.getcwd(), "random_walks"))
    path_report =\
        reporter.post(report)
    return\
        Record(
            provenance=provenance,
            report=report,
            reporter=reporter,
            path_report=path_report)

def test_dict_provenance():
    """
    Report should generate from a dict as a the provenance.
    """
    figure, axes =\
        golden_figure(14, 12)
    xs = np.linspace(0., 1., 100)
    ys = np.cumsum(np.random.uniform(size=100))
    measurement =\
        pd.DataFrame({"x": xs, "y": ys}).set_index(["x"])
    plt.plot(xs, ys)

    provenance =\
        CircuitProvenance(
            label="Test",
            authors=3*[Author.anonymous],
            date_release="XXXXXXXX",
            uri="UnknownLocation",
            animal="UnkownAnimal",
            age="UnknownAge",
            brain_region="UnknownBrainArea")
    report =\
        CircuitAnalysisReport(
            author=Author.anonymous,
            phenomenon="unknown",
            abstract="""
            This is an abstract.
            """,
            introduction="""
            This is an introduction.
            A single paragraph can have lines ending in at most a single endline
            marker. If you insert two line breaks, such as follows

            a new paragraph should start...
            """,
            measurement=measurement,
            figures={
                "random_walk_1": Figure(
                    figure,
                    caption="""
                    Random Walk
                    ================
                    Each random walk step size is uniformly drawn from [0, 1).
                    The individual steps are added up cummulatively to obtain
                    the location of the walk at a given time.
                    """)},
            methods="""
            Describe how.
            """,
            results="""
            Test results are good.
            """,
            discussion="""
            No need to discuss.
            """,
            reference="""
            No need for references.
            """,
            provenance_model=provenance.field_dict)
    reporter =\
        CheetahReporter(
            path_output_folder=os.path.join(
                os.getcwd(), "random_walks"))
    reporter.post(report)
    return Record(
        provenance=provenance,
        report=report,
        reporter=reporter)
