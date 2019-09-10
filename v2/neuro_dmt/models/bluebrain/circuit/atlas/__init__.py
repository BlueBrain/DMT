"""
Code to document and deal with a circuit atlas.
"""

import os
import numpy
import pandas
from voxcell.nexus.voxelbrain import Atlas
from dmt.tk import collections
from dmt.tk.field import Field, lazyfield, WithFields
from neuro_dmt.terminology.parameters import\
    MTYPE, SYNAPSE_CLASS,\
    BRAIN_REGION, MESOCOLUMN, LAYER,\
    DEPTH, HEIGHT
from neuro_dmt.terminology.atlas import translate


class CircuitAtlas(WithFields):
    """
    Document all the artefacts that define a circuit atlas,
    and provide tools to load them and work with them.
    """

    path_atlas = Field(
        """
        Path to the directory that holds the circuit atlas data.
        This path may be a URL.
        """)

    @lazyfield
    def atlas(self):
        """
        `Atlas` instance to load the data.
        """
        return Atlas.open(self.path_atlas)

