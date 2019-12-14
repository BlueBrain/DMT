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
from neuro_dmt import terminology
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
        __default_value__ = np.array([100., 100., 100.]) )
    path_reports = Field(
        """
        Location where the reports will be posted.
        """,
        __default_value__=os.getcwd())
    analyzed_phenomenon = {
        "cell_density": Phenomenon(
            "Cell Density",
            "Number of cells in a unit volume (mm^3)",
            group="Composition"),
        "inhibitory_cell_fraction": Phenomenon(
            "Inhibitory Cell Fraction",
            "Fraction of inhibitory cells.",
            group="Composition")}

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

        def get_spatial_volume(self, circuit_model, **spatial_query):
            """
            Get total volume in circuit space that satisfies a spatial query.
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

    def _get_random_region(self, circuit_model, adapter, spatial_query):
        """
        Get a random region in the circuit model space.
        """
        position =\
            adapter.random_position(
                circuit_model,
                **spatial_query)
        return\
            Cuboid(
                position - self.size_roi / 2.,
                position + self.size_roi / 2.)

    def _random_cells(self, circuit_model, adapter, spatial_query):
        """
        Get cell density in a region specified by query.

        Arguments
        --------------
        spatial_query : A dict specifying a region in the circuit model space,
        """
        roi =\
            self._get_random_region(
                circuit_model, adapter, spatial_query)
        return\
            adapter.get_cells(
                circuit_model, roi=roi.bbox
            )
    def get_cell_density_measurement(self,
            circuit_model,
            adapter,
            exhaustive=False):
        """
        Get cell density in `circuit_model` using the `adapter` that provides
        the methods defined in `AdapterInterface`.

        Arguments
        ===========
        exhaustive :: If True cell density will be measured over all the entire
        circuit space specified by brain-region and layer.
        """

        regions =\
            adapter.get_brain_regions(circuit_model)
        layers =\
            adapter.get_layers(circuit_model)
        regions_and_layers =\
            pd.DataFrame({
                "region": [r for r in regions for _ in layers],
                "layer":  [l for _ in regions for l in layers]})
        measurement_parameters =\
            pd.concat(self.sample_size * [regions_and_layers])\
            if not exhaustive else\
               regions_and_layers

        def _retrieve(query):
            if not exhaustive:
                cuboid_of_interest =\
                    self._get_random_region(
                        circuit_model, adapter, query)
                cell_count =\
                    adapter.get_cells(
                        circuit_model,
                        roi=cuboid_of_interest.bbox
                    ).shape[0]
                return 1.e9 * cell_count / cuboid_of_interest.volume

            cell_count =\
                adapter.get_cells(
                    circuit_model,
                    **query).shape[0]
            spatial_volume =\
                adapter.get_spatial_volume(
                    circuit_model,
                    **query)
            return cell_count / spatial_volume

        return\
            measurement_parameters.assign(
                cell_density = measurement_parameters.apply(_retrieve, axis=1),
                dataset = adapter.get_label(circuit_model)
            ).set_index(
                ["dataset"] + list(measurement_parameters.columns.values))

    def get_mtype_cell_density_by_layer_measurement(self,
            circuit_model,
            adapter):
        """..."""
        regions = adapter.get_brain_regions(circuit_model)
        layers = adapter.get_layers(circuit_model)
        measurement_parameters =\
            pd.DataFrame({
                "region": [r for r in regions for _ in layers],
                "layer":  [l for _ in regions for l in layers]})

        def _retrieve(query):
            cuboid =\
                self._get_random_region(
                    circuit_model, adapter, query)
            cells =\
                adapter.get_cells(
                    circuit_model, roi=cuboid)
            return\
                cells.groupby("mtype")\
                     .agg("size")\
                     .rename("cell_density")\
                     .apply(lambda density: 1.e9 * density / cuboid.volume)\
                     .reset_index()\
                     .assign(**query)\
                     .set_index(
                         ["mtype"] + list(query.keys()))

        return pd.concat([
            _retrieve(query)
            for _, query in measurement_parameters.iterrows()
            for _ in range(self.sample_size)])

    def get_inhibitory_cell_fraction_measurement(self,
            circuit_model,
            adapter,
            exhaustive=True):
        """
        Get the fraction of inhibitory cells in  `circuit_model` using the
        `adapter` that provides  the methods defined in `AdapterInterface`.

        Arguments
        ============
        exhaustive :: If True, cells in the entire region in circuit space
        specified by a spatial query will be considered.
        """
        regions = adapter.get_brain_regions(circuit_model)
        layers = adapter.get_layers(circuit_model)
        measurement_parameters = pd.concat( self.sample_size * [
            pd.DataFrame({
                "region": [r for r in regions for _ in layers],
                "layer":  [l for _ in regions for l in layers]})])

        def _retrieve(spatial_query):
            """..."""
            if not exhaustive:
                roi =\
                    self._get_random_region(
                        circuit_model,
                        adapter,
                        spatial_query)
                number_synapse_class =\
                    adapter.get_cells(circuit_model,roi=roi.bbox)\
                           .groupby(terminology.cell.synapse_class)\
                           .agg("size")
                if number_synapse_class.empty:
                    return np.nan
                try:
                    return number_synapse_class["INH"] / number_synapse_class.sum()
                except KeyError:
                    pass
                return 0.

            number_synapse_class =\
                adapter.get_cells(circuit_model, **spatial_query)\
                       .groupby(terminology.cell.synapse_class)\
                       .agg("size")
            if number_synapse_class.empty:
                return np.nan
            try:
                return number_synapse_class["INH"] / number_synapse_class.sum()
            except KeyError:
                pass
            return 0.
            
        return\
            measurement_parameters.assign(
                inhibitory_cell_fraction=lambda df: df.apply(_retrieve, axis=1),
                dataset=adapter.get_label(circuit_model)
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
            adapter,
            exhaustive=False):
        """
        Measure cell densities and generate a report.

        Arguments
        =============
        exhaustive :: If True, cell density will be computed over the entire
        circuit space specified by layer and brain-region.
        """
        phenomenon =\
            self.analyzed_phenomenon[
                "cell_density"]
        brain_regions = adapter.get_brain_regions(circuit_model)
        reference_data ={
            "DeFelipe2017": rat.defelipe2017.summary_measurement,
            "DeFelipe2014": rat.defelipe2014.summary_measurement,
            "Meyer2010": rat.meyer2010}
        measurement =\
            self.get_cell_density_measurement(
                circuit_model,
                adapter,
                exhaustive=exhaustive)
        plotter =\
            MultiPlot(
                mvar="region",
                plotter=Bars(
                    xvar="layer",
                    xlabel="Layer",
                    yvar=phenomenon.label,
                    ylabel=phenomenon.name,
                    gvar="dataset"))
        caption =\
            """
            Cell density was measured in randomly sampled boxes of
            dimension {} with their position conditioned to lie in a
            specified brain region and layer. The plot shows mean and
            standard-deviation of thus sampled cell densities.
            Reference data plotted alongside model measurements was
            measured (somewhere) in the SSCx. Specific sub-region for the
            reference data is not known. All sub-regions in these plots
            show the same reference data.
            """.format(self.size_roi)\
            if not exhaustive else\
                    """
                    Cell density was measured as the total number of cells in
                    the circuit's spatial region specified by brain-region and
                    layer divided by the volume of the spatial region.
                    Specific sub-region for the
                    reference data is not known. All sub-regions in these plots
                    show the same reference data.
                    """

        figures =\
            plotter.get_figures(
                self._with_reference_data(
                    measurement,
                    {label: self._with_brain_regions(
                        reference_dataset.samples(100),
                        brain_regions)
                     for label, reference_dataset in reference_data.items()}),
                caption=caption)
        introduction =\
            """
            A circuit model should reproduce experimentally measured cell 
            densities. For the mammalian cerebral cortex, the simplest 
            measurement to validate against is the cell density of each layer.
             In this analysis we use three experimentally measured reference 
            datasets (see References section) to validate layer cell densities 
            of the circuit model {}.
            """.format(adapter.get_label(circuit_model))
        methods =\
            """
            Cell density was measured in randomly sampled boxes of
            dimension {} with their position conditioned to lie in a
            specified brain region and layer. The plot shows mean and
            standard-deviation of thus sampled cell densities.
            Reference data plotted alongside model measurements was
            measured (somewhere) in the SSCx. Specific sub-region for the
            reference data is not known. All sub-regions in these plots
            show the same reference data.
            """.format(self.size_roi))\
                if not exhaustive else\
                   """
                   Cell density was measured as the total number of cells in
                   the circuit's spatial region specified by brain-region and
                   layer divided by the volume of the spatial region.
                   Specific sub-region for the
                   reference data is not known. All sub-regions in these plots
                   show the same reference data.
                   """
        return\
            CircuitAnalysisReport(
                phenomenon="{}{}".format(
                    "sampled_" if not exhaustive else "overall_",
                    phenomenon.label),
                measurement=measurement,
                figures=figures,
                introduction=introduction,
                methods=methods.split('\n'),
                results="Results are presented as figures",
                discussion="Results will be discussed after a review",
                references={
                    label: reference.citation
                    for label, reference in reference_data.items()},
                **adapter.get_provenance(circuit_model))
 
    def get_inhibitory_cell_fraction_report(self,
            circuit_model,
            adapter,
            exhaustive=True):
        """
        Measure cell densities and generate a report.

        Arguments
        ============
        exhaustive :: If True, cells in the entire region in circuit space
        specified by a spatial query will be considered.
        """
        phenomenon =\
            self.analyzed_phenomenon[
                "inhibitory_cell_fraction"]
        brain_regions = adapter.get_brain_regions(circuit_model)
        reference_data = {
            "Ghobril2012": rat.ghobril2012,
            "LeFort2009": rat.lefort2009,
            "Beaulieu1992": rat.beaulieu1992}
        measurement =\
            self.get_inhibitory_cell_fraction_measurement(
                circuit_model,
                adapter,
                exhaustive)
        plotter =\
            MultiPlot(
                mvar="region",
                plotter=Bars(
                    xvar="layer",
                    xlabel="Layer",
                    yvar=phenomenon.label,
                    ylabel=phenomenon.name,
                    gvar="dataset"))
        caption =\
            """
            Fraction of inhibitory cells was measured in randomly sampled boxes 
            of dimension {} with their position conditioned to lie in a
            specified brain region and layer. The plot shows mean and
            standard-deviation of thus sampled cell densities.
            Reference data plotted alongside model measurements was
            measured (somewhere) in the SSCx. Specific sub-region for the
            reference data is not known. All sub-regions in these plots
            show the same reference data.
            """.format(self.size_roi)
        figures =\
            plotter.get_figures(
                self._with_reference_data(
                    measurement,
                    {label: self._with_brain_regions(
                        reference_dataset.samples(1000),
                        brain_regions)
                     for label, reference_dataset in reference_data.items()}),
                caption=caption)
        introduction =\
            """
            A circuit model should reproduce experimentally measured ratio of
            inhibitory cells. For the mammalian cerebral cortex, the simplest 
            measurement to validate against is the fraction of inhibitory 
            cells in each layer. In this analysis we use three experimentally
            measured reference datasets (see References section) to validate
            layer fraction of inhibitory cells in circuit model {}.
            """.format(adapter.get_label(circuit_model))
        methods =\
            """
            Fraction of inhibitory cells was measured in randomly sampled boxes 
            of dimension {} with their position conditioned to lie in a
            specified brain region and layer. The plot shows mean and
            standard-deviation of thus sampled cell densities.
            Reference data plotted alongside model measurements was
            measured (somewhere) in the SSCx. Specific sub-region for the
            reference data is not known. All sub-regions in these plots
            show the same reference data.
            """.format(self.size_roi)
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

    def get_mtype_cell_density_by_layer_report(self,
            circuit_model,
            adapter):
        """
        Measure mtype cell densities and generate a report.
        """
        phenomenon =\
            self.analyzed_phenomenon[
                "cell_density"]
        brain_regions =\
            adapter.get_brain_regions(
                circuit_model)
        measurement =\
            self.get_mtype_cell_density_by_layer_measurement(
                circuit_model,
                adapter)
        plotter =\
            MultiPlot(
                mvar="mtype",
                plotter=Bars(
                    xvar="layer",
                    xlabel="Layer",
                    yvar=phenomenon.label,
                    ylabel=phenomenon.name,
                    gvar="region"))
        caption = """
        Cell density was measured for each cell mtype in randomly sampled boxes
        of dimension {} with their position conditioned to lie in a specified
        brain region and layer. The plot shows mean and standard-deviation of
        the sampled cell densities.
        """.format(self.size_roi).replace('\n', ' ')
        figures =\
            plotter.get_figures(
                {adapter.get_label(circuit_model): measurement},
                caption=caption)
        introduction = """
        A circuit model should reproduce experimentally measured cell densities.
        In addition to the total cell densities by layer, here we analyze cell
        density of each mtype for each layer in all the populated brain regions
        of the circuit model {}
        """.format(adapter.get_label(circuit_model)).replace('\n', ' ')
        methods = """
        Cell density was measured for each cell mtype in randomly sampled boxes
        of dimension {} with their position conditioned to lie in a specified
        brain region and layer. The plot shows mean and standard-deviation of
        the sampled cell densities.
        """.format(self.size_roi).replace('\n', ' ')
        return\
            CircuitAnalysisReport(
                phenomenon="mtype_{}".format(phenomenon.label),
                measurement=measurement,
                figures=figures,
                introduction=introduction,
                methods=methods,
                results="Results are presented as figures",
                discussion="Results will be discussed after a review",
                references={},
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
            "2. Analyze Cell Density, overall without sampling regions.")

        overall_cell_density_report =\
            self.get_cell_density_report(
                circuit_model,
                adapter,
                exhaustive=True)
        LOGGER.info(
            "\tPOST overall cell density report")
        LOGGER.info(
            "Overall Cell density analysis report generated at {}"\
            .format(
                reporter.post(overall_cell_density_report)))

        LOGGER.info(
            "3. Analyze Inhibitory Cell Fraction.")
        inhibitory_cell_fraction_report =\
            self.get_inhibitory_cell_fraction_report(
                circuit_model,
                adapter,
                exhaustive=True)
        LOGGER.info(
            "\tPOST inhibitory cell fraction report")
        LOGGER.info(
            "Inhibitory cell fraction analysis report generated at {}"\
            .format(
                reporter.post(inhibitory_cell_fraction_report)))

        LOGGER.info(
            "4. Analyze Mtype Cell Density by Layer.")
        mtype_cell_density_by_layer_report =\
            self.get_mtype_cell_density_by_layer_report(
                circuit_model,
                adapter)
        LOGGER.info(
            "\tPOST mtype cell density by layer report")
        LOGGER.info(
            "Mtype cell density by layer analysis report generated at {}"\
            .format(
                reporter.post(mtype_cell_density_by_layer_report)))

        LOGGER.info(
            "DONE")
