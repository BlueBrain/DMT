"""Utilities for circuit composition by layer.
Validations defined here, (module 'by_layer') apply to any brain region
that has layers."""

from dmt.data.reference import MultiReferenceData
from dmt.analysis.validation.test_case import ValidationTestCase
from dmt.vtk.utils.descriptor import Field, document_fields
from dmt.vtk.judgment.verdict import Verdict
from dmt.vtk.utils.collections import Record
from dmt.vtk.measurement.parameter.group import ParameterGroup
from neuro_dmt.analysis.comparison.circuit.composition.by_layer\
    import ByLayerCompositionComparison
from neuro_dmt.analysis.comparison.validation.\
    circuit.composition.by_layer.report \
    import ValidationReport
from neuro_dmt.analysis.circuit.composition import SpatialCompositionAnalysis
from neuro_dmt.analysis.circuit.composition.by_layer import\
    CellDensityAnalysis,\
    CellRatioAnalysis,\
    InhibitorySynapseDensityAnalysis,\
    SynapseDensityAnalysis


@document_fields
class ByLayerCompositionValidation(
        ValidationTestCase,
        ByLayerCompositionComparison):
    """Validation of a single circuit composition phenomenon.
    Validation is against reference data that provide experimental data
    as a function of layer. This base class may be used for validation
    composition of any brain region that is composed of layers."""

    reference_data=\
        Field(
            __name__="reference_data",
            __type__=MultiReferenceData,
            __doc__="""If not provided, assume validation does not use
            reference data""")

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
        figure = self.plot(model_measurement)
        pval = self.pvalue(model_measurement)
        verdict = self.get_verdict(pval)
        return ValidationReport(
            phenomenon=self.phenomenon,
            author=self.author,
            caption=self.get_caption(model_measurement),
            reference_datasets=self.reference_datasets,
            is_pass=verdict == Verdict.PASS,
            is_fail=verdict == Verdict.FAIL,
            pvalue=pval,
            figure=figure)



class CellDensityValidation(
        ByLayerCompositionValidation,
        CellDensityAnalysis):
    """..."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args, **kwargs)

class CellRatioValidation(
        ByLayerCompositionValidation,
        CellRatioAnalysis):
    """..."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args, **kwargs)

class InhibitorySynapseDensityValidation(
        ByLayerCompositionValidation,
        InhibitorySynapseDensityAnalysis):
    """..."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args, **kwargs)

class SynapseDensityValidation(
        ByLayerCompositionValidation,
        SynapseDensityAnalysis):
    """..."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args, **kwargs)
