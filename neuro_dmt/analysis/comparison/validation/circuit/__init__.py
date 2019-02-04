"""Validation of a  circuit phenomenon."""

from dmt.data.reference\
    import MultiReferenceData
from dmt.analysis.comparison.validation.test_case\
    import ValidationTestCase
from dmt.vtk.utils.descriptor\
    import Field
from dmt.vtk.judgment.verdict\
    import Verdict
from neuro_dmt.analysis.comparison.validation.report.single_phenomenon\
    import ValidationReport


class CircuitPhenomenonValidationTestCase(
        ValidationTestCase):
    """Mixin for validations of a single circuit--phenomenon.
    Validation is against a reference data that provide experimental data
    as a function of mtypes. This base class may be used for any validation
    by mtype (or pair of mtypes representing a pre --> post synapse pathway.)
    """
    reference_data=\
        Field(
            __name__ = "reference_data",
            __type__ = MultiReferenceData,
            __doc__  = """If not provided, assume validation does not use
            reference data.""")

    def __init__(self,
            phenomenon,
            *args, **kwargs):
        """...
        """
        super().__init__(
            phenomenon,
            *args, **kwargs)

    def get_report(self,
            model_measurement):
        """Create a report."""
        figure=\
            self.plot(
                model_measurement)
        pval=\
            self.pvalue(
                model_measurement)
        verdict=\
            self.get_verdict(
                pval)
        return\
            ValidationReport(
                phenomenon = self.phenomenon,
                author = self.author,
                caption = self.get_caption(model_measurement),
                reference_datasets = self.reference_datasets,
                is_pass = verdict == Verdict.PASS,
                is_fail = verdict == Verdict.FAIL,
                pvalue = pval,
                figure = figure)
                    
