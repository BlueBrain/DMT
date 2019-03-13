"""Analysis of cell density by layer."""
from dmt.model.interface import Interface
from dmt.vtk.phenomenon import Phenomenon
from neuro_dmt.analysis.circuit.composition.by_layer\
    import ByLayerCompositionAnalysis


class CellDensityAnalysis(
        ByLayerCompositionAnalysis):
    """Cell density validation is a 'unit' test case for a circuit model.
    Cell density is a spatial composition phenomenon.
    We assume that all measurements are made by layer in the brain,
    and require that from measurements made on the circuit model."""

    def __init__(self, *args, **kwargs):
        """..."""
        super().__init__(
            Phenomenon(
                "Cell Density",
                "Count of cells in a unit volume",
                group="composition"),
            *args, **kwargs)

    class AdapterInterface(
            Interface):
        """All methods listed here must be implemented by an adapter for this
        interface.
        """
        def get_label(self,
                circuit_model):
            """Get a label for the circuit model.

            Parameters
            --------------------------------------------------------------------
            circuit_model :: ModelCircuit
            """
            pass

        def get_cell_density(self,
                circuit_model,
                spatial_parameters):
            """Get volume density of (neuronal) cells in a circuit.
            This method must be defined for the model adapter class that will
            adapt a circuit model to the requirements of this analysis.

            Parameters
            --------------------------------------------------------------------
            circuit_model :: ModelCircuit
            spatial_parameter :: SpatialParameter # that cell density is to be
            ~ # measured by, eg layer, multiple parameters can b used, for
            ~ # example for cell densities by cortical region and layer.
            ~ # Such a call should return a dataframe with a MultiIndex.
            
            Returns
            --------------------------------------------------------------------
            Record(phenomenon :: Phenomenon, #that was measured
            ~      data :: DataFrame["mean", "std"],
            ~      method :: String)

            Example
            --------------------------------------------------------------------
            If 'spatial_parameter' is 'CorticalLayer', the adapter should return
            cell density as a function of cortical layers in the circuit.
            """
            pass

    def get_measurement(self,
            circuit_model,
            *args, **kwargs):
        """Get measurement of the cell density."""
        return\
            self.adapter\
                .get_cell_density(
                    circuit_model,
                    spatial_parameters=self.spatial_parameters,
                    *args, **kwargs)
