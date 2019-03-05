"""Analysis of bouton density, by mtype"""
from dmt.model.interface\
    import Interface
from dmt.vtk.phenomenon\
    import Phenomenon
from neuro_dmt.analysis.circuit.connectome.by_mtype\
    import ByMtypeConnectomeAnalysis

class CellBoutonDensityAnalysis(
        ByMtypeConnectomeAnalysis):
    """Analyze bouton density statistics for cells grouped by mtype."""

    def __init__(self,
            *args, **kwargs):
        """Initialize Me"""
        super().__init__(
            Phenomenon(
                "Bouton Density",
                "Number of boutons per unit length of axonic arbor of a cell.",
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
            circuit_model :: ModelCircuit"""
            pass

        def get_cell_bouton_density(self,
                circuit_model,
                parameters=[]):
            """Get statistical summary of a cell's axonal bouton density.
            This method must be defined for the model adapter class that will
            adapt a circuit model to the requirements of this analysis.

            Parameters
            -----------------
            circuit_model :: ModelCircuit
            parameters :: groups cells for which bouton densities must be
            ~             summarized


            Return
            -----------------
            Record[
            ~    phenomenon :: Phenomenon
            ~    data :: DataFrame<cell_group>["mean", "std"]
            ~    method :: String #describe the computation]
            """
            pass


    def get_measurement(self,
            circuit_model,
            *args, **kwargs):
        """Get a (statistical) measurement of the phenomenon analyzed"""
        return\
            self.adapter\
                .get_cell_bouton_density(
                    circuit_model,
                    parameters=self.measurement_parameters,
                    *args, **kwargs)


