"""Validations for the somatosensory-cortex circuit connectome of a rat."""
import os
from neuro_dmt.library.bluebrain.circuit.cortex\
    import MeasureByMtype
from neuro_dmt.library.bluebrain.circuit.cortex.sscx.connectome\
    import SomatosensoryCortexConnectomeValidation
from neuro_dmt.analysis.comparison.validation.circuit.connectome.by_mtype\
    import PairSynapseCountValidation
#from neuro_dmt.data.bluebrain.circuit.rat.cortex.sscx.connectome\
#    import RatSSCxConnectomeData


class RatSSCxPairSynapseCountValidation(
        SomatosensoryCortexConnectomeValidation,
        MeasureByMtype,
        PairSynapseCountValidation):
    """..."""
    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            animal="rat",
            reference_data=RatSSCxConnectomeData(),
            *args, **kwargs)
