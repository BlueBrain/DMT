""""Analysis of a circuit's connectome."""

import os
from dmt.vtk.utils.descriptor\
    import Field\
    ,      document_fields
from neuro_dmt.analysis.circuit\
    import BrainCircuitAnalysis
from neuro_dmt.models.bluebrain.circuit.parameters\
    import Mtype\


class ConnectomeAnalysis(
        BrainCircuitAnalysis):
    """Analyze a single connectome phenomenon."""
    pass
