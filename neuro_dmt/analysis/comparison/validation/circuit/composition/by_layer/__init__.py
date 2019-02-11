"""Validations for circuit composition by layer.
Validations defined here, (module 'by_layer') apply to any brain region
that has layers."""

from dmt.vtk.utils.descriptor\
    import Field\
    ,      document_fields
from dmt.vtk.utils.collections\
    import Record
from neuro_dmt.analysis.comparison.circuit.composition.by_layer\
    import ByLayerCompositionComparison
from neuro_dmt.analysis.circuit.composition.by_layer \
    import CellDensityAnalysis\
    ,      CellRatioAnalysis\
    ,      InhibitorySynapseDensityAnalysis\
    ,      SynapseDensityAnalysis
from neuro_dmt.analysis.comparison.validation.circuit\
    import CircuitPhenomenonValidationTestCase


@document_fields
class ByLayerCompositionValidation(
        CircuitPhenomenonValidationTestCase,
        ByLayerCompositionComparison):
    """Validation of a single circuit composition phenomenon.
    Validation is against reference data that provide experimental data
    as a function of layer. This base class may be used for validation
    composition of any brain region that is composed of layers.
    """
    pass


class CellDensityValidation(
        ByLayerCompositionValidation,
        CellDensityAnalysis):
    """..."""
    pass


class CellRatioValidation(
        ByLayerCompositionValidation,
        CellRatioAnalysis):
    """..."""
    pass


class InhibitorySynapseDensityValidation(
        ByLayerCompositionValidation,
        InhibitorySynapseDensityAnalysis):
    """..."""
    pass


class SynapseDensityValidation(
        ByLayerCompositionValidation,
        SynapseDensityAnalysis):
    """..."""
    pass
