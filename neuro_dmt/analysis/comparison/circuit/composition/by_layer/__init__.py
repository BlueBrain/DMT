"""Compare model phenomena by layer."""
from dmt.analysis.comparison\
    import ModelComparison
from neuro_dmt.analysis.circuit.composition.by_layer\
    import ByLayerCompositionAnalysis
from dmt.vtk.utils.descriptor import Field, document_fields
from neuro_dmt.analysis.circuit.composition.by_layer import\
    ByLayerCompositionAnalysis,\
    CellDensityAnalysis,\
    CellRatioAnalysis,\
    InhibitorySynapseDensityAnalysis,\
    SynapseDensityAnalysis

@document_fields
class ByLayerCompositionComparison(
        ModelComparison):
    """..."""

    def __init__(self,
            phenomenon,
            *args, **kwargs):
        """..."""
        super().__init__(
            phenomenon,
            *args, **kwargs)

class CellDensityComparison(
        ByLayerCompositionComparison,
        CellDensityAnalysis):
    """..."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args, **kwargs)

class CellRatioComparison(
        ByLayerCompositionComparison,
        CellRatioAnalysis):
    """..."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args, **kwargs)

class InhibitorySynapseDensityComparison(
        ByLayerCompositionComparison,
        InhibitorySynapseDensityAnalysis):
    """..."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args, **kwargs)

class SynapseDensityComparison(
        ByLayerCompositionComparison,
        SynapseDensityAnalysis):
    """..."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            *args, **kwargs)
