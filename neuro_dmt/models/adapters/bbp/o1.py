"""Adapters for BBP circuits, using the bluepy API.

Guidelines
--------------------------------------------------------------------------------
As a first proof-of-principle we will implement assuming an O1.v6a circuit.
However, we may want to add another level of indirection to abstract away this
detail.

The Circuit type has changed drastically over past years, however if were
to use 'bluepy.api.Circuit' as a type for all of them, we will rely on manual
book-keeping to organize all the different adapters.

A proxy object, a wrapper for BBP circuits is thus necessary. We can use a
factory method to determine which kind of a Circuit we are dealing with and
set that as the """
from dmt.aii import interface, adapter

from bluepy.api import Circuit
from neuro_dmt.validations.circuit.composition.by_layer.\
    cell_density import CellDensityValidation
from neuro_dmt.validations.circuit.composition.by_layer.\
    cell_ratio import CellRatioValidation
from neuro_dmt.validations.circuit.composition.by_layer.\
    inhibitory_synapse_density import InhibitorySynapseDensityValidation
from neuro_dmt.validations.circuit.composition.by_layer.\
    synapse_density import SynapseDensityValidation


@adapter.adapter(Circuit)
@interface.implementation(CellDensityValidation.AdapterInterface)
@interface.implementation(CellRatioValidation.AdapterInterface)
@interface.implementation(InhibitorySynapseDensityValidation.AdapterInterface)
@interface.implementation(SynapseDensityValidation.AdapterInterface)
class BBPCircuitAdapter:
    """Adapt a circuit from the Blue Brain Project.
    Move code from previous attempts at ValidationFramework."""

    @classmethod
    def get_cell_density(cls, circuit_model):
        """Implement this!"""
        raise NotImplementedError

    @classmethod
    def get_cell_ratio(cls, circuit_model):
        """Implement this!"""
        raise NotImplementedError

    @classmethod
    def get_inhibitory_synapse_density(cls, circuit_model):
        """Implement this!"""
        raise NotImplementedError

    @classmethod
    def get_synapse_density(cls, circuit_model):
        """Implement this!"""
        raise NotImplementedError
