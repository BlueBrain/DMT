"""
Deifinitions and methods for synapses in a MockCircuit.
"""
from collections import Mapping
import numpy as np
import pandas as pd
from bluepy.v2.enums improt Synapse as SynapseProperty
from dmt.tk.field import Field, Property, WithFields, lazy
from composition import CircuitComposition

class Synapse(WithFields):
    """
    Defines a synapse, and documents it's (data) fields.
    This class is mostly for documenting and learning purposes.
    """
    axonal_delay = Field(
        """
        Scholarapedia
        -------------------------
        Axonal conduction delays refer to the time
        required for an action potential to travel from its initiation site 
        near the neuronal soma to the axon terminals, where synapses are formed
        with other neurons...

        Sonata
        -------------------------
        Axonal delay when the synaptic event begins relative to a spike from
        the presynaptic source.

        NRN
        -------------------------
        Computed using the distance of the presynaptic axon to the post
        synaptic terminal.

        Units
        -------------------------
        milliseconds
        """,
        __type__=(float, np.float),
        __required__=False)
    @property
    def delay(self):
        """
        Sonata label for axonal delay.
        """
        return self.axonal_delay

    depression_time = Field(
        """
        NRN
        --------------------------
        Time constant of depression

        Units
        --------------------------
        milliseconds
        """,
        __type__=(float, np.float),
        __required__=False)
    @property
    def d_syn(self):
        """
        NRN label for synapse depression time.
        """
        return self.depression_time

    facilitation_time = Field(
        """
        NRN
        --------------------------
        Time constant of facilitation

        Units
        --------------------------
        milliseconds
        """,
        __type__=(float, np.float),
        __required__=False)
    @property
    def f_syn(self):
        """
        NRN label for synapse facilitation time.
        """
        return self.facilitation_time

    decay_time = Field(
        """
        NRN
        --------------------------
        Decay time constant

        Units
        --------------------------
        milliseconds
        """,
        __type__=(float, np.float),
        __required__=False)
    @property
    def DTC(self):
        """
        NRN label for synapse decay time.
        """
        return self.decay_time

    conductance = Field(
        """
        NRN
        --------------------------
        Conductance of the synapse

        Units
        --------------------------
        nanosiemens
        """,
        __type__=(float, np.float),
        __required__=False)
    @property
    def g_synX(self):
        """
        NRN label for conductance of the synapse
        """
        return self.conductance

    u_syn = Field(
        """
        NRN
        -------------------------
        u parameter of the TM model.
        """,
        __type__=float,
        __required__=False)

    synapse_type_id = Field(
        """
        The synapse type Inhibitory < 100 or Excitatory >= 100
        (specific value corresponds to the generating recipe.)
        """,
        __required__=False)

    n_rrp_vesicles = Field(
        """
        Number of readily releasable pool of vesicles.
        """,
        __type__=(integer, np.integer),
        __required__=False)

    morpho_branch_order_post = Field(
        """
        Branch order of the dendrite (i.e. on the post-synaptic side.)
        """,
        __required__=False)
    @property
    def post_branch_order(self):
        """
        NRN label for branch order of the dendrite.
        """
        return self.morpho_branch_order_post

    morpho_section_type_post = Field(
        """
        Branch type from the post neuron.
        (soma: 0, axon: 1, basal: 2, apical 3)
        """,
        __type__=(int, np.integer),
        __required__=False)
    @property
    def post_branch_type(self):
        """
        NRN label for branch type from the post neuron.
        """
        return self.morpho_section_type_post

    morpho_section_id_post = Field(
        """
        Specific section on the post-synaptic (dendritic) morphology
        where this synapse is placed.
        """,
        __required__=False)
    @property
    def post_section_id(self):
        """
        NRN label for morpho_section_id_post
        """
        return self.morpho_section_id_post

    morpho_segment_id_post = Field(
        """
        Given the section of where a synapse is placed on the target node, the
        position along the length of that section (normalized to the range
        [0,1], where 0 is at the start of the section and 1 is at the end.)
        Post synaptic (dendritic) segment id.
        """,
        __type__=int,
        __required__=False)

    morpho_offset_segment_post = Field(
        """
        
        """)


