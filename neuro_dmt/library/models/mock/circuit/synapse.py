# Copyright (C) 2020 Blue Brain Project / EPFL

# This file is part of BlueBrain DMT <https://github.com/BlueBrain/DMT>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License version 3.0 as published by the 
# Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with
# DMT source-code.  If not, see <https://www.gnu.org/licenses/>. 

"""
Deifinitions and methods for synapses in a MockCircuit.
"""
from collections import Mapping
import numpy as np
import pandas as pd
from dmt.tk.field import Field, Property, WithFields, lazy
from .composition import CircuitComposition

class Synapse(WithFields):
    """
    Defines a synapse, and documents it's (data) fields.
    This class is mostly for documenting and learning purposes.
    """

    pre_gid = Field(
        """
        Pre-synaptic cell's GID.
        """,
        __type__=(int, np.integer))
    post_gid = Field(
        """
        Post-synaptic cell's GID.
        """,
        __type__=(int, np.integer))

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
        SYN2
        -------------------------
        The synapse type id as used in the recipe.

        NRN
        -------------------------
        Inhibitory < 100 or Excitatory >= 100
        (specific value corresponds to the generating recipe.)
        """,
        __required__=False)

    n_rrp_vesicles = Field(
        """
        Number of readily releasable pool of vesicles.
        """,
        __type__=(int, np.integer),
        __required__=False)
    @property
    def NRRP(self):
        """
        NRN label for n_rrp_vesicles
        """
        return self.n_rrp_vesicles

    morpho_branch_order_post = Field(
        """
        Order of the dendritic tree branch on which this synapse is located.
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
        SYN2
        -------------------------
        The section if of the touched segment associated with the post-synaptic
        neuron. The ID comes associated with the morphology model.
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
        The id of the touched (by this synapse) segment associated with the
        post-synaptic neuron. The ID comes associated with the morphology
        model.
        """,
        __type__=(int, np.integer),
        __required__=False)

    afferent_section_pos = Field(
        """
        Sonata
        ---------------------------
        Given the section of where a synapse is placed on the target node, the
        position along the length of that section (normalized to the range
        [0,1], where 0 is at the start of the section and 1 is at the end.)
        """,
        __type__=(float, np.float),
        __required__=False)

    morpho_offset_segment_post = Field(
        """
        Given the section and the segment of where a synapse is placed on the
        target node, the offset further localizes the synapse on the
        target node morphology.
        """,
        __required__=False)

    morpho_branch_order_pre = Field(
        """
        Order of the axonal tree branch on which this synapse is located.
        """,
        __required__=False)
    @property
    def pre_branch_order(self):
        """
        NRN label for morpho_branch_order_pre
        """
        return self.morpho_branch_order_pre

    morpho_section_id_pre = Field(
        """
        Syn2
        ---------------------
        The section id of the touched segment associated with the pre-synaptic
        neuron. The ID comes associated with the morphology model.
        """,
        __required__=False)
    @property
    def pre_section_id(self):
        """
        NRN label for morpho_section_id_pre
        """
        return self.morpho_section_id_pre

    morpho_segment_id_pre = Field(
        """
        The id of the touched (by this synapse) segment associated with the
        pre-synaptic neuron. The ID comes associated with the morphology model.
        """,
        __type__=(int, np.integer),
        __required__=False)

    efferent_section_pre = Field(
        """
        Sonata
        --------------------------
        Given the section of where a synapse is placed on the source node, the
        position along the length of that section (normalized to the range
        [0,1], where 0 is the start of the section and 1 is a the end.)
        """,
        __required__=False)

    morpho_offset_segment_pre = Field(
        """
        Given the section and the segment of where a synapse is placed on the
        source node, the offset further localizes the synapse on the
        source node morphology.
        """,
        __required__=False)

    efferent_center_x = Field(
        """
        Sonata
        ----------------
        For edges that represent synapses in morphologically detailed networks,
        this attribute specifies 'x' position in network global spatial
        coordinates of the synapse along the axon axis of the pre-synaptic
        neuron. For synapses on the soma this location is at the soma center
        """,
        __required__=False)
    @property
    def pre_x_center(self):
        """
        NRN label for efferent_center_x
        """
        return self.efferent_center_x

    efferent_center_y = Field(
        """
        Sonata
        ----------------
        For edges that represent synapses in morphologically detailed networks,
        this attribute specifies 'y' position in network global spatial
        coordinates of the synapse along the axon axis of the pre-synaptic
        neuron. For synapses on the soma this location is at the soma center
        """,
        __required__=False)
    @property
    def pre_y_center(self):
        """
        NRN label for efferent_center_y
        """
        return self.efferent_center_y

    efferent_center_z = Field(
        """
        Sonata
        ----------------
        For edges that represent synapses in morphologically detailed networks,
        this attribute specifies 'z' position in network global spatial
        coordinates of the synapse along the axonal axis of the pre-synaptic
        neuron. For synapses on the soma this location is at the soma center
        """,
        __required__=False)
    @property
    def pre_z_center(self):
        """
        NRN label for efferent_center_z
        """
        return self.efferent_center_z

    afferent_center_x = Field(
        """
        Sonata
        ----------------
        For edges that represent synapses in morphologically detailed networks,
        this attribute specifies 'x' position in network global spatial
        coordinates of the synapse along the dendrite axis of the post-synaptic
        neuron. For synapses on the soma this location is at the soma center
        """,
        __required__=False)
    @property
    def post_x_center(self):
        """
        NRN label for afferent_center_x
        """
        return self.afferent_center_x

    afferent_center_y = Field(
        """
        Sonata
        ----------------
        For edges that represent synapses in morphologically detailed networks,
        this attribute specifies 'y' position in network global spatial
        coordinates of the synapse along the dendrite axis of the post-synaptic
        neuron. For synapses on the soma this location is at the soma center
        """,
        __required__=False)
    @property
    def post_y_center(self):
        """
        NRN label for afferent_center_y
        """
        return self.afferent_center_y

    afferent_center_z = Field(
        """
        Sonata
        ----------------
        For edges that represent synapses in morphologically detailed networks,
        this attribute specifies 'z' position in network global spatial
        coordinates of the synapse along the dendrite axis of the post-synaptic
        neuron. For synapses on the soma this location is at the soma center
        """,
        __required__=False)
    @property
    def post_z_center(self):
        """
        NRN label for afferent_center_z
        """
        return self.afferent_center_z

    efferent_surface_x = Field(
        """
        Same as efferent_center_x, but for the synapse location on the axon
        surface.
        """,
        __required__=False)
    @property
    def pre_x_contour(self):
        """
        NRN label for efferent_surface_x
        """
        return self.efferent_surface_x

    afferent_surface_x = Field(
        """
        Same as 'afferent_center_x', but for the synapse location on the soma or
        dendrite surface.
        """,
        __required__=False)
    @property
    def post_x_contour(self):
        """
        NRN label for afferent_surface x
        """
        return self.afferent_surface_x

    efferent_surface_y = Field(
        """
        Same as efferent_center_y, but for the synapse location on the axon
        surface.
        """,
        __required__=False)
    @property
    def pre_y_contour(self):
        """
        NRN label for efferent_surface_y
        """
        return self.efferent_surface_y

    afferent_surface_y = Field(
        """
        Same as 'afferent_center_y', but for the synapse location on the soma or
        dendrite surface.
        """,
        __required__=False)
    @property
    def post_y_contour(self):
        """
        NRN label for afferent_surface y
        """
        return self.afferent_surface_y

    efferent_surface_z = Field(
        """
        Same as efferent_center_z, but for the synapse location on the axon
        surface.
        """,
        __required__=False)
    @property
    def pre_z_contour(self):
        """
        NRN label for efferent_surface_z
        """
        return self.efferent_surface_z

    afferent_surface_z = Field(
        """
        Same as 'afferent_center_z', but for the synapse location on the soma or
        dendrite surface.
        """,
        __required__=False)
    @property
    def post_z_contour(self):
        """
        NRN label for afferent_surface z
        """
        return self.afferent_surface_z


class SynapseCollection(WithFields):
    """
    A collection of synapses that stores synapses.
    SynapseCollection builds on pandas DataFrame to store data
    in memory, and provides an efficient secondary index on the stored data.
    If there are two many synapses to store in memory, SynapseCollection will
    respond to queries by loading the data from disk.

    """
    adjacency = Field(
        """
        List of 2-tuples holding connected cell gid and synapse count.
        """)
    direction = Field(
        """
        Direction of the connections in 'adjacency' data.
        """)
