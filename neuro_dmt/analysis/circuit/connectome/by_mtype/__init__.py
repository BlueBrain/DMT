"""Measure a circuit's connectome grouping cells by their mtypes."""

from dmt.analysis\
    import OfSinglePhenomenon
from dmt.vtk.utils.collections\
    import Record
from dmt.vtk.utils.descriptor\
    import  Field, document_fields
from dmt.vtk.measurement.parameter.group\
    import ParameterGroup
from neuro_dmt.analysis.circuit.connectome\
    import ConnectomeAnalysis
from neuro_dmt.analysis.report.single_phenomenon\
    import AnalysisReport

class ByMtypeConnectomeAnalysis(
        OfSinglePhenomenon,
        ConnectomeAnalysis):
    """Measure a circuit's connectome grouping cells by their mtypes."""
    def __init__(self,
            phenomenon,
            *args, **kwargs):
        """..."""
        super().__init__(
            phenomenon,
            *args, **kwargs)


from neuro_dmt.analysis.circuit.connectome.by_mtype.synapse_count\
    import PairSynapseCountAnalysis
