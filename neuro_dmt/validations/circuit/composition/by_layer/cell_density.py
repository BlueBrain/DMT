"""Validation of cell density by layer."""
from dmt.aii.interface import Interface
from dmt.vtk.phenomenon import Phenomenon
from neuro_dmt.validations.circuit.composition.by_layer \
    import ByLayerCompositionValidation
from neuro_dmt.utils.brain_region import CorticalLayer

class CellDensityValidation(ByLayerCompositionValidation):
    """Cell density validation is a 'unit' test case for a circuit model.
    Cell density is a spatial composition phenomenon.
    We assume that all measurements are made by region in the brain,
    and require that from measurements made on the circuit model."""
    validated_phenomenon  = Phenomenon(
        "cell density",
        "Count of cells in a unit volume."
    )
    region_type = CorticalLayer
    class AdapterInterface(Interface):
        """All methods listed here must be implemented by an adapter for this
        interface.
        """
        def get_label(self, circuit_model):
            """Get a label for the circuit model.

            Parameters
            --------------------------------------------------------------------
            circuit_model :: ModelCircuit
            """
            pass

        def get_cell_density(self, circuit_model):
            """Get volume density of (neuronal) cells in a circuit.
            This method must be defined for the model adapter class that will
            adapt a circuit model to the requirements of this validation.
            
            Parameters
            --------------------------------------------------------------------
            circuit_model :: ModelCircuit
            
            Return
            --------------------------------------------------------------------
            Record(phenomenon :: Phenomenon, #that was measured
            ~      region_label :: String, #label for regions in data
            ~      data :: DataFrame["region", "mean", "std"],
            ~      method :: String)
            """
            pass

     
    def get_measurement(self, circuit_model):
        """Get measurement of the phenomenon validated."""
        return self.adapter.get_cell_density(circuit_model)
