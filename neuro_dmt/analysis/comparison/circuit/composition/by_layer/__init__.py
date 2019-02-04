"""Compare circuit composition phenomena by layer."""
from dmt.vtk.utils.descriptor\
    import Field, document_fields
from dmt.vtk.plotting.comparison.barplot\
    import ComparisonPlot\
    ,      BarPlotComparison
from neuro_dmt.analysis.comparison.circuit\
    import CircuitPhenomenonComparison
from neuro_dmt.analysis.circuit.composition.by_layer\
    import CellDensityAnalysis\
    ,      CellRatioAnalysis\
    ,      InhibitorySynapseDensityAnalysis\
    ,      SynapseDensityAnalysis


@document_fields
class ByLayerCompositionComparison(
        CircuitPhenomenonComparison):
    """Compare circuit composition phenomena measured by layer."""

    Plotter=\
        Field(
            __name__ = "Plotter",
            __typecheck__ = Field.typecheck.subtype(ComparisonPlot),
            __default__ = BarPlotComparison,
            __doc__ = """A subclass of {} to comparison results.""".format(
                ComparisonPlot))
    pass

       
class CellDensityComparison(
        ByLayerCompositionComparison,
        CellDensityAnalysis):
    """..."""
    pass


class CellRatioComparison(
        ByLayerCompositionComparison,
        CellRatioAnalysis):
    """..."""
    pass


class InhibitorySynapseDensityComparison(
        ByLayerCompositionComparison,
        InhibitorySynapseDensityAnalysis):
    """..."""
    pass
    

class SynapseDensityComparison(
        ByLayerCompositionComparison,
        SynapseDensityAnalysis):
    """..."""
    pass
