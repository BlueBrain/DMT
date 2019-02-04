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


class ConnectomeAnalysis(
        BrainCircuitAnalysis):
    """Analyze a single connectome phenomenon."""

    pathway_parameters=\
        Field(
            __name__ = "pathway_parameters",
            __typecheck__ = Field.typecheck.collection(
                BrainCircuitConnectomeParameter),
            __doc__ = """A connectome phenomenon must be measured as a
            function of either cell-type (for example mtype) or a
            cell-type --> cell-type pathway. Most often we will use mtype
            as cell-type.""")
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
            *args, **kwargs):
        """Initialize Me"""
        super().__init__(
            *args, **kwargs)
