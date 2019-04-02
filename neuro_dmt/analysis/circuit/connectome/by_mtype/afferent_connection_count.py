"""Analyze number of efferent connections by mtype -> mtype pathway."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dmt.model.interface\
    import Interface
from dmt.vtk.plotting\
    import golden_figure
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


class AfferentConnectionCount(
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

        def get_pathway_afferent_connection_count(self,
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
            region=None,
            *args, **kwargs):
        """Override to consider distance dependence."""
        measurement_data=\
            model_measurement\
            .data\
            .sort_values(by="soma_distance")
        measurement_index=\
            model_measurement.data.index.to_frame()
        soma_distances=\
            sorted(list(set(
                measurement_index["soma_distance"].values)))
        x_positions=[
            np.mean(bin) for bin in soma_distances]
        assert len(x_positions) >= 2
        delta_x=\
            x_positions[1] - x_positions[0]
        if not region:
            regions=\
                set(measurement_index["region"].values)
            assert len(regions) == 1
            region=\
                regions.pop()
        def __get_afferent_mtypes(mtype):
            return {
                pre_mtype
                for pre_mtype, post_mtype in self.pathways_to_analyze
                if post_mtype == mtype}
        def __get_plot(post_mtype):
            figure=\
                golden_figure(
                    height=kwargs.get("height", 8),
                    width=kwargs.get("width", None))
            pre_mtypes=\
                __get_afferent_mtypes(post_mtype)
            colors=\
                plt.cm.RdYlBu(
                    np.linspace(
                        1., 0., len(pre_mtypes)))
            for color, pre_mtype in zip(colors, pre_mtypes):
                afferent_counts=\
                    measurement_data[["mean", "std"]]\
                    .xs((region, pre_mtype, post_mtype),
                        level=("region", "pre_mtype", "post_mtype"))\
                    .reindex(soma_distances)\
                    .fillna(0.)
                plt.bar(
                    x_positions,
                    afferent_counts["mean"],
                    width=delta_x,
                    yerr=afferent_counts["std"],
                    label=post_mtype,
                    alpha=0.75,
                    color="white",
                    edgecolor=color,
                    linewidth=4,
                    linestyle="solid")
            plt.xticks(
                x_positions,
                soma_distances,
                rotation=90)
            plt.legend()
            plt.title(
                "{}: EFF".format(post_mtype))
            plt.ylabel(
                "Number of Connections")
            plt.xlabel(
                "Soma Distance")
            return figure
        post_mtypes={
            post_mtype for _, post_mtype in self.pathways_to_analyze}
        return {
            "{}: AFF".format(post_mtype): __get_plot(post_mtype)
            for post_mtype in post_mtypes}

    def get_measurement(self,
            circuit_model,
            *args, **kwargs):
        """Get a (statistical) measurement  of the phenomenon analyzed."""
        return\
            self.adapter\
                .get_pathway_afferent_connection_count(
                    circuit_model,
                    parameters=self.measurement_parameters,
                    pathways=self.pathways_to_analyze,
                    *args, **kwargs)
