"""
Neuroscience terminology used.
"""
from dmt.tk.terminology import *
from dmt.tk.utils.singleton import Singleton


class circuit(Singleton):
    """
    A collection of terms used in neuroscience.
    """
    region = Term(
        "region",
        "A region / area in the brain.")
    layer = Term(
        "layer",
        "A structure in certain brain areas, such as the cortex")
    depth = Term(
        "depth",
        "Depth into a brain region, measured absolutely.")
    height = Term(
        "height",
        "Height into a brain region, measured absolutely.")
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


class cell(Singleton):
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


class synapse(Singleton):
    """
    A collection of terms used in neuroscience.
    """
    afferent = Term(
        "afferent",
        "An afferent synapse, or connection, enters a cell.")
    efferent = Term(
        "efferent",
        "An efferent synapse, or connection exits a cell.")



