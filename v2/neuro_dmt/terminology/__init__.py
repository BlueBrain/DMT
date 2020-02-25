"""
Neuroscience terminology used.
"""
from enum import Enum
from bluepy.v2.enums import Cell, Synapse
from dmt.tk.terminology import *
from dmt.tk.utils.singleton import Singleton



class circuit(TermCollection):
    """
    A collection of terms used in neuroscience.
    """
    region = Term(
        "region",
        """
        1. Either a region / area in the brain represented by a string,
        2. or a two-tuple of 3D numpy arrays or list providing corners of a box.
        """)
    layer = Term(
        "layer",
        "A structure in certain brain areas, such as the cortex")
    mesocolumn  = Term(
        "mesocolumn",
        """
        Organizational structure of model brain circuits that corresponds
        to cortical columns. A meso-column is a collection of micro-column.
        """)
    hypercolumn = Term(
        "hypercolumn",
        """
        Used at BBP, probably the same as a meso-column.
        """)
    roi = Term(
        "roi", 
        """
        Region of interest packaged as a bounding-box or a type
        that will return a bounding-box on invocation of `.bbox`.
        """)
    class atlas(TermCollection):
        """
        Terminology relevant to, specific to, or to be used with
        a circuit atlas.
        """
        depth = Term(
            "depth",
            "Depth into a brain region, measured absolutely.")
        height = Term(
            "height",
            "Height into a brain region, measured absolutely.")
        
        terms = (
            depth,
            height)


    depth = atlas.depth
    height = atlas.height

    spatial_terms =(
        region,
        layer,
        depth,
        height,
        mesocolumn,
        hypercolumn)
    terms =(
        region,
        layer,
        depth,
        height,
        mesocolumn,
        hypercolumn,
        roi)

    @classmethod
    def get_spatial_query(cls, query_dict):
        """
        Extract spatial parameters and their values from a `query_dict`.
        """
        return {
            parameter: value
            for parameter, value in query_dict.items()
            if parameter in cls.spatial_terms and value is not None}


class cell(TermCollection):
    """
    A collection of terms used in neuroscience.
    """
    mtype = Term(
        "mtype",
        "Label assigned to cells to mark their morphology.")
    etype = Term(
        "etype",
        "Label assigned to cells to mark their electro-physiology.")
    synapse_class = Term(
        "synapse_class",
        "Synapse class of a cell can be either excitatory, or inhibitory")
    postsynaptic = Term(
        "postsynaptic",
        """
        The value of this parameter should describe,
        the postsynaptic cell group of a pathway.
        """)
    presynaptic = Term(
        "presynaptic",
        """
        The value of this parameter should describe,
        the presynaptic cell group of a pathway.
        """)
    morphology_class = Term(
        "morphology_class",
        "the morphology class of a cell, either pyramidal or interneuron.")
    morphology_subclass = Term(
        "morphology_subclass",
        """
        the specific form of morphology, e.g. MC or CHC.
        """)
    terms =(
        mtype,
        etype,
        synapse_class,
        postsynaptic,
        presynaptic)
    afferent = Term(
        "AFF",
        """
        Use this term to refer to cells whose outputs enter a synapse.
        """)
    efferent = Term(
        "EFF",
        """
        Use this term to refer to cells that receive their input from a
        synapse --- a.k.a post-synaptic neuron
        """)


class synapse(TermCollection):
    """
    A collection of terms used in neuroscience.
    """
    post_gid = Synapse.POST_GID
    pre_gid = Synapse.PRE_GID
    afferent = Term(
        "AFF",
        "An afferent synapse, or connection, enters a cell.")
    efferent = Term(
        "EFF",
        "An efferent synapse, or connection exits a cell.")
    terms =(
        afferent,
        efferent)


class measurement_method(TermCollection):
    """
    Tags for measurement methods
    """
    random_sampling = Term(
        "random_sampling",
        """
        Measure a phenomenon by randomly sampling
        measurement parameters.
        """)
    exhaustive = Term(
        "exhaustive",
        """
        Measure a phenomenon by iterating exhaustively
        over the measurement parameters""")

    terms =(
        random_sampling,
        exhaustive)


class sampling_methodology(TermCollection):
    """
    Enum specifying how to sample a population.
    """
    random = Term(
        "random",
        """
        Take random samples from the population.
        The function making the measurement will also need the number
        of individuals to collect in the sample.
        """)
    exhaustive = Term(
        "exhaustive",
        """
        Use the entire population as the sample.
        """)


class processing_methodology(TermCollection):
    """
    Enum specifying / indicating how to process a sample.
    """
    serial = Term(
        "one",
        """
        Indicate to process one individual from the population at a time.
        """)
    batch = Term(
        "batch",
        """
        Indicate to process a batch of individuals from the population at a
        time.
        """)


class direction(TermCollection):
    """
    Direction of transmission across a synapse (for-example).
    """
    forward = Term(
        "FORWARD",
        "From pre-synaptic neuron to post-synaptic neuron.")
    reverse = Term(
        "REVERSE",
        "From post-synaptic neuron to pre-synaptic neuron.")

    random = 1
    exhaustive = 2


class bluepy(Singleton):
    """
    Terms defined in BluePy enums
    """
    class cell_columns(TermCollection):
        """Terms found in bluepy.enums.Cell"""
        morphology = Term(
            "morphology",
            "Morphology of the cell.")
        me_combo = Term(
            "me_combo",
            "Mtype, etype combination of the cell.")
        mtype = Term(
            "mtype",
            "Label for the cell morphology.")
        etype = Term(
            "etype",
            "Label for the cell electrophisiology type.")
        layer = Term(
            "layer",
            "Layer where the cell is located.")
        region = Term(
            "region",
            "Brain region where the cell is located")
        hypercolumn = Term(
            "hypercolumn",
            "In O1 circuits hypercolumn in which the cell is located.")
        minicolumn = Term(
            "minicolumn",
            "In O1 circuits minicolumn in which is the cell is located")
        morph_class = Term(
            "morph_class",
            "Class of the cell's morphology type.")
        synapse_class = Term(
            "synapse_class",
            "Class of the cell's synapses.")
        x = Term(
            "x",
            "X component of the cell's position.")
        y = Term(
            "y",
            "Y component of the cell's position.")
        z = Term(
            "z",
            "Z component of the cell's position.")
        orientation = Term(
            "orientation",
            "A matrix representing the cell's orientation.")


        terms =(
            morphology,
            me_combo,
            mtype,
            etype,
            layer,
            region,
            hypercolumn,
            minicolumn,
            morph_class,
            synapse_class,
            x, y, z,
            orientation)
