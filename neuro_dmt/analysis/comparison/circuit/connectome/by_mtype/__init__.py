"""Compare circuit connectome phenomena by mytpe."""
from dmt.vtk.utils.collections\
    import Record
from dmt.vtk.utils.descriptor\
    import Field\
    ,      document_fields
from dmt.vtk.plotting.comparison\
    import ComparisonPlot\
    ,      CrossPlotComparison
from neuro_dmt.analysis.comparison.report.single_phenomenon\
    import ComparisonReport
from neuro_dmt.analysis.comparison.circuit\
    import CircuitPhenomenonComparison
from neuro_dmt.analysis.circuit.connectome.by_mtype\
    import PairSynapseCountAnalysis


@document_fields
class ByMtypeConnectomeComparison(
        CircuitPhenomenonComparison):
    """Compare two instances of a circuit connectome phenomenon that have
    been measured by mtype.
    """
    Plotter=\
        Field(
            __name__ = "Plotter",
            __typecheck__ = Field.typecheck.subtype(ComparisonPlot),
            __doc__ = """A subclass of {} to plot comparison results.""".format(
                ComparisonPlot))

    def __init__(self,
            *args, **kwargs):
        """Initialize Me, and pass on to supers..."""
        kwargs["Plotter"]=\
            kwargs.get(
                "Plotter",
                CrossPlotComparison)
        super().__init__(
            *args, **kwargs)


class PairSynapseCountComparison(
        ByMtypeConnectomeComparison,
        PairSynapseCountAnalysis):
    """..."""
    pass
