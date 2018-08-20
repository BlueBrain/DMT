"""Adapters for O1 (v5 and v6a) circuits from the Blue Brain Project.
These adapters leverage the bluepy API.

Guidelines
--------------------------------------------------------------------------------
As a first proof-of-principle we will implement assuming an O1.v6a circuit.
However, we may want to add another level of indirection to abstract away this
detail.
The Circuit type has changed drastically over past years, however if we 
use 'bluepy.v2.circuit.Circuit' as a type for all of them, we will rely on 
manual book-keeping to organize all the different adapters.
"""
from dmt.aii import interface, adapter

from bluepy.v2.circuit import Circuit
from neuro_dmt.validations.circuit.composition.by_layer.\
    cell_density import CellDensityValidation
from neuro_dmt.validations.circuit.composition.by_layer.\
    cell_ratio import CellRatioValidation
from neuro_dmt.validations.circuit.composition.by_layer.\
    inhibitory_synapse_density import InhibitorySynapseDensityValidation
from neuro_dmt.validations.circuit.composition.by_layer.\
    synapse_density import SynapseDensityValidation
from neuro_dmt.models.bluebrain import geometry, cell_collection, utils


@adapter.adapter(Circuit)
@interface.implementation(CellDensityValidation.AdapterInterface)
@interface.implementation(CellRatioValidation.AdapterInterface)
@interface.implementation(InhibitorySynapseDensityValidation.AdapterInterface)
@interface.implementation(SynapseDensityValidation.AdapterInterface)
class BlueBrainModelAdapter:
    """Adapt a circuit from the Blue Brain Project (BBP).
    This adapter was developed for the O1.v6a models developed at BBP in 2017-
    2018. The brain (micro-)circuit models are not atlas based, but are
    organized as hexagonal columns, while respecting the connectivity patterns
    observed in real brain circuits.
    """

    @classmethod
    def get(cls, circuit, target='mc2_Column'):
        cells = circuit.

    @classmethod
    def get_cell_density(cls, circuit):
        """Implement this!"""
        return geometry.collect_sample(
            measurement=circuit.stats.cell_density,
            region_to_explore=
        )
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


