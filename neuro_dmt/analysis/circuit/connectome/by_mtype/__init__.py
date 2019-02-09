"""Measure a circuit's connectome grouping cells by their mtypes."""

from dmt.analysis\
    import OfSinglePhenomenon
from dmt.vtk.utils.collections\
    import Record
from dmt.vtk.utils.descriptor\
    import  Field, document_fields
from dmt.vtk.measurement.parameter.group\
    import ParameterGroup
from dmt.vtk.plotting\
    import Plot\
    ,      HeatMap
from neuro_dmt.measurement.parameter\
    import BrainCircuitConnectomeParameter
from neuro_dmt.analysis.circuit.connectome\
    import ConnectomeAnalysis
from neuro_dmt.analysis.report.single_phenomenon\
    import AnalysisReport


class ByMtypeConnectomeAnalysis(
        OfSinglePhenomenon,
        ConnectomeAnalysis):
    """Measure a circuit's connectome grouping cells by their mtypes.
    """
    cell_group_parameters=\
        Field(
            __name__ = "cell_group_parameters",
            __typecheck__ = Field.typecheck.collection(
                BrainCircuitConnectomeParameter),
            __doc__ = """A connectome phenomenon must be measured as a
            function of either cell-type (for example mtype) or a
            cell-type --> cell-type pathway. Most often we will use mtype
            as cell-type.""")

    def __init__(self,
            phenomenon,
            *args, **kwargs):
        """..."""
        super().__init__(
            phenomenon,
            ReportType=AnalysisReport,
            *args, **kwargs)


class ByMtypePathwayConnectomeAnalysis(
        OfSinglePhenomenon,
        ConnectomeAnalysis):
    """Measure a circuit's connectome's pathway properties using
    mtypes to group pathways (pre-mtype --> post-mtype).
    """
    pathway_parameters=\
        Field(
            __name__ = "pathway_parameters",
            __typecheck__ = Field.typecheck.collection(
                BrainCircuitConnectomeParameter),
            __doc__ = """A connectome phenomenon must be measured as a
            function of either cell-type (for example mtype) or a
            cell-type --> cell-type pathway. Most often we will use mtype
            as cell-type.""")
    Plotter=\
        Field(
            __name__ = "Plotter",
            __typecheck__ = Field.typecheck.subtype(Plot),
            __default__ = HeatMap,
            __doc__ = """A subclass of {} to comparison results.""".format(
                Plot))

    def __init__(self,
            phenomenon,
            *args, **kwargs):
        """..."""
        super().__init__(
            phenomenon,
            ReportType=AnalysisReport,
            *args, **kwargs)


from neuro_dmt.analysis.circuit.connectome.by_mtype.synapse_count\
    import PairSynapseCountAnalysis
