"""By layer analysis of the cell density of a Hippocampus circuit."""

import pandas as pd
from dmt.model.interface import Interface
from dmt.vtk.phenomenon import Phenomenon
from neuro_dmt.analysis.circuit.composition.by_layer\
    import ByLayerCompositionAnalysis
from neuro_dmt.utils.enums import Cell
from neuro_dmt.measurement.parameter\
    import HippocampalLayer
from neuro_dmt.utils.cell_type import CellType

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
                spatial_parameters=None,
                given={}):
            """Get volume density of (neuronal) cells in a circuit.
            This method must be defined for the model adapter class that will
            adapt a circuit model to the requirements of this validation.
            
            Parameters
            --------------------------------------------------------------------
            circuit_model :: ModelCircuit
            spatial_parameters :: set{SpatialParameter} #that cell density be measured against
            given :: dict# providing conditions on cell properties

            Returns
            --------------------------------------------------------------------
            Record(phenomenon :: Phenomenon, #that was measured
            ~      region_label :: String, #label for regions in data
            ~      data :: DataFrame["region", "mean", "std"],
            ~      method :: String)

            Note
            --------------------------------------------------------------------
            If 'spatial_parameters' are 'None', get cell density for the whole
            circuit.
            Example
            --------------------------------------------------------------------
            If 'spatial_parameter' is 'CorticalLayer', the adapter should return
            cell density as a function of cortical layers in the circuit.
            """
            pass


    def get_measurement(self,
            circuit_model,
            *args, **kwargs):
        """Get measurement of the phenomenon validated."""
        ca1_density\
            = self.adapter\
                  .get_cell_density(
                      circuit_model)
        ca1_density.data.index\
            = pd.Index(
                ["CA1"],
                dtype="object",
                name="cell_type")
        sp_pc_density\
            = self.adapter\
                  .get_cell_density(
                      circuit_model,
                      layer="SP",
                      for_cell_type=CellType(
                          morph_class="PYR"))
        sp_pc_density.data.index\
            = pd.Index(
                ["SP_PC"],
                dtype="object",
                name="cell_type")
        hippocampal_layer\
            = HippocampalLayer()
        layer_density\
            = self.adapter\
                  .get_cell_density(
                      circuit_model,
                      spatial_parameters={hippocampal_layer})
        layer_density.data.index\
            = pd.Index(
                [hippocampal_layer.repr(i)
                 for i in layer_density.data.index],
                dtype=object,
                name="cell_type")
        measurement\
            = layer_density
        measurement.data\
            = pd.concat([
                ca1_density.data,
                sp_pc_density.data,
                layer_density.data
            ]).append(
                pd.Series(
                    layer_density.data.loc["SLM"] + layer_density.data.loc["SR"],
                    name="SLM-SR"))
        return measurement
