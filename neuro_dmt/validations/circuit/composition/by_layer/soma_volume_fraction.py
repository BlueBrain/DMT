"""Validation of cell density by layer."""
from dmt.model.interface import Interface
from dmt.vtk.phenomenon import Phenomenon
from neuro_dmt.validations.circuit.composition.by_layer \
    import ByLayerCompositionValidation

class SomaVolumeFractionValidation(ByLayerCompositionValidation):
    """Cell density validation is a 'unit' test case for a circuit model.
    Cell density is a spatial composition phenomenon.
    We assume that all measurements are made by region in the brain,
    and require that from measurements made on the circuit model."""

    validated_phenomenon = Phenomenon(
        "volume fraction",
        "Fraction of volume occupied by neurons in a unit volume."
    )

    class AdapterInterface(Interface):
        """All methods listed here must be implemented by an adapter for this
        interface."""

        def get_label(self, circuit_model):
            """Get a label for the circuit model.

            Parameters
            --------------------------------------------------------------------
            circuit_model :: ModelCircuit
            """
            pass

        def get_soma_volume_fraction(self, circuit_model):
            """Get cell density for a circuit.
            This method must be defined for the model adapter class that will
            adapt a circuit model to the requirements of this validation.
            
            Parameters
            --------------------------------------------------------------------
            circuit_model :: ModelCircuit
            
            Return
            --------------------------------------------------------------------
            Record(phenomenon :: Phenomenon, #that was measured
            ~      label :: String, #used as label for the measurement
            ~      region_label :: String, #label for regions in data
            ~      data :: DataFrame["region", "mean", "std"],
            ~      method :: String)
            """
            pass

     
    def get_measurement(self, circuit_model):
        """Get measurement of the phenomenon validated."""
        return self.adapter.get_soma_volume_fraction(circuit_model)
