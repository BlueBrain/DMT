"""Circuit composition data for the cortex."""

from neuro_dmt.data.bluebrain.circuit import BlueBrainCircuitCompositionData


class CortexCompositionData(BlueBrainCircuitCompositionData):
    """Nothing here for the moment. 
    For now the purpose of this class to exist is to be a node in the class
    hierarchy for Blue Brain reference data classes."""

    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(*args, **kwargs)
