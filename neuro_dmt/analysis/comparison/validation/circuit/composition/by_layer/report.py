"""Report by layer composition validations."""

import os
from dmt.vtk.utils.descriptor import Field
from neuro_dmt.analysis.comparison.circuit.composition.by_layer.report\
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
    
    def __init__(self, *args, **kwargs):
        """initialize!"""
        super().__init__(
            *args, **kwargs)
