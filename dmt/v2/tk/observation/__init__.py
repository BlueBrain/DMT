"""
Prototypes and documentation to help us develop Observation

"""

from ..field import Field, WithFields
from ..quantity import Quantity

class Observation(WithFields):
    """
    Observation of a phenomenon
    """

    phenomenon = Field(
        """
        Phenomenon observed.
        """,
        __type__=Phenomenon)
    result = Field(
        """
        
        """)
