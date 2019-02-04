"""Circuit composition data for the cortex."""
from neuro_dmt.data.bluebrain.circuit\
    import BlueBrainCircuitCompositionData\
    ,      BlueBrainCircuitConnectomeData
from neuro_dmt.utils\
import brain_regions
from neuro_dmt.measurement.parameter\
    import CorticalLayer


class CortexCompositionData(
        BlueBrainCircuitCompositionData):
    """Nothing here for the moment. 
    For now the purpose of this class to exist is to be a node in the class
    hierarchy for Blue Brain reference data classes."""
    pass


class CortexConnectomeData(
        BlueBrainCircuitConnectomeData):
    """Nothing here for the moment. 
    For now the purpose of this class to exist is to be a node in the class
    hierarchy for Blue Brain reference data classes."""
    pass
