"""Validation of cell density by layer."""
from dmt.aii import Interface
from dmt.validation.single_phenomemon import SinglePhenomenonValidation
from neuro_dmt.validations.circuit.composition.by_layer \
    import CompositionPhenomenonValidation

class SynapseDensityValidation(CompositionPhenomenonValidation,
                               SinglePhenomenonValidation):
    """Cell density validation is a 'unit' test case for a circuit model.
    Cell density is a spatial composition phenomenon.
    We assume that all measurements are made by region in the brain,
    and require that from measurements made on the circuit model."""

    validated_phenomenon = Phenomenon(
        "synapse density",
        "Count of synapses in a unit volume."
    )

    class AdapterInterface(Interface):
        """All methods listed here must be implemented by an adapter for this
        interface."""
        def get_label(circuit_model):
            """Get a label for the circuit model.

            Parameters
            --------------------------------------------------------------------
            circuit_model :: ModelCircuit
            """
            pass

        def get_synapse_density(circuit_model):
            """Get volume density of synapses in a circuit.
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
        model = self.adapt(circuit_model)
        return model.get_synapse_density()
