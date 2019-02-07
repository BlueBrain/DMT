"""Analyze synapse count by mtype --> mtype pathway."""
from dmt.model.interface\
    import Interface
from dmt.vtk.phenomenon\
    import Phenomenon
from neuro_dmt.analysis.circuit.connectome.by_mtype\
    import ByMtypeConnectomeAnalysis

class PairSynapseCountAnalysis(
        ByMtypeConnectomeAnalysis):
    """Analyze synapse count by mtype --> mtype pathway."""

    def __init__(self,
            *args, **kwargs):
        """Initialize me."""
        super().__init__(
            Phenomenon(
                "Pair Synapse Count",
                "Number of cells in an mtype --> mtype pathway",
                group="connectome"),
            *args, **kwargs)


    class AdapterInterface(
            Interface):
        """All methods listed here must be implemented by an adapter for
        the analyzed circuit (class)."""
        def get_label(self,
                circuit_model):
            """Get a label for the circuit model.

            Parameters
            ------------------
            circuit_model :: ModelCircuit
            """
            pass

        def get_pathway_synapse_count(self,
                circuit_model,
                parameters=[]):
            """Get statistical summary of the number of synapses between
            pre- and post-synaptic cells in an mtype --> mtype pathway.
            This method must be defined for the model adapter class that will
            adapt a circuit model to the requirements of this analysis.

            Parameters
            -------------------
            circuit_model :: ModelCircuit
            pathway_parameter :: provides the pathways for which synapse counts
            ~                    are to be computed.

            Return
            -------------------
            Record[
            ~   phenomenon :: Phenomenon,
            ~   data :: DataFrame<pre_mtype, post_mtype>["mean", "std"]
            ~           #a dataframe with a pre/post mtypes in index
            ~   method :: String #describe how synapse counts were computed]
            """
            pass

    def plot(self,
            model_measurement,
            *args, **kwargs):
        """We implement a plot method here while we develop ConnectomeAnalysis.
        Once all wrinkles have been smoothed, we will abstract this plot to
        a vtk.plotting."""




    def get_measurement(self,
            circuit_model,
            *args, **kwargs):
        """Get a (statistical) measurement  of the phenomenon analyzed."""
        return\
            self.adapter\
                .get_pathway_synapse_count(
                    circuit_model,
                    parameters=self.pathway_parameters)
