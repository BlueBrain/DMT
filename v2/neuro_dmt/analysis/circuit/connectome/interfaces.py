"""
Adapter interfaces that document what is required of adapters to use
our suite of analyses.
"""

from dmt.model.interface import Interface

class SynapsesPerConnectionAdapterInterface(Interface):
    """
    This class documents the methods that must be adapted for your circuit
    model to use analyses of synapses per connection.
    """
    __measurement__ = "synapses_per_connection"

    def get_label(self,
            circuit_model):
        """
        A label that can be used to name a pandas.DataFrame column.
        """
        raise NotImplementedError

    def get_mtypes(model):
        """
        get all of the mytpes in the model
        Arguments:
            model: the model to get mtypes from
            
        Returns:
            iterable of mtypes (string)
        """
        raise NotImplementedError

    def get_synapses_per_connection(model, pre_mtype, post_mtype):
        """
        get the number of synapses per connection from the model
        for the pathway defined be pre and post mtyp
        
        Arguments:
            model: the model to get the data from
            pre_mtype: string, the presynaptic mtype
            post_mtype: string, the postsynaptic mtype
            
        Returns:
            Array: number of synapses for each connection sampled
        """
        raise NotImplementedError

