"""
Analyze cell density in a circuit model.
"""
import os
import numpy as np
import pandas as pd
from dmt.tk.journal import Logger
from dmt.model.interface import Interface
from dmt.tk.field import Field
from dmt.tk.field import lazyfield as Section
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.plotting import Bars, LinePlot
from dmt.tk.plotting.multi import MultiPlot
from dmt.tk.parameters import Parameters
from neuro_dmt import terminology
from neuro_dmt.analysis.circuit import BrainCircuitAnalysis
from neuro_dmt.analysis.reporting import\
    CircuitAnalysisReport,\
    CheetahReporter
from neuro_dmt.data import rat
from neuro_dmt.models.bluebrain.circuit.geometry import Cuboid
from .import BrainCircuitCompositionAnalysis


LOGGER = Logger(client=__file__, level="DEBUG")


class CellDensityAnalysisByLayer(BrainCircuitCompositionAnalysis):
    """
    Analyze the cell density composition of a brain circuit model.
    """
    @Section
    def introduction(self):
        return """
        A circuit model should reproduce experimentally measured cell densities.
        For the mammalian cerebral cortex, the simplest measurement to validate
        against is the cell density of each layer.
        In this analysis, we use three experimentally measured reference
        datasets (see References section) to validate layer cell densities.
        """
    @Section
    def methods(self):
        return """
        Cell density was measured in randomly sampled boxes of dimension {}
        with their position conditioned to lie in the modeled brain's spatial
        region specified by a named brain-region and layer. Cell density was
        measured as the number of total (neuronal) cells in the sampled cuboid
        divided by its volume, and the result was converted the 1000 cells per
        mm^3.

        Reference data shown alongside the model measurement was measured
        (somwhere) in the rat SSCx. Specific sub-region for the reference data
        is not known, and the same datasets have been show as reference in all
        plotted brain-regions.
        """
    @lazyfield
    def reference_data(xelf):
        return {
            "DeFelipe2017": rat.defelipe2017.summary_measurement,
            "DeFelipe2014": rat.defelipe2014.summary_measurement,
            "Meyer2010": rat.meyer2010}

    def get_measurement(self, circuit_model, adapter):
        """
        Measure a model circuit's cell density by layer.
        """
        regions =\
            adapter.get_brain_regions(circuit_model)
        layers =\
            adapter.get_layers(circuit_model)
        measurement_parameters =\
            pd.DataFrame({
                "region": [r for r in regions for _ in layers],
                "layer":  [l for _ in regions for l in layers]})

        def _retrieve(query):
            cuboid_of_interest =\
                self._get_random_region(
                    circuit_model, adapter, query)
            cell_count =\
                adapter.get_cells(
                    circuit_model,
                    roi=cuboid_of_interest.bbox)
            return 1.e9 * cell_count / cuboid_of_interest.volume

        return pd.concat([
            measurement_parameters.assign(
                cell_density=measurement_parameters.apply(_retrieve, axis=1),
                dataset=adapter.get_label(circuit_model))
            for _ in range(self.sample_size)]
        ).set_index(
            ["dataset", list(measurement_parameters.columns.values)])


class CellDensityAnalysisByCorticalDepth(BrainCircuitCompositionAnalysis):
    """
    Analyze the cell density composition of a brain circuit model.
    """
    @Section
    def introduction(self):
        return """
        A circuit model should reproduce experimentally measured cell densities.
        For the mammalian cerebral cortex, the simplest measurement to validate
        against is the cell density of each layer.
        In this analysis, we use three experimentally measured reference
        datasets (see References section) to validate layer cell densities.
        """
    @Section
    def methods(self):
        return """
        Cell density was measured in randomly sampled boxes of dimension {}
        with their position conditioned to lie in the modeled brain's spatial
        region specified by a named brain-region and cortical-depth. Cell 
        density was measured as the number of total (neuronal) cells in the 
        sampled cuboid divided by its volume, and the result was converted the 
        1000  cells per mm^3.
        """

    def get_measurement(self, circuit_model, adapter):
        """
        Measure a model circuit's cell density by layer.
        """
        regions =\
            pd.Series(
                adapter.get_brain_regions(circuit_model),
                name="region")
        depth_begins =\
            np.linspace(0., 2500., 51)
        depth_ends =\
            depth_begins + 50.
        measurement_parameters =\
            pd.concat([
                pd.DataFrame({
                    ("depth", "begin"): depth_begins,
                    ("depth", "end"):   depth_ends,
                    "region": regions})
                for _ in range(self.sample_size())])

        def _retrieve(query):
            cuboid_of_interest =\
                self._get_random_region(
                    circuit_model, adapter, query)
            cell_count =\
                adapter.get_cells(
                    circuit_model,
                    roi=cuboid_of_interest.bbox)
            return 1.e9 * cell_count / cuboid_of_interest.volume

        return pd.concat([
            measurement_parameters.assign(
                cell_density=measurement_parameters.apply(_retrieve, axis=1),
                dataset=adapter.get_label(circuit_model))
            for _ in range(self.sample_size)
        ]).set_index(
                ["dataset", list(measurement_parameters.columns.values)])

        


