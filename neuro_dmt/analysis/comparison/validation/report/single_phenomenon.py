"""Report by layer composition validations."""

import os
from dmt.vtk.utils.descriptor\
    import Field
from Cheetah.Template\
    import Template
from dmt.vtk.reporting\
    import Report
from dmt.vtk.utils.exceptions\
    import RequiredKeywordArgumentError
from dmt.vtk.utils.descriptor\
    import Field
from dmt.vtk.phenomenon\
    import Phenomenon
from dmt.vtk.author\
    import Author
from dmt.vtk.utils.utils\
    import get_file_name_base
from neuro_dmt.analysis.comparison.report.single_phenomenon\
    import ComparisonReport

class ValidationReport(
        ComparisonReport):
    """A class to be used to report all of our composition validations.
    The html produced by the Cheetah Template used here will display a plot for
    the validation, with a caption, metadata about the authors and their
    affiliation, and the status of the validation.

    Notes
    ----------------------------------------------------------------------------
    Associated Cheetah template must be placed  in a directory named templates
    in the same directory as this file."""

    reference_datasets=\
        Field(
            __name__ = "reference_datasets",
            __type__ = dict,
            __doc__ = """List of metadata, one element for each dataset used 
            by the validation. Please take a look at documentation of the
            validation.""")

    def __init__(self,
            *args, **kwargs):
        """initialize!"""
        self.logger.debug(
            self.logger.get_source_info(),
            "Create a validation report with attributes from \n {}".format(
                kwargs))
        if "template_location" not in kwargs:
            kwargs["template_location"]=\
                os.path.join(
                    os.path.dirname(__file__),
                    "templates",
                    "report.cheetah")
        super().__init__(
            *args, **kwargs)
