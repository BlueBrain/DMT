"""Test develop circuit connectome data."""

from neuro_dmt.data.bluebrain.circuit.rat.cortex.sscx.composition\
    import RatSSCxCompositionData
from neuro_dmt.data.bluebrain.circuit.rat.cortex.sscx.connectome\
    import RatSSCxConnectomeData

rat_cell_density_data=\
    RatSSCxCompositionData.get("cell_density")
rat_synapse_count_data=\
    RatSSCxConnectomeData.get("pair_synapse_count")
