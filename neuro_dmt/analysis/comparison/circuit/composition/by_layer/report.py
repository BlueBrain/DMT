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
class ComparisonReport(
        AnalysisReport):
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
        super().__init__(
            *args, **kwargs)
