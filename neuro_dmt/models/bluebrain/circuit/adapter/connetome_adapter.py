"""An adapter specialized to compute connectome properties efficiently."""

from neuro_dmt.models.bluebrain.circuit.adapter\
    import BlueBrainModelAdapter

class BlueBrainModelConnectomeAdapter(
        BlueBrainModelAdapter):
    """BlueBrainModelAdapter specialized for the connectome,
    for efficiency."""


    def get_pathway_synapse_count(self,
            circuit_model,
            parameters=[],
            *args, **kwargs):
        """Get statistics for number of synapse in a connection."""

