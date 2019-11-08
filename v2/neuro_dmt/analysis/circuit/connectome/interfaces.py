"""
Adapter interfaces that document what is required of adapters to use
our suite of analyses.
"""

from dmt.model.interface import Interface

class PathwayPropertyInterface(Interface):
    """
    Documents methods common to all pathway property measurements.
    """
    def get_label(self, circuit_model):
        """
        A label that can be used to name a pandas.DataFrame column.
        """
        raise NotImplementedError

    def get_mtypes(self, circuit_model):
        """
        All mtypes in a circuit model.
        """
        raise NotImplementedError

    def get_pathways(self, cell_type_specifier):
        """
        Get pathways between cell groups 

        Arguments
        ---------------
        cell_type_specifier : An object that specifies cell groups.
        Examples:
        1. A tuple of strings representing cell properties. When each tuple is
        coupled with a value, the resulting key-value pairs specify a
        group of neurons in the circuit.
        2. ?

        Returns
        --------------
        pandas DataFrame.
        """
        raise NotImplementedError


class ConnectionProbabilityInterface(PathwayPropertyInterface):
    """
    Documents the methods that must be adapted for your circuit model
    to use connection probability analyses.
    """
    __measurement__ = "connection_probability"

    def get_connection_probability(self,
            circuit_model,
            pre_mtype,
            post_mtype,
            consider_connection=lambda pre, post: True):
        """
        Get connection probability of a mtype-->mtype pathway.
        """
        raise NotImplementedError


class ConnectomeAdapterInterface(ConnectionProbabilityInterface):
    """
    Combines individual connectome measurement interfaces.
    """
    pass
