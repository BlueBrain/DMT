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

class MouseSSCxConnectomeData(
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
        return list(cls.get_available_data().keys())

    @classmethod
    def get_available_data(cls,
            phenomenon=None):
        """..."""
        from neuro_dmt.data.bluebrain.circuit.mouse.\
            cortex.sscx.connectome.connection_probability\
            import MouseSSCxConnectionProbability
        available={
            "pathway_connection_probability": MouseSSCxConnectionProbability}
        return\
            available[getattr(phenomenon, "label", phenomenon)]\
            if phenomenon else available
