"""
The connectome of a circuit.
"""

from dmt.tk.field import Field, WithFields

class CircuitConnectome(WithFields):
    """
    The connectome of a circuit.
    """
    afferent_adjacency = Field(
        """
        List of afferent cell gids for each  cell in a circuit.
        We can build other connectome properties from this list.
        """)

