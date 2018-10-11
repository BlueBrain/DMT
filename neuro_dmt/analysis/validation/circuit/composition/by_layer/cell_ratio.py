"""Validation of cell density by layer."""
from dmt.model.interface import Interface
from dmt.vtk.phenomenon import Phenomenon
from neuro_dmt.analysis.validation.circuit.composition.by_layer \
    import ByLayerCompositionValidation

class CellRatioValidation(ByLayerCompositionValidation):
    """Cell density validation is a 'unit' test case for a circuit model.
    Cell density is a spatial composition phenomenon.
    We assume that all measurements are made by region in the brain,
    and require that from measurements made on the circuit model."""

    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(
            Phenomenon(
                "Cell Ratio",
                "Ratio of inhibitory to excitatory cells in a region",
                group="composition"),
            *args, **kwargs)

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

        def get_cell_ratio(self, circuit_model, spatial_parameters):
            """Get cell ratio for a circuit.
            This method must be defined for the model adapter class that will
            adapt a circuit model to the requirements of this validation.
            
            Parameters
            --------------------------------------------------------------------
            circuit_model :: ModelCircuit
            
            Return
            --------------------------------------------------------------------
            Record(phenomenon :: Phenomenon, #that was measured
            ~      label :: String, #used as label for the measurement
            ~      region_label :: String, #label for regions in data, eg layer
            ~      data :: DataFrame["mean", "std"],
            ~      method :: String)
            """
            pass

    def get_measurement(self, circuit_model, *args, **kwargs):
        """Get measurement of the phenomenon validated."""
        return self.adapter.get_cell_ratio(
            circuit_model, self.spatial_parameters)
