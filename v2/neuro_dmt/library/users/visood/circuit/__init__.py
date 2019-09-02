"""
Blue brain circuit model.
"""
import numpy
import bluepy
from dmt.tk import collections
from dmt.tk.field import WithFields, lazyfield, Field

class BlueBrainCircuitModel(WithFields):
    """
    Circuit model developed at the Blue Brain Project.
    """
    label = Field(
        """
        A label to represent your circuit model instance.
        """,
        __default_value__="BlueBrainCircuitModel")
