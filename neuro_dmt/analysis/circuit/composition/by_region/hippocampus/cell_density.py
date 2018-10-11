"""By layer analysis of the cell density of a Hippocampus circuit."""

from dmt.model.interface import Interface
from dmt.vtk.phenomenon import Phenomenon
from neuro_dmt.analysis.circuit.composition.by_layer\
    import ByLayerCompositionAnalysis
from neuro_dmt.utils.enums import Cell

class CellCompositionAnalysis(
        ByLayerCompositionAnalysis):
    """Analysis of a circuit's cell composition."""

    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(
            Phenomenon(
                "Cell Compsition",
                "Cell counts in a unit volume.",
                group="composition"),
            *args, **kwargs)

    class AdapterInterface(Interface):
        """Methods here will be used to define this Analysis'
        measurement. All methods listed in this 'class AdapterInterface' 
        must be implemented by the analyzed model's adapter."""
        def get_label(self, circuit_model):
            """Get a label for the cirucit model.
            
            Parameters
            --------------------------------------------------------------------
            circuit_model :: ModelCircuit """
            pass

        def get_cell_density(self,
                             circuit_model,
                             spatial_parameters,
                             given={}):
            """Get volume density of (neuronal) cells in a circuit.
            This method must be defined for the model adapter class that will
            adapt a circuit model to the requirements of this validation.
            
            Parameters
            --------------------------------------------------------------------
            circuit_model :: ModelCircuit
            spatial_parameter :: SpatialParameter #that cell density be measured for
            given :: dict# providing conditions on cell properties
            Returns
            --------------------------------------------------------------------
            Record(phenomenon :: Phenomenon, #that was measured
            ~      region_label :: String, #label for regions in data
            ~      data :: DataFrame["region", "mean", "std"],
            ~      method :: String)

            Example
            --------------------------------------------------------------------
            If 'spatial_parameter' is 'CorticalLayer', the adapter should return
            cell density as a function of cortical layers in the circuit.
            """
            pass


    def get_measurement(self, circuit_model, *args, **kwargs):
        """Get measurement of the phenomenon validated."""
        pc_density\
            = self.adapter.get_cell_density(
                circuit_model,
                self.spatial_parameters,
                morph_class="PC")
        return self.adapter.get_cell_density(
            circuit_model, self.spatial_parameters)



