"""Analysis of mtype cell densities by layer."""
from dmt.model.interface import Interface
from dmt.vtk.phenomenon import Phenomenon
from neuro_dmt.analysis.report.single_phenomenon\
    import AnalysisMultiFigureReport
from neuro_dmt.analysis.circuit.composition.by_layer\
    import ByLayerCompositionAnalysis


class MtypeCellDensityAnalysis(
        ByLayerCompositionAnalysis):
    """Analyze cell density by layer for each mtype in the circuit.
    """
    def __init__(self,
            *args, **kwargs):
        """..."""
        super().__init__(
            Phenomenon(
                "Mtype Cell Density",
                "Count of cells of a given mtype in a unit volume.",
                group="composition"),
            ReportType=AnalysisMultiFigureReport,
            *args, **kwargs)

    class AdapterInterface(
            Interface):
        """All methods listed here must be implemented by an adapter for this
        interface."""
        def get_label(self,
            circuit_model):
            """Get a label for the cirucit model.
            Parameters
            --------------
            circuit_model :: CircuitModel"""
            pass

        def get_mtype_cell_density(self,
            circuit_model,
            spatial_parameters):
            """"Get volume density of (neuronal) cells in a circuit.
            This method must be define for the model adapter class that will
            adapt a circuit model to the requirements of this analysis.

            Parameters
            -------------------------------------------------------------------
            circuit_model :: CircuitModel
            spatial_parameters :: [SpatialParameter] # that cell density is to
            ~ # measured by, eg layer, multiple parameters can b used, for
            ~ # example for cell densities by cortical region and layer.
            ~ # Such a call should return a dataframe with a MultiIndex.
            Return
            -------------------------------------------------------------------
            Record[
            ~   phenomenon :: Phenomenon, # that was measured
            ~   data :: DataFrame # with  multi-indexed columns 
            ~                     # Mtype[ [mean], [std]]
            """
            pass

    def get_measurement(self,
            circuit_model,
            *args, **kwargs):
        """Get a measurement of mtype cell densities."""
        return\
            self.adapter\
                .get_mtype_cell_density(
                    circuit_model,
                    spatial_parameters=self.spatial_parameters)

    def plot(self,
            model_measurement,
            *args, **kwargs):
        """Override super's plot method.
        The super's plot method assumes that we need a single plot.
        However, here we will plot means and stds for more than one mtype.
        We override to produce one plot figure for each mtype. We can implement
        a new Plotter that makes a multi-plot with as many subplots as the
        number of mtypes. The code will be useful for such a multi-plot.
        The code below is guided by an instance of the dataframe returned by
        the code that we will use to obtain mtype cell densities for Blue Brain
        Circuits. The code, therefore expects an equivalent dataframe to work.
        """
        measurement_labels=\
            model_measurement.data.columns.levels[0]
        yvar=\
            model_measurement.phenomenon.label
        title_common=\
            model_measurement.phenomenon.name

        def __get_plot(column_label):
            """..."""
            return\
                self.Plotter(
                    model_measurement)\
                    .analyzing(
                        column_label)\
                    .plotting(
                        self.plotting_parameter.label)\
                    .versus(
                        self.plotting_parameter.label)\
                    .given(
                        **self._for_given_parameter_values(
                            **kwargs))\
                    .with_customization(
                        title="{} {}".format(column_label, title_common),
                        **kwargs)\
                    .plot()

        return{
            label: __get_plot(label)
            for label in measurement_labels}

