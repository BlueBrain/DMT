"""Validations of the circuit connectome, by mtype."""

from dmt.vtk.utils.descriptor\
    import Field\
    ,      document_fields
from neuro_dmt.analysis.comparison.circuit.connectome.by_mtype\
    import ByMtypeConnectomeComparison
from neuro_dmt.analysis.circuit.connectome.by_mtype\
    import PairSynapseCountAnalysis
from neuro_dmt.analysis.comparison.validation.circuit\
    import CircuitPhenomenonValidationTestCase


@document_fields
class ByMtypeConnectomeValidation(
        CircuitPhenomenonValidationTestCase,
        ByMtypeConnectomeComparison):
    """Validation of a single circuit-connectome-phenomenon.
    Validation is against reference data that provide experimental data as
    function of mtype."""
    pass

class PairSynapseCountValidation(
        ByMtypeConnectomeValidation,
        PairSynapseCountAnalysis):
    """..."""
    pass
