""""Data for the circuit connectome of Rat Somatosensory cortex."""

import os
import pickle
import numpy as np
import pandas as pd
from dmt.vtk.phenomenon\
    import Phenomenon
from dmt.vtk.utils.descriptor\
    import Field
from dmt.vtk.utils.collections\
    import Record
from neuro_dmt.data.bluebrain.circuit.cortex.sscx.connectome\
    import SSCxConnectomeData

class RatSSCxConnectomeData(
        SSCxConnectomeData):
    """..."""

    data_location=\
        Field.Optional(
            __name__ = "data_location",
            __type__ = dict,
            __typecheck__=Field.typecheck.mapping(str, str),
            __doc__="A dict{str: str} that maps dataset label to its location")

    def __init__(self,
            phenomenon,
            *args, **kwargs):
        """..."""
        super().__init__(
            animal = "rat",
            phenomenon=phenomenon,
            *args, **kwargs)

    @classmethod
    def get_available_data_keys(cls):
        """A list of keys (labels) for available data."""
        return list(cls.data().keys())

    @classmethod
    def get_available_data(cls,
            phenomenon=None):
        from neuro_dmt.data.bluebrain.circuit.rat.\
            cortex.sscx.connectome.pair_synapse_count\
            import RatSSCxPairSynapseCountData
        from neuro_dmt.data.bluebrain.circuit.rat.\
            cortex.sscx.connectome.bouton_density\
            import RatSSCxBoutonDensity
        from neuro_dmt.data.bluebrain.circuit.rat.\
            cortex.sscx.connectome.connecton_proabability\
            import RatSSCxConnectionProbability
        from neuro_dmt.data.bluebrain.circuit.rat.\
            cortex.sscx.connectome.inhibitory_synapses_on_soma\
            import RatSSCxInhibitorySynapsesOnSomaData
        available={
            "pair_synapse_count": RatSSCxPairSynapseCountData,
            "pathway_connection_count": RatSSCxConnectionProbability,
            "pathway_connection_probability": RatSSCxConnectionProbability,
            "bouton_density": RatSSCxBoutonDensity}
        return\
            available[getattr(phenomenon, "label", phenomenon)]\
            if phenomenon else available
