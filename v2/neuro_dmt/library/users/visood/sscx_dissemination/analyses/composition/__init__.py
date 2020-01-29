"""
Analysis circuit composition.
"""

import os
from copy import deepcopy
import numpy as np
import pandas as pd
from dmt.tk.journal import Logger
from dmt.model.interface import Interface
from dmt.tk.field import WithFields, Field, lazyfield
from dmt.tk.author import Author
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.plotting import Bars, LinePlot
from dmt.tk.plotting.multi import MultiPlot
from dmt.tk.parameters import Parameters
from dmt.data.observation import measurement
from neuro_dmt import terminology
from neuro_dmt.analysis.circuit import BrainCircuitAnalysis
from neuro_dmt.analysis.reporting import\
    CircuitAnalysisReport,\
    CheetahReporter
from neuro_dmt.data import rat
from neuro_dmt.models.bluebrain.circuit.geometry import Cuboid
from neuro_dmt.models.bluebrain.circuit.adapter.adapter import measurement_method


LOGGER = Logger(client=__file__, level="DEBUG")


class CompositionAnalysesSuite(WithFields):
    """
    Analyze the composition of a brain circuit model.
    """
    sample_size = Field(
        """
        Number of individual sample measurements for each set of parameter
        values.
        """,
        __default_value__=100)
    size_roi = Field(
        """
        Size of ROIs that composition phenomena will be computed in.
        """,
        __default_value__ = 50. * np.ones(3))
    path_reports = Field(
        """
        Location where the reports will be posted.
        """,
        __default_value__=os.path.join(os.getcwd(), "reports"))
    bin_size_cortical_thickness = Field(
        """
        Size of bins in um to be used to bin depth / height.
        """,
        __default_value__=100)
    maximum_cortical_thickness = Field(
        """
        Maximum cortical thickness will be used to measure phenomena by depth
        or height.
        """,
        __default_value__=2500.)


    @lazyfield
    def number_cortical_thickness_bins(self):
        """..."""
        return\
            1 + np.floor(
                self.maximum_cortical_thickness / self.bin_size_cortical_thickness)

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
 
    def _get_random_cells(self, circuit_model, adapter, spatial_query):
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
                circuit_model, roi=roi.bbox)


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

    @lazyfield
    def parameters_regions_and_layers(self):
        """..."""
        def _regions_and_layers(adapter, circuit_model):
            """..."""
            regions =\
                adapter.get_brain_regions(circuit_model)
            layers =\
                adapter.get_layers(circuit_model)
            return\
                pd.DataFrame({
                    "region": [r for r in regions for _ in layers],
                    "layer":  [l for _ in regions for l in layers]})

        return\
            Parameters(
                _regions_and_layers,
                labels=("region", "layer"))

    @lazyfield
    def parameters_regions_and_depths(self):
        """..."""
        def _regions_and_depths(adapter, circuit_model):
            regions =\
                adapter.get_brain_regions(circuit_model)
            depths =\
                np.linspace(
                    0.,
                    self.maximum_cortical_thickness,
                    self.number_cortical_thickness_bins)
            return\
                pd.DataFrame({
                    ("region", ""): [r for r in regions for _ in depths],
                    ("depth", "begin"): [d for _ in regions for d in depths],
                    ("depth", "end"): [d + self.bin_size_cortical_thickness
                                  for _ in regions for d in depths]})

        return\
            Parameters(
                _regions_and_depths,
                labels=("region", "depth"))

    @lazyfield
    def phenomenon_cell_density(self):
        return\
            Phenomenon(
                "Cell Density",
                "Number of cells in a unit volume (mm^3)",
                group="Composition")

    @lazyfield
    def phenomenon_inhibitory_cell_fraction(self):
        return\
            Phenomenon(
                "Inhibitory Cell Fraction",
                "Fraction of inhibitory cells",
                group="Composition")

    def sampled_reference_data(self, reference_data):
        return {
            label: dataset.samples(20)
            for label, dataset in reference_data.items()}


    def reference_data_cell_density(self, brain_regions=None):
        """..."""
        defelipe2017 =\
            deepcopy(
                rat.defelipe2017.summary_measurement)
        defelipe2014 =\
            deepcopy(
                rat.defelipe2014.summary_measurement)
        meyer2010 =\
            deepcopy(
                rat.meyer2010)
        nsamples = 1000
        if brain_regions is not None:
            defelipe2017.data =\
                self._with_brain_regions(
                    defelipe2017.samples(nsamples), brain_regions)
            defelipe2014.data =\
                self._with_brain_regions(
                    defelipe2014.samples(nsamples), brain_regions)
            meyer2010.data =\
                self._with_brain_regions(
                    meyer2010.samples(nsamples), brain_regions)
        else:
            defelipe2017.data =\
                defelipe2017.samples(nsamples)
            defelipe2014.data =\
                defelipe2014.samples(nsamples)
            meyer2010.data =\
                meyer2010.samples(nsamples)

        return {
            "InputConstraintDeFelipe2017": defelipe2017,
            "DeFelipe2014": defelipe2014,
            "Meyer2010": meyer2010}

    def reference_data_inhibitory_cell_fraction(self, brain_regions=None):
        """..."""
        ghobril2012 =\
            deepcopy(rat.ghobril2012)
        lefort2009 =\
            deepcopy(rat.lefort2009)
        beaulieu1992 =\
            deepcopy(rat.beaulieu1992)
        input_constraint =\
            deepcopy(rat.input_constraint_inhibitory_fraction)
        nsamples = 1000
        if brain_regions is not None:
            ghobril2012.data =\
                self._with_brain_regions(
                    ghobril2012.samples(nsamples), brain_regions)
            lefort2009.data =\
                self._with_brain_regions(
                    lefort2009.samples(nsamples), brain_regions)
            beaulieu1992.data =\
                self._with_brain_regions(
                    beaulieu1992.samples(nsamples), brain_regions)
            input_constraint.data =\
                self._with_brain_regions(
                    input_constraint.samples(nsamples), brain_regions)
        else:
            ghobril2012.data =\
                ghobril2012.samples(nsamples)
            lefort2009.data =\
                lefort2009.samples(nsamples)
            beaulieu1992.data =\
                beaulieu1992.samples(nsamples)
            input_constraint.data =\
                input_constraint.samples(nsamples)
        return {
            "InputConstraint": input_constraint,
            "Ghobril2012": ghobril2012,
            "LeFort2009": lefort2009,
            "Beaulieu1992": beaulieu1992}


    @measurement_method("""
    Cells were counted in a randomly sampled cube (see Methods for dimensions),
    that was required to be centered in the location specified by a spatial
    query.
    """)
    def measurement_cell_density_using_sampling(self,
            circuit_model,
            adapter,
            **query):
        """
        Get cell density in circuit model using an adapter that provides
        the methods defined in `AdapterInterface`, by sampling random regions
        in circuit space specified by a query.
        """
        spatial_query =\
            terminology.circuit.get_spatial_query(query)
        cuboid_to_measure =\
            self._get_random_region(
                circuit_model, adapter, spatial_query)
        cell_count =\
            adapter.get_cells(
                circuit_model, roi=cuboid_to_measure
            ).shape[0]
        spatial_volume =\
            cuboid_to_measure.volume
        return 1.e9 * cell_count / spatial_volume

    @lazyfield
    def analysis_cell_density_by_layer_using_sampling(self):
        """..."""
        return\
            BrainCircuitAnalysis(
                introduction="""
                A circuit model should reproduce experimentally measured cell 
                densities. For the mammalian cerebral cortex, the simplest 
                measurement to validate against is the cell density of each 
                layer. In this analysis we use three experimentally measured 
                reference datasets (see References section) to validate layer 
                cell densities of the circuit model {label}.
                """,
                methods="""
                Cell density was measured in randomly sampled boxes of
                dimension {}. Each sampled box was conditioned to lie in a
                the spatial location specified by brain-region and layer.
                The plot shows mean and standard-deviation of cell densities
                sampled from {} cubes. Reference data plotted alongside model 
                measurements was measured (somewhere) in the SSCx. Specific 
                sub-region for the reference data is not known. all sub-regions 
                in these plots show the same reference data.
                """.format(self.size_roi, self.sample_size),
                phenomenon=self.phenomenon_cell_density,
                AdapterInterface=self.AdapterInterface,
                measurement_parameters=self.parameters_regions_and_layers,
                sample_measurement=self.measurement_cell_density_using_sampling,
                plotter=MultiPlot(
                    mvar="region",
                    plotter=Bars(
                        xvar="layer",
                        xlabel="Layer",
                        yvar="cell_density",
                        ylabel="Cell Density",
                        gvar="dataset")),
                report=CircuitAnalysisReport)

    @lazyfield
    def analysis_region_cell_density_by_layer_using_sampling(self):
        """..."""
        return\
            BrainCircuitAnalysis(
                introduction="""
                A circuit model should reproduce experimentally measured data.
                For layered brain tissue, cell densities by layer are a
                fundamental structural property of circuit composition that
                must be analyzed to evaluate the validity of the circuit model.
                In this analysis we compare cell density by layer across the
                brain-regions modeled in the circuit model {label}
                """,
                methods="""
                Cell density was measured in randomly sampled boxes of
                dimension {}. Each sampled box was conditioned to lie in a
                the spatial location specified by brain-region and layer.
                The plot shows mean and standard-deviation of cell densities
                sampled from {} cubes. 
                """.format(self.size_roi, self.sample_size),
                phenomenon=self.phenomenon_cell_density,
                AdapterInterface=self.AdapterInterface,
                measurement_parameters=self.parameters_regions_and_layers,
                sample_measurement=self.measurement_cell_density_using_sampling,
                plotter=Bars(
                    xvar="layer",
                    xlabel="Layer",
                    yvar="cell_density",
                    ylabel="Cell Density",
                    gvar="region"))

    @lazyfield
    def analysis_cell_density_by_depth_using_sampling(self):
        """..."""
        return\
            BrainCircuitAnalysis(
                introduction="""
                Dependence of cell density on cortical depth is analyzed.
                """,
                methods="""
                A random region of interest (roi) in the shape of a cube was
                sampled at a given depth in the circuit. Number of cells in this
                cube was divided by its volume to obtain the cell density.
                """,
                phenomenon=self.phenomenon_cell_density,
                AdapterInterface=self.AdapterInterface,
                measurement_parameters=self.parameters_regions_and_depths,
                sample_measurement=self.measurement_cell_density_using_sampling,
                plotter=LinePlot(
                    xvar=("depth", "begin"),
                    xlabel="Cortical Depth",
                    yvar="cell_density",
                    ylabel="Cell Density",
                    gvar="region",
                    drawstyle="steps-mid"),
                report=CircuitAnalysisReport)


    @measurement_method("""
    Cells were counted in circuit space specified by a spatial query.
    """)
    def measurement_cell_density_exhaustively(self,
            circuit_model,
            adapter,
            **query):
        """
        Get cell density in circuit model using an adapter that provides
        the methods defined in `AdapterInterface`,  in circuit space specified
        by a query.
        """
        spatial_query =\
            terminology.circuit.get_spatial_query(query)
        cell_count =\
            adapter.get_cells(
                circuit_model, **spatial_query
            ).shape[0]
        spatial_volume =\
            adapter.get_spatial_volume(
                circuit_model, **spatial_query)
        return 1.e9 * cell_count / spatial_volume

    @lazyfield
    def analysis_cell_density_by_layer_exhaustively(self):
        """..."""
        return\
            BrainCircuitAnalysis(
                introduction="""
                A circuit model should reproduce experimentally measured cell 
                densities. For the mammalian cerebral cortex, the simplest 
                measurement to validate against is the cell density of each 
                layer. In this analysis we use three experimentally measured 
                reference datasets (see References section) to validate layer 
                cell densities of the circuit model {label}.
                """,
                methods="""
                Cell density was measured as the total number of cells in
                the circuit's spatial region specified by brain-region and
                layer divided by the volume of the spatial region.
                Specific sub-region for the
                reference data is not known. All sub-regions in these plots
                show the same reference data.
                """,
                phenomenon=self.phenomenon_cell_density,
                AdapterInterface=self.AdapterInterface,
                measurement_parameters=self.parameters_regions_and_layers,
                sample_measurement=self.measurement_cell_density_overall,
                plotter=MultiPlot(
                    mvar="region",
                    plotter=Bars(
                        xvar="layer",
                        xlabel="Layer",
                        yvar="cell_density",
                        ylabel="Cell Density",
                        gvar="dataset")),
                report=CircuitAnalysisReport)


    @measurement_method("""
    Inhibitory and excitatory cells in circuit region specified by a spatial
    query. Number of inhibitory cells was divided by the total number of cells
    to obtain the fraction of inhibitory cells.
    """)
    def measurement_inhibitory_cell_fraction_exhaustively(self,
            circuit_model,
            adapter,
            **query):
        """..."""
        spatial_query =\
            terminology.circuit.get_spatial_query(query)
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

    @lazyfield
    def analysis_inhibitory_cell_fraction_by_layer_exhaustively(self):
        """..."""
        return\
            BrainCircuitAnalysis(
                introduction="""
                A circuit model should reproduce experimentally measured cell
                densities of specific cell types. A characteristic property
                of circuit cell composition is the fraction of inhibitory cells
                in a spatial region of the circuit. For example layer L1 of
                cortical circuits does not have any excitatory cells, and hence
                should have inhibitory cell fraction of 1. In this analysis we 
                present the fraction of inhibitory cells in each layer for 
                different brain-regions populated in the circuit model.
                """,
                methods="""
                Excitatory and inhibitory cell counts were measured in the
                circuit's spatial region specified by brain-region and layer.
                Inhibitory cell fraction was computed as the count of inhibitory
                cells divided by the total number of cells in a specified
                spatial region.
                """,
                phenomenon=self.phenomenon_inhibitory_cell_fraction,
                AdapterInterface=self.AdapterInterface,
                measurement_parameters=self.parameters_regions_and_layers,
                sample_measurement=self.measurement_inhibitory_cell_fraction_exhaustively,
                plotter=MultiPlot(
                    mvar="region",
                    plotter=Bars(
                        xvar="layer",
                        xlabel="Layer",
                        yvar="inhibitory_cell_fraction",
                        ylabel="Inhibitory Cell Fraction",
                        gvar="dataset")),
                report=CircuitAnalysisReport)


    @staticmethod
    def _get_mtype_cell_density(cells, volume):
        """..."""
        return cells.groupby("mtype")\
                    .agg("size")\
                    .rename("cell_density")\
                    .apply(lambda density: 1.e9 * density / volume)
                        #["mtype"] + list(spatial_query.keys()))

    @measurement_method("""
    Cells were counted, by their mtype, in randomly sampled cubes (see Methods
    for dimensions), that was centered in the location specified by a spatial 
    query.
    """)
    def measurement_mtype_cell_density_using_sampling(self,
            circuit_model,
            adapter,
            **query):
        """..."""
        spatial_query =\
            terminology.circuit.get_spatial_query(query)
        cuboid =\
            self._get_random_region(
                circuit_model, adapter, spatial_query)
        cells =\
            adapter.get_cells(
                circuit_model, roi=cuboid)
        return self._get_mtype_cell_density(
            cells, cuboid.volume, spatial_query)

    @lazyfield
    def analysis_mtype_cell_density_by_layer_using_sampling(self):
        """..."""
        return\
            BrainCircuitAnalysis(
                introduction="""
                A circuit model should reproduce experimentally measured cell
                densities. Here we compare layer mtype cell densities across
                regions modeled in a brain circuit model.
                """,
                methods="""
                Cell density was measured by mtype in randomly sampled boxes of
                dimension {}. Each sampled box was conditioned to lie in a
                spatial location of the brain specified by its
                brain-region and layer.
                """.format(self.size_roi),
                phenomenon=self.phenomenon_cell_density,
                AdapterInterface=self.AdapterInterface,
                measurement_parameters=self.parameters_regions_and_layers,
                sample_measurement=self.measurement_mtype_cell_density_using_sampling,
                measurement_collection=measurement.collection.series_type,
                plotter=MultiPlot(
                    mvar="mtype",
                    plotter=Bars(
                        xvar="layer",
                        xlabel="Layer",
                        yvar="cell_density",
                        ylabel="Cell Density",
                        gvar="region")))

    @measurement_method("""
    Cells of each mtype were counted in the entire region specified by a query. 
    """)
    def measurement_mtype_cell_density_exhaustively(self,
            circuit_model,
            adapter,
            **query):
        """..."""
        spatial_query =\
            terminology.circuit.get_spatial_query(query)
        cells =\
            adapter.get_cells(
                circuit_model, **spatial_query)
        spatial_volume =\
            adapter.get_spatial_volume(
                circuit_model, **spatial_query)
        return\
            self._get_mtype_cell_density(cells, spatial_volume)

    @lazyfield
    def analysis_mtype_cell_density_by_layer_exhaustively(self):
        """..."""
        return\
            BrainCircuitAnalysis(
                introduction="""
                A circuit model should reproduce experimentally measured cell
                densities. Here we compare layer mtype cell densities across
                regions modeled in a brain circuit model.
                """,
                methods="""
                Cell density for each mtype was measured by mtype in regions of 
                the circuit specified by a spatial query.
                """.format(self.size_roi),
                phenomenon=self.phenomenon_cell_density,
                AdapterInterface=self.AdapterInterface,
                measurement_parameters=self.parameters_regions_and_layers,
                sample_measurement=self.measurement_mtype_cell_density_exhaustively,
                measurement_collection=measurement.collection.series_type,
                plotter=MultiPlot(
                    mvar="mtype",
                    plotter=Bars(
                        xvar="layer",
                        xlabel="Layer",
                        yvar="cell_density",
                        ylabel="Cell Density",
                        gvar="region")))


    @lazyfield
    def analysis_mtype_cell_density_by_depth(self):
        """
        Analysis of mtype cell density.
        """
        return\
            BrainCircuitAnalysis(
                phenomenon=self.phenomenon_cell_density,
                AdapterInterface=self.AdapterInterface,
                reference_data=self.sampled_reference_data(
                    self.reference_data_cell_density.items()),
                measurement_parameters=self.parameters_regions_and_depths,
                sample_measurement=self.sample_measurement_cell_density,
                measurement_collection=measurement.collection.series_type,
                plotter=MultiPlot(
                    mvar="mtype",
                    plotter=LinePlot(
                        xvar="depth",
                        xlabel="Cortical Depth",
                        yvar="cell_density",
                        ylabel="Cell Density",
                        gvar="region")),
                report=CircuitAnalysisReport)

    def __call__(self, circuit_model, adapter):
        """..."""
        adapter =\
            self.AdapterInterface.implementation(
                adapter)
        reporter_analyses =\
            CheetahReporter(
                path_output_folder=os.path.join(
                    self.path_reports,
                    "analyses"))
        brain_regions =\
            adapter.get_brain_regions(circuit_model)
        reference_data_cell_density =\
            self.reference_data_cell_density(brain_regions)

        LOGGER.info(
            "Analyzing circuit {}".format(
                adapter.get_label(circuit_model)))
        sampled_cell_density_validation_report =\
            self.analysis_cell_density_by_layer_using_sampling(
                circuit_model,
                adapter,
                reference_data=reference_data_cell_density,
                sampling_methodology=terminology.sampling_methodology.random,
                sample_size=self.sample_size,
                author=Author.zero)
        LOGGER.info(
            "1. Validate Cell Density.")

        LOGGER.info(
            "\tPOST cell density report")
        LOGGER.info(
            "Cell density validation report generated at {}"\
            .format(
                reporter_analyses.post(
                    sampled_cell_density_validation_report,
                    output_subfolder=os.path.join(
                        "validation", "sampled"))))

        LOGGER.info(
            "2. Analyze Cell Density, exhaustively without sampling regions.")

        exhaustive_cell_density_validation_report =\
            self.analysis_cell_density_by_layer_exhaustively(
                circuit_model,
                adapter,
                reference_data=reference_data_cell_density,
                sampling_methodology=terminology.sampling_methodology.exhaustive,
                author=Author.zero)
        LOGGER.info(
            "\tPOST exhaustively cell density validation report")
        LOGGER.info(
            "exhaustively Cell density validation report generated at {}"\
            .format(
                reporter_analyses.post(
                    exhaustive_cell_density_validation_report,
                    output_subfolder=os.path.join(
                        "validation", "exhaustive"))))

        sampled_cell_density_analysis_report =\
            self.analysis_region_cell_density_by_layer_using_sampling(
                circuit_model,
                adapter,
                sampling_methodology=terminology.sampling_methodology.exhaustive,
                sample_size=self.sample_size,
                author=Author.zero)
        LOGGER.info(
            "\tPOST exhaustive cell density analysis report")
        LOGGER.info(
            "exhaustive Cell density analysis report generated at {}"\
            .format(
                reporter_analyses.post(
                    sampled_cell_density_analysis_report,
                    output_subfolder=os.path.join(
                        "exhaustive", "by-layer"))))


        LOGGER.info(
            "3. Analyze Inhibitory Cell Fraction.")
        reference_data_inhibitory_cell_fraction =\
            self.reference_data_inhibitory_cell_fraction(brain_regions)
        inhibitory_cell_fraction_validation_report =\
            self.analysis_inhibitory_cell_fraction_by_layer_exhaustively(
                circuit_model,
                adapter,
                reference_data=reference_data_inhibitory_cell_fraction,
                sampling_methodology=terminology.sampling_methodology.exhaustive,
                author=Author.zero)
        LOGGER.info(
            "\tPOST inhibitory cell fraction report")
        LOGGER.info(
            "Inhibitory cell fraction analysis report generated at {}"\
            .format(
                reporter_analyses.post(
                    inhibitory_cell_fraction_validation_report,
                    output_subfolder=os.path.join(
                        "validation", "exhaustive"))))

        # LOGGER.info(
        #     "4. Analyze Mtype Cell Density by Layer.")
        # mtype_cell_density_by_layer_report =\
        #     self.analysis_mtype_cell_density(
        #         circuit_model,
        #         adapter,
        #         methodology=terminology.sampling_methodolgy.random)
        # LOGGER.info(
        #     "\tPOST mtype cell density by layer report")
        # LOGGER.info(
        #     "Mtype cell density by layer analysis report generated at {}"\
        #     .format(
        #         reporter.post(mtype_cell_density_by_layer_report)))

        LOGGER.info(
            "DONE")
