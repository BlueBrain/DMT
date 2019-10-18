"""
Neuroscience terminology used.
"""
from dmt.tk.terminology import *
from dmt.tk.utils.singleton import Singleton


class TermCollection(Singleton):
    """
    A collection of terms.
    """
    @classmethod
    def make_query(cls, **kwargs):
        """
        Make a query from key-word arguments.
        """
        return {
            label: kwargs[label]
            for label in cls.terms
            if label in kwargs}

    @classmethod
    def filter(cls, **query):
        """
        Filter all the query entries that have value `None`.
        """
        return {
            label: value
            for label, value in query.items()
            if label in cls.terms and value is not None}

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
    terms =(
        region,
        layer,
        depth,
        mesocolumn,
        hypercolumn)


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
    terms =(
        mtype,
        etype,
        synapse_class,
        postsynaptic,
        presynaptic)


class synapse(TermCollection):
    """
    A collection of terms used in neuroscience.
    """
    afferent = Term(
        "afferent",
        "An afferent synapse, or connection, enters a cell.")
    efferent = Term(
        "efferent",
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
