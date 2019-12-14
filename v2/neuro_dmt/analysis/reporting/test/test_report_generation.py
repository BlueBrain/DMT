from collections.abc import Mapping
import numpy as np
from matplotlib import pyplot as plt
import pytest as pyt
from dmt.tk.reporting import Report
from dmt.tk.plotting import golden_figure
from dmt.tk.plotting.figure import Figure
from ..import CircuitAnalysisReport, CheetahReporter


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
    plt.plot(
        range(100),
        np.cumsum(np.random.uniform(size=100)))
    report =\
        CircuitAnalysisReport(
            introduction="""
            This is an introduction.
            A single paragraph can have lines ending in at most a single endline
            marker. If you insert two line breaks, such as follows

            a new paragraph should start...
            """,
            animal="Not Defined",
            age="Not Defined",
            brain_region="Not Defined",
            uri="Not Defined",
            figures={
                "random_walk_1": Figure(
                    figure,
                    caption="""
                    Random Walk
                    ================
                    Each random walk step size is uniformly drawn from [0, 1).
                    The individual steps are added up cummulatively to obtain
                    the location of the walk at a given time.
                    """)})
    reporter =\
        CheetahReporter("random_walks")
    reporter.post(report)
