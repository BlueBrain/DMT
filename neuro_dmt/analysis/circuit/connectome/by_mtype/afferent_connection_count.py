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


class AfferentConnectionCountAnalysis(
        ByMtypePathwayConnectomeAnalysis):
    """Analyze number of connections by mytpe --> mtype pathway."""

    def __init__(self,
            *args, **kwargs):
        """Initialize Me"""
        phenomenon=\
            Phenomenon(
                "Pathway Afferent Connection Count",
                """Number of afferent connections in an mtype --> mtype,
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
            bin[1] for bin in soma_distances]
        #    np.mean(bin) for bin in soma_distances]
        assert len(x_positions) >= 2
        delta_x=\
            x_positions[1] - x_positions[0]
        if not region:
            regions=\
                set(measurement_index["region"].values)
            if len(regions) != 1:
                self.logger.error(
                    self.logger.get_source_info(),
                    """Current implementation of {}
                    allows only 1 region in measured data.
                    Measured data had {}"""\
                    .format(
                        self.__class__.__name__,
                        len(regions)))
                raise ValueError(
                    """Current implementation of {}
                    allows only 1 region in measured data"""\
                    .format(self.__class__.__name__))
            region=\
                regions.pop()
        afferent_mtypes=\
            self._get_aggregated_pathways(
                model_measurement,
                direction="AFF")
        def __get_plot(post_mtype):
            self.logger.info(
                self.logger.get_source_info(),
                "plot {} for post mtype {}"\
                .format(
                    self.__class__.__name__,
                    post_mtype))
            figure=\
                golden_figure(
                    height=kwargs.get("height", None),
                    width=kwargs.get("width", 14))
            axes=\
                figure.subplots()
            pre_mtypes=\
                afferent_mtypes[post_mtype]
            colors=\
                plt.cm.RdYlBu(
                    np.linspace(
                        1., 0., len(pre_mtypes)))
            post_mtype_data=\
                measurement_data.xs(
                    (region, post_mtype),
                    level=("region", "post_mtype"))
            for color, pre_mtype in zip(colors, pre_mtypes):
                afferent_counts=\
                    post_mtype_data\
                    .reindex(
                        pd.MultiIndex.from_product(
                            [[pre_mtype], soma_distances],
                            names=["pre_mtype", "soma_distance"]))\
                    .fillna(0.)\
                    .xs(pre_mtype, level="pre_mtype")
                max_count=\
                    np.nanmax(
                        afferent_counts["mean"])
                if max_count == 0.:
                    continue
                label=\
                    pre_mtype if max_count > 1.\
                    else "_nolegend_"
                plt.step(
                    x_positions,
                    afferent_counts["mean"],
                    #width=delta_x,
                    #yerr=afferent_counts["std"],
                    label=label,
                    alpha=0.75,
                    color=color,
                    #color="white",
                    #edgecolor=color,
                    linewidth=4,
                    linestyle="solid")
            plt.xticks(
                x_positions,
                x_positions,
                #soma_distances,
                rotation=90,
                fontsize=8)
            plt.legend()
            plt.title(
                "Region {} Mtype {}:AFF"\
                .format(
                    region,
                    post_mtype),
                fontsize=24)
            axes.set_ylabel(
                "Number of Connections",
                fontsize=16)
            axes.set_xlabel(
                "Soma Distance",
                fontsize=16)
            plt.tight_layout()
            return figure
        post_mtypes={
            post_mtype for _, post_mtype in self.pathways_to_analyze}
        return {
            "{}:AFF".format(post_mtype): __get_plot(post_mtype)
            for post_mtype in post_mtypes}

    def get_measurement(self,
            circuit_model,
            *args, **kwargs):
        """Get a (statistical) measurement  of the phenomenon analyzed."""
        return\
            self.adapter\
                .get_pathway_afferent_connection_count_by_distance(
                    circuit_model,
                    parameters=self.measurement_parameters,
                    pathways=self.pathways_to_analyze,
                    *args, **kwargs)
