"""Logic for validation of circuit composition."""

from Cheetah.Template import Template
from dmt.vtk.reporting import Report
from dmt.vtk.utils.exceptions import RequiredKeywordArgumentError

class CompositionReport(Report):
    """A class to be used to report all of our composition validations.
    The html produced by the Cheetah Template used here will display a plot for
    the validation, with a caption, metadata about the authors and their
    affiliation, and the status of the validation.

    Notes
    ----------------------------------------------------------------------------
    Associated Cheetah template must be placed  in a directory named templates
    in the same directory as this file.
    """

    def __init__(self, *args, **kwargs):
        """We explicitly check for the required fields in 'kwargs',
        this acts as both documentation and a run-time help system."""
        

    __template_loc__ = os.path.join(os.path.dirname(__file__),
                                    "templates",
                                    "validation_with_plot.cheetah")



class CompositionTestCase:
    """Code that is common to composition validation test cases,
    irrespective of how the composition is measured."""
    pass


