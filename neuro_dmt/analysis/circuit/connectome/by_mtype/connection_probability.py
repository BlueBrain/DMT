"""Analyze connection probabilty by mtype -> mtype pathway."""
from dmt.model.interface\
    import Interface
from dmt.vtk.phenomenon\
    import Phenomenon
from dmt.vtk.plotting\
    import HeatMap\
    ,      LinePlot
from neuro_dmt.analysis.report.single_phenomenon\
    import AnalysisReport\
    ,      AnalysisMultiFigureReport
from neuro_dmt.analysis.circuit.connectome.by_mtype\
    import ByMtypePathwayConnectomeAnalysis


class PathwayConnectionProbabilityAnalysis(
        ByMtypePathwayConnectomeAnalysis):
    """Analyze probability of connections by mytpe --> mtype pathway."""

    def __init__(self,
            by_distance=True,
            *args, **kwargs):
        """Initialize Me"""
        self._by_distance=\
            by_distance
        if not by_distance:
            super().__init__(
                Phenomenon(
                    "Pathway Connection Probability",
                    "Probability of connections in an mtype --> mtype pathway.",
                    group="connectome"),
                ReportType=AnalysisReport,
                Plotter=HeatMap,
                *args, **kwargs)
        else:
            super().__init__(
                Phenomenon(
                    "Pathway Connection Probability by Distance",
                    """Probability of connections in an mtype --> mtype
                    pathway conditioned by soma-distance""",
                    group="connectome"),
                ReportType=AnalysisMultiFigureReport,
                Plotter=LinePlot,
                *args, **kwargs)


    class AdapterInterface(
            Interface):
        """All methods listed here must be implemented by an adapter for
        the analyzed circuit (class)."""
        def get_label(self,
                circuit_model):
            """Get a label for the circuit model.

            Parameters
            ------------------
            circuit_model :: ModelCircuit
            """
            pass

        def get_pathway_connection_probability(self,
                circuit_model,
                parameters=[],
                *args, **kwargs):
            """Get statistical summary of the number of synapses between
            pre- and post-synaptic cells in an mtype --> mtype pathway.
            This method must be defined for the model adapter class that will
            adapt a circuit model to the requirements of this analysis.

            Parameters
            -------------------
            circuit_model :: ModelCircuit
            parameters :: provides the pathways for which synapse counts
            ~             are to be computed.
            ~             For eg. [region, pre_mtype, post_mtype, soma_distance]

            Return
            -------------------
            Record[
            ~   phenomenon :: Phenomenon,
            ~   data :: DataFrame<pre_mtype, post_mtype>["mean", "std"]
            ~           #a dataframe with a pre/post mtypes in index
            ~   method :: String #describe how the computation]
            """
            pass

    def plot(self,
            model_measurement,
            *args, **kwargs):
        """Override to consider distance dependence."""
        if not self._by_distance:
            return\
                super().plot(
                    model_measurement,
                    *args, **kwargs)
        #make line plots
        yvar=\
            model_measurement.phenomenon.label
        title_common=\
            model_measurement.phenomenon.name
        def __get_plot(
                region,
                pre_mtype,
                post_mtype):
            """assuming that there is only one region in model_measurement"""
            return\
                LinePlot(
                    model_measurement)\
                .plotting(\
                    "Pathway Connection Probability")\
                .versus(
                    "Soma Distance")\
                .given(
                    region=region,
                    pre_mtype=pre_mtype,
                    post_mtype=post_mtype)\
                .with_customization(
                    title="Pathway {}-->{} in region".format(
                        pre_mtype,
                        post_mtype,
                        region),
                    **kwargs)\
                .plot()
        measurement_index=\
            model_measurement\
              .data\
              .index\
              .to_frame()[
                  ["region", "pre_mtype", "post_mtype"]]\
              .values
        figure_parameters=[
            tuple(xs) for xs in measurement_index] 
        return {
            parameters: __get_plot(*parameters)
            for parameters in figure_parameters}


    def get_measurement(self,
            circuit_model,
            *args, **kwargs):
        """Get a (statistical) measurement  of the phenomenon analyzed."""
        return\
            self.adapter\
                .get_pathway_connection_probability(
                    circuit_model,
                    parameters=self.measurement_parameters,
                    *args, **kwargs)
