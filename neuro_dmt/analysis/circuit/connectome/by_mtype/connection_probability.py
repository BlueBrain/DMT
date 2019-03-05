"""Analyze connection probabilty by mtype -> mtype pathway."""
from dmt.model.interface\
    import Interface
from dmt.vtk.phenomenon\
    import Phenomenon
from neuro_dmt.analysis.circuit.connectome.by_mtype\
    import ByMtypePathwayConnectomeAnalysis


class PathwayConnectionProbabilityAnalysis(
        ByMtypePathwayConnectomeAnalysis):
    """Analyze probability of connections by mytpe --> mtype pathway."""

    def __init__(self,
            *args, **kwargs):
        """Initialize me."""
        super().__init__(
            Phenomenon(
                "Pathway Connection Probability",
                "Probability of connections in an mtype --> mtype pathway.",
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

        def get_pathway_connection_probability(self,
                circuit_model,
                parameters=[],
                *args, **kwargs):
            """Get statistical summary of the number of synapses between
            pre- and post-synaptic cells in an mtype --> mtype pathway.
            This method must be defined for the model adapter class that will
            adapt a circuit model to the requirements of this analysis.

            Parameters
            -------------------
            circuit_model :: ModelCircuit
            parameters :: provides the pathways for which synapse counts
            ~             are to be computed. For eg. [pre_mtype, post_mtype]

            Return
            -------------------
            Record[
            ~   phenomenon :: Phenomenon,
            ~   data :: DataFrame<pre_mtype, post_mtype>["mean", "std"]
            ~           #a dataframe with a pre/post mtypes in index
            ~   method :: String #describe how the computation]
            """
            pass


    def get_measurement(self,
            circuit_model,
            *args, **kwargs):
        """Get a (statistical) measurement  of the phenomenon analyzed."""
        return\
            self.adapter\
                .get_pathway_connection_probability(
                    circuit_model,
                    parameters=self.measurement_parameters,
                    *args, **kwargs)
