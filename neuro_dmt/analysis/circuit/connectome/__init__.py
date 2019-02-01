"""Analysis of a circuit's connectome."""

import os
from dmt.vtk.utils.descriptor\
    import Field\
    ,      document_fields
from neuro_dmt.analysis.circuit\
    import BrainCircuitAnalysis
from neuro_dmt.measurement.parameter\
    import BrainCircuitConnectomeParameter
from neuro_dmt.models.bluebrain.circuit.parameters\
    import Mtype\
    ,      PreMtype\
    ,      PostMtype


class ConnectomeAnalysis(
        BrainCircuitAnalysis):
    """Analyze a single connectome phenomenon."""
    pathway_parameters=\
        Field(
            __name__="pathway_parameters",
            __typecheck__=Field.typecheck.collection(
                BrainCircuitConnectomeParameter),
            __doc__="""To measure pathway properties of a circuit connectome
            you will need to specify how the pathway is defined.""",
            __default__=[PreMtype, PostMtype])
    cell_group_parameters=\
        Field(
            __name__="cell_group_parameters",
            __typecheck__=Field.typecheck.collection(
                BrainCircuitConnectomeParameter),
            __doc__="""Parameters to measure groups of cell in the circuit.""",
            __default=[Mtype])

    def __init__(self,
            *args, **kwargs):
        """Initialize Me"""
        super().__init__(
            *args, **kwargs)
