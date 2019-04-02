"""Analyze number of efferent connections by mtype -> mtype pathway."""
import numpy as np
import pandas as pd
from dmt.model.interface\
    import Interface
from dmt.vtk.phenomenon\
    import Phenomenon
from dmt.vtk.plotting\
    import HeatMap\
    ,      LinePlot\
    ,      BarPlot
from neuro_dmt.analysis.report.single_phenomenon\
    import AnalysisReport\
    ,      AnalysisMultiFigureReport
from neuro_dmt.analysis.circuit.connectome.by_mtype\
    import ByMtypePathwayConnectomeAnalysis


class EfferentConnectionCount(
        ByMtypePathwayConnectomeAnalysis):
    """Analyze probability of connections by mytpe --> mtype pathway."""

    def __init__(self,
            *args, **kwargs):
        """Initialize Me"""
        phenomenon=\
            Phenomenon(
                "Pathway Efferent Connection Count",
                """Number of efferent connections in an mtype --> mtype,
                by distance.""",
                group="connectome")
        kwargs["ReportType"]=\
            AnalysisMultiFigureReport
        kwargs["Plotter"]=\
            BarPlot
        super().__init__(
            phenomenon,
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

        def get_pathway_efferent_connection_count(self,
                circuit_model,
                parameters=[],
                pathways=set(),
                cache_size=100,
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
            measurement_data=\
                model_measurement.data
            measurement_index=\
                model_measurement.data.index
            soma_distances=\
                np.unique(
                    measurement_index.to_frame()["soma_distance"].values)
            pre_mtypes={
                pre_mtype for pre_mtype, _ in self.pathways_to_analyze}
            def __get_efferent_mtypes(mtype):
                return {
                    post_mtype
                    for pre_mtype, post_mtype in self.pathways_to_analyze
                    if pre_mtype == mtype}
            xtick_positions=\
                np.arange(len(soma_distances))
            for pre_mtype in pre_mtypes:
                post_mtypes=\
                    __get_efferent_mtypes(pre_mtype)

            
            some_post_mtypes=\
                ["L5_TPC:A", "L5_TPC:B", "L4_TPC", "L3_TPC:A", "L3_TPC:B", "L2_TPC:A"]

            colors = plt.cm.RdYlBu(np.linspace(1., 0., len(some_post_mtypes)))
            for color, post_mtype in zip(colors, some_post_mtypes):
                df = eccm_ssp.data[["mean", "std"]].xs(
                    ("SSp-ll@left", "L2_TPC:A", post_mtype),
                level=("region", "pre_mtype", "post_mtype"))
                plt.bar(
                    np.arange(df.shape[0]),
                    df["mean"],
                    width=1.0,
                    #yerr=df["std"],
                    label=post_mtype,
                    alpha=0.2,
                    color=color,
                    edgecolor="black",
                    linewidth=1,
                linestyle="dashed")
                plt.xticks(
                    xtick_positions,
                    l2tpca_l5tpca.index,
                rotation=90)
                plt.legend()
                
    def get_measurement(self,
            circuit_model,
            *args, **kwargs):
        """Get a (statistical) measurement  of the phenomenon analyzed."""
        return\
            self.adapter\
                .get_pathway_efferent_connection_count(
                    circuit_model,
                    parameters=self.measurement_parameters,
                    pathways=self.pathways_to_analyze,
                    *args, **kwargs)
