"""
Analysis circuit composition.
"""

import os
import numpy as np
import pandas as pd
from dmt.tk.journal import Logger
from dmt.model.interface import Interface
from dmt.tk.field import Field
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.plotting import Bars, LinePlot
from dmt.tk.plotting.multi import MultiPlot
from dmt.tk.parameters import Parameters
from neuro_dmt.analysis.circuit import BrainCircuitAnalysis
from neuro_dmt.analysis.reporting import\
    CircuitAnalysisReport,\
    CheetahReporter
from neuro_dmt.data import rat
from neuro_dmt.models.bluebrain.circuit.geometry import Cuboid


LOGGER = Logger(client=__file__, level="DEBUG")

class BrainCircuitCompositionAnalysis(BrainCircuitAnalysis):
    """
    Analyze the composition of a brain circuit.
    Circuit composition phenomena are measured in randomly sampled
    regions of interest (ROIs). The location of these ROIs can be specified
    by brain region, cortical layer, cortical depth, or cortical height.
    """

    sample_size = Field(
        """
        Number of individual sample measurements for each set of parameter
        values.
        """,
        __default_value__=20)
    size_roi = Field(
        """
        Size of ROIs that composition phenomena will be computed in.
        """,
        __default_value__ = np.array([50., 50., 50.]) )
    path_reports = Field(
        """
        Location where the reports will be posted.
        """,
        __default_value__=os.getcwd())

    class AdapterInterface(Interface):
        """
        Document the methods that will be used by this analysis to measure a
        circuit model. Users must adapt the functionality of their circuit model
        to provide the methods defined in this `Interface`. They may implement
        their adapter as a class or a module.
        """

        def get_provenance(self, circuit_model):
            """
            Provide a dictionary with following keys:

            1. label: that names the circuit model
            2. authors: group that built the circuit model
            3. release_date: when the circuit model was released in its final form
            4. location: a URI from where the circuit model can be loaded
            5. animal: whose brain was modeled
            6  age: of the animal at which the brain was modeled
            7. brain_region: name of the region in the brain modeled 
            """
            raise NotImplementedError

        def get_brain_regions(self, circuit_model):
            """
            A list of named regions in the `circuit_model`.
            """
            raise NotImplementedError

        def get_layers(self, circuit_model):
            """
            A list of layers in the `circuit_model`
            """
            raise NotImplementedError

        def random_position(self,
                circuit_model,
                region=None,
                layer=None,
                depth=None,
                height=None):
            """
            Get a random position in the circuit space that falls in the region
            specified by the query arguments.

            Arguments
            ================
            `circuit_model`: model of a brain circuit
            `layer`: Cortical layer in which the cells should be counted.
            `region`: Named brain region in which the random position should lie.
            
            How this method's result will be used
            =======================================
            A cuboid ROI of specified size will be defined around the
            random position returned by this method, and passed to the
            adapter method `get_cell_count` to obtain the number of cells in
            the ROI. Ratio of number of cells to the ROI volume will be 
            cell density. Multiple values of cell density obtained this way,
            for the same argument values will be constitute sample cell density
            values that will be then be analyzed.
            
            Returns
            ===============
            A 3D np.ndarray providing the X, Y, and Z components of a position
            in the circuit space.
            """
            raise NotImplementedError

        def get_cells(self, circuit_model, properties=None, **query):
            """
            Get cells in a region of interest.

            Arguments
            ============
            properties: Cell properties to load
            roi: A cuboidal region of interest encoded as two diagonally opposite
            ~    corners of the box.

            Returns
            =============
            pandas.DataFrame containing all relevant cell properties as columns.
            """
            raise NotImplementedError


    @staticmethod
    def bars_against_layers_plotter(phenomenon):
        """..."""
        return\
            MultiPlot(
                mvar="region",
                plotter=Bars(
                    xvar="layer",
                    xlabel="Layer",
                    yvar=phenomenon.label,
                    ylabel=phenomenon.name,
                    gvar="dataset"))

    def get_cell_density_measurement(self, circuit_model, adapter):
        """
        Get cell density in `circuit_model` using the `adapter` that provides
        the methods defined in `AdapterInterface`.
        """
        adapter = self.AdapterInterface.implementation(adapter)

        regions = adapter.get_brain_regions(circuit_model)
        layers = adapter.get_layers(circuit_model)
        measurement_parameters = pd.concat( self.sample_size * [
            pd.DataFrame({
                "region": [r for r in regions for _ in layers],
                "layer":  [l for _ in regions for l in layers]})])

        def _random_region(spatial_query):
            """..."""
            position =\
                adapter.random_position(
                    circuit_model,
                    **spatial_query)
            return\
                Cuboid(
                    position - self.size_roi / 2.,
                    position + self.size_roi / 2.)

        def _cell_density(spatial_query):
            """..."""
            roi =\
                _random_region(spatial_query)
            cell_count =\
                adapter.get_cells(circuit_model, roi=roi.bbox).shape[0]
            return 1.e9 * cell_count / roi.volume

        return\
            measurement_parameters.assign(
                cell_density = lambda df: df.apply(
                    lambda row: _cell_density(row), axis=1),
                dataset = adapter.get_label(circuit_model)
            ).set_index(
                ["dataset"] + list(measurement_parameters.columns.values))

    @staticmethod
    def _with_brain_regions(dataframe, brain_regions):
        """
        Insert a column for brain regions
        """
        return\
            pd.concat([
                dataframe.reset_index(
                ).assign(
                    region=region
                ).set_index(
                    ["region", "layer"]
                ) for region in brain_regions])
        
    def get_cell_density_report(self,
            circuit_model,
            adapter):
        """
        Measure cell densities and generate a report.
        """
        phenomenon =\
            Phenomenon(
                "Cell Density",
                "Number of cells in a unit volume.",
                group="Composition")
        brain_regions = adapter.get_brain_regions(circuit_model)
        reference_data ={
            "DeFelipe2017": rat.defelipe2017.summary_measurement,
            "DeFelipe2014": rat.defelipe2014.summary_measurement,
            "Meyer2010": rat.meyer2010}
        measurement =\
            self.get_cell_density_measurement(circuit_model, adapter)
        plotter =\
            self.bars_against_layers_plotter(
                phenomenon)
        caption = """
        Cell density was measured in randomly sampled boxes of
        dimension {} with their position conditioned to lie in a
        specified brain region and layer. The plot shows mean and
        standard-deviation of thus sampled cell densities.
        Reference data plotted alongside model measurements was
        measured (somewhere) in the SSCx. Specific sub-region for the
        reference data is not known. All sub-regions in these plots
        show the same reference data.
        """.format(self.size_roi).replace('\n', ' ')
        figures =\
            plotter.get_figures(
                self._with_reference_data(
                    measurement,
                    {label: self._with_brain_regions(
                        reference_dataset.samples(1000),
                        brain_regions)
                     for label, reference_dataset in reference_data.items()}),
                caption=caption)
        introduction = """
        A circuit model should reproduce experimentally measured cell densities.
        For the mammalian cerebral cortex, the simplest measurement to validate
        against is the cell density of each layer. In this analysis we use
        three experimentally measured reference datasets
        (see References section) to validate layer cell densities of the
        circuit model {}.
        """.format(
            adapter.get_label(circuit_model)
        ).replace(
            '\n', ' ')
        methods =  """
        Cell density was measured in randomly sampled boxes of
        dimension {} with their position conditioned to lie in a
        specified brain region and layer. The plot shows mean and
        standard-deviation of thus sampled cell densities.
        Reference data plotted alongside model measurements was
        measured (somewhere) in the SSCx. Specific sub-region for the
        reference data is not known. All sub-regions in these plots
        show the same reference data.
        """.format(
            self.size_roi,
        ).replace(
            '\n', ' ')
        return\
            CircuitAnalysisReport(
                phenomenon=phenomenon.label,
                measurement=measurement,
                figures=figures,
                introduction=introduction,
                methods=methods,
                results="Results are presented as figures",
                discussion="Results will be discussed after a review",
                references={
                    label: reference.citation
                    for label, reference in reference_data.items()},
                **adapter.get_provenance(circuit_model))
 
    def __call__(self, circuit_model, adapter):
        """..."""
        adapter =\
            self.AdapterInterface.implementation(
                adapter)
        reporter =\
            CheetahReporter(
                path_output_folder=os.path.join(
                    self.path_reports,
                    "analyses"))
        LOGGER.info(
            "Analyzing circuit {}".format(
                adapter.get_label(circuit_model)))
        LOGGER.info(
            "1. Analyze Cell Density.")
        cell_density_report =\
            self.get_cell_density_report(
                circuit_model,
                adapter)
        LOGGER.info(
            "\tPOST cell density report")
        LOGGER.info(
            "Cell density analysis report generated at {}"\
            .format(
                reporter.post(cell_density_report)))
        LOGGER.info(
            "DONE")
