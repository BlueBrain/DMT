"""Test develop MultiReference Data"""

from neuro_dmt.data.bluebrain.circuit.mouse.cortex.sscx.composition\
    import MouseSSCxCompositionData

cell_density_data=\
    MouseSSCxCompositionData.get(
        "cell_density")
