"""
Adapter for the mock BBP circuit.
"""

import numpy
import pandas
from dmt.model import interface, adapter
from dmt.tk.field import WithFields, Field, lazyproperty
from .circuit import MockCircuit
from neuro_dmt.analysis.circuit.composition.interfaces\
    import CellDensityAdapterInterface


@interface.implements(CellDensityAdapterInterface)
@adapter.adapts(MockCircuit)
class MockCircuitAdapter(WithFields):
    """
    A mock adapter for a mock circuit.
    """

    def get_cell_density(self,
            mock_circuit_model,
            *args, **kwargs):
        """
        A mock value!
        """
        return numpy.random.uniform(0., 100000.)
            
