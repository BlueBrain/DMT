"""
Configuration of a Blue Brain Circuit Model.
"""

from dmt.tk.field import Field, lazyfield, WithFields

class CircuitConfig(WithFields):
    """
    Holds the configuration of a Blue Brain Circuit Model.
    """
    path_circuit = Field(
        """
        Absolute path to the directory that holds the circuit.
        This path must be provided for circuits on the local disk.
        """,
        __default_value__="not-available")
    uri_circuit = Field(
        """
        Universal Resource Identifier for the circuit.
        """,
        __required__=False)
