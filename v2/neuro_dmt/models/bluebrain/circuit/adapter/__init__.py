"""
Adapter(s) for BBP circuits.
"""

import numpy
import pandas
from bluepy.v2.circuit import Circuit as BlueBrainCircuitModel
from dmt.model import interface, adapter
from dmt.tk.field import Field, lazyfield, WithFields
from neuro_dmt.analysis.circuit.composition.interfaces import\
    CellDensityAdapterInterface
from neuro_dmt.models.bluebrain.circuit.geometry import Cuboid

@interface.implements(CellDensityAdapterInterface)
@adapter.adapts(BlueBrainCircuitModel)
class BlueBrainCircuitModelAdapter(WithFields):
    """
    Adapts BlueBrainCircuitModel to adapter interfaces.
    """

    circuit_model = Field(
        """
        The circuit model instance adapted by this `Adapter` instance.
        """,
        __type__=BlueBrainCircuitModel,
        __required__=False)

    bounding_box_size = Field(
        """
        Dimensions of the bounding box to sample regions.
        """,
        __default_value__= numpy.array(100., 100., 100.))

    def _resolve_circuit_model(self,
            circuit_model):
        """
        Resolve the circuit model to adapt.
        """
        if circuit_model:
            return circuit_model

        try:
            return self.circuit_model
        except AttributeError:
            raise AttributeError(
                """
                Attribute circuit_model was not set for this `Adapter`.
                You may still use this `Adapter` by passing a `circuit_model`
                as an argument to the methods it adapts.
                """)

    def get_cell_density(self,
            circuit_model=None,
            mtype=None,
            etype=None,
            region=None,
            layer=None):
        """
        Get cell type density for either the `circuit_model` passed as a
        parameter or `self.circuit_model`
        """
        circuit_model = self\
            ._resolve_circuit_model(
                circuit_model)
        random_position = self\
            .circuit_model\
            .atlas_helper\
            .get_random_position(
                region=region,
                layers=[layer])
        cuboid = Cuboid(
            random_position - self.bounding_box_size / 2.,
            random_position + self.bounding_box_size / 2.)
        
