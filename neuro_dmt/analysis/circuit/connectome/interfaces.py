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

    def get_pathways(self,
            circuit_model,
            cell_group):
        """
        Get pathways between cell groups 

        Arguments
        ---------------
        cell_group : An object that specifies cell groups.
        ~   This may be 
        ~   1. Either a frozen-set of strings that represent cell properties.
        ~   2. Or, a mapping from cell properties to their values.

        Returns
        ------------
        pandas.DataFrame with nested columns, with two columns 
        `(pre_synaptic, post_synaptic)` at the 0-th level.
        Under each of these two columns should be one column each for
        the cell properties specified in the `cell_group` when it is a
        set, or its keys if it is a mapping.
        ~   1. When `cell_group` is a set of cell properties, pathways between
        ~      all possible values of these cell properties.
        ~   2. When `cell-group` is a mapping, pathways between cell groups
        ~      that satisfy the mapping values.
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
            pre_synaptic_cell_type,
            post_synaptic_cell_type):
        """
        Get connection probability of a pathway.

        Arguments
        --------------
        pre/(post)_synaptic_cell_type: A mapping of cell property to its value.
        ~                              The two mappings defines the cell type 
        ~                              on the afferent, and efferent sides of
        ~                              a synapse.
        """
        raise NotImplementedError


class ConnectionProbabilityBySomaDistanceInterface(PathwayPropertyInterface):
    """
    Documents the methods that must be adapted for your circuit model
    to use connection probability by soma-distance analyses.
    """
    __measurement__ = "connection_probability_by_soma_distance"

    def get_connection_probability_by_soma_distance(self,
            circuit_model,
            pre_synaptic,
            post_synaptic,
            soma_distance_bins):
        """
        Get connection probability of a pathway, by distance between the somas
        of the afferent and efferent cells in a pathway pair.

        Arguments
        --------------
        pre/(post)_synaptic_cell_type: A mapping of cell property to its value.
        ~                              The two mappings defines the cell type 
        ~                              on the afferent, and efferent sides of
        ~                              a synapse.
        soma_distance_bins : A list of two-tuples in which the soma distance
        ~                    between afferent, efferent cells.
        """
        raise NotImplementedError


class AfferentConnectionCountInterface(PathwayPropertyInterface):
    """
    Documents the methods that must be adapted for your circuit model
    to afferent connection count analyses.
    """
    __measurement__ = "afferent_connection_count_summary"

    def get_afferent_connection_count_summary(self,
            circuit_model,
            post_synaptic,
            pre_synaptic_cell_type_specifier=None):
        """
        Get number of afferent connections by distance between the somas
        of the afferent and efferent cells in a pathway pair.

        Arguments
        --------------
        post_synaptic_cell_type: A mapping of cell property to its value.
        ~                        The mapping defines the cell type on the
        ~                        efferent side of a synapse.
        pre_synaptic_cell_type_specifier :  A set of cell property names
        ~                        that will be used to group pre-synaptic cells
        ~                        to count afferent counts from.
        ~                        If not provided, keys of the argument
        ~                        `post_synaptic_cell_type` should be used.
        """
        raise NotImplementedError

   
class AfferentConnectionCountBySomaDistanceInterface(PathwayPropertyInterface):
    """
    Documents the methods that must be adapted for your circuit model
    to use connection probability by soma-distance analyses.
    """
    __measurement__ = "number_connections_afferent_by_soma_distance"

    def get_number_connections_afferent_by_soma_distance(self,
            circuit_model,
            pre_synaptic,
            post_synaptic,
            soma_distance_bins):
        """
        Get number of afferent connections by distance between the somas
        of the afferent and efferent cells in a pathway pair.

        Arguments
        --------------
        pre/(post)_synaptic_cell_type: A mapping of cell property to its value.
        ~                              The two mappings defines the cell type 
        ~                              on the afferent, and efferent sides of
        ~                              a synapse.
        soma_distance_bins : A list of two-tuples in which the soma distance
        ~                    between afferent, efferent cells.
        """
        raise NotImplementedError



class ConnectomeAdapterInterface(ConnectionProbabilityInterface):
    """
    Combines individual connectome measurement interfaces.
    """
    pass


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
