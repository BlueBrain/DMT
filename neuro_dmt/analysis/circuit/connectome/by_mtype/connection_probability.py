"""Analyze connection probabilty by mtype -> mtype pathway."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dmt.model.interface\
    import Interface
from dmt.vtk.phenomenon\
    import Phenomenon
from dmt.vtk.plotting\
    import HeatMap\
    ,      LinePlot\
    ,      BarPlot\
    ,      golden_figure
from neuro_dmt.analysis.report.single_phenomenon\
    import AnalysisReport\
    ,      AnalysisMultiFigureReport
from neuro_dmt.analysis.circuit.connectome.by_mtype\
    import ByMtypePathwayConnectomeAnalysis


class PathwayConnectionProbabilityAnalysis(
        ByMtypePathwayConnectomeAnalysis):
    """Analyze probability of connections by mytpe --> mtype pathway."""

    def __init__(self,
            *args, **kwargs):
        """Initialize Me"""
        self._by_distance=\
            kwargs.get(
                "by_distance",
                True)
        self._upper_bound_soma_distance=\
            kwargs.get("upper_bound_soma_distance", 300.)\
            if not self._by_distance else\
               None
        self._plot_view=\
            kwargs.get(
                "plot_view",
                "Both")
        phenomenon=\
            Phenomenon(
                "Pathway Connection Probability",
                """Probability of connections in an mtype --> mtype
                pathway conditioned by soma-distance.""",
                group="connectome")\
                if self._by_distance else\
                   Phenomenon(
                       "Pathway Connection Probability",
                       "Probability of connections in an mtype --> mtype.""",
                       group="connectome")
        kwargs["ReportType"]=\
            kwargs.get(
                "ReportType",
                AnalysisMultiFigureReport\
                if self._by_distance else\
                AnalysisReport)
        kwargs["Plotter"]=\
            kwargs.get(
                "Plotter",
                LinePlot\
                if self._by_distance else\
                HeatMap)
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


    def __plot_efferent_view(self,
            measurement_data,
            region,
            soma_distances,
            width=14):
        """..."""
        measurement_index=\
            measurement_data.index.to_frame()
        x_positions=[
            bin[1] for bin in soma_distances]
       #     np.mean(bin) for bin in soma_distances]
        assert len(x_positions) >= 2
        delta_x=\
            x_positions[1] - x_positions[0]
        efferent_mtypes=\
            self._get_aggregated_pathways(
                measurement_data,
                direction="EFF")
        def __get_plot(pre_mtype):
            self.logger.info(
                self.logger.get_source_info(),
                """plot {} for pre mtype {}"""\
                .format(
                    self.__class__.__name__,
                    pre_mtype))
            figure=\
                golden_figure(
                    width=width)
            axes=\
                figure.subplots()
            post_mtypes=\
                efferent_mtypes[pre_mtype]
            colors=\
                plt.cm.RdYlBu(
                    np.linspace(
                        1., 0., len(post_mtypes)))
            pre_mtype_data=\
                measurement_data.xs(
                    (region, pre_mtype),
                    level=("region", "pre_mtype"))
            for color, post_mtype in zip(colors, post_mtypes):
                efferent_probs=\
                    pre_mtype_data\
                    .reindex(
                        pd.MultiIndex.from_product(
                            [[post_mtype], soma_distances],
                            names=["post_mtype", "soma_distance"]))\
                    .fillna(0.)\
                    .xs(post_mtype, level="post_mtype")
                max_prob=\
                    np.nanmax(
                        efferent_probs["mean"])
                if max_prob == 0.:
                    continue
                label=\
                    "{}-->{}".format(pre_mtype, post_mtype)\
                    if max_prob > 0.05\
                    else "_nolegend_"
                plt.step(
                    x_positions,
                    efferent_probs["mean"],
                    #width=delta_x,
                    #yerr=efferent_counts["std"],
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
                "Region {} {} Efferent View".format(
                    region,
                    pre_mtype),
                fontsize=24)
            axes.set_ylabel(
                "Probability that two cells are connected.",
                fontsize=16)
            axes.set_ylim(
                0.,
                np.nanmax(pre_mtype_data["mean"]) + 0.1)
            axes.set_xlabel(
                "Soma Distance",
                fontsize=16)
            plt.tight_layout()
            return figure
        pre_mtypes={
            pre_mtype for pre_mtype, _ in self.pathways_to_analyze}
        return {
            "{}: EFF".format(pre_mtype): __get_plot(pre_mtype)
            for pre_mtype in pre_mtypes}

    def __plot_afferent_view(self,
            measurement_data,
            region,
            soma_distances,
            width=14):
        """..."""
        x_positions=[
            bin[1] for bin in soma_distances]
            #np.mean(bin) for bin in soma_distances]
        assert len(x_positions) >= 2
        delta_x=\
            x_positions[1] - x_positions[0]
        afferent_mtypes=\
            self._get_aggregated_pathways(
                measurement_data,
                direction="AFF")
        def __get_plot(post_mtype):
            self.logger.info(
                self.logger.get_source_info(),
                """plot {} for post mtype {}"""\
                .format(
                    self.__class__.__name__,
                    post_mtype))
            figure=\
                golden_figure(
                    width=width)
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
                afferent_probs=\
                    post_mtype_data\
                    .reindex(
                        pd.MultiIndex.from_product(
                            [[pre_mtype], soma_distances],
                            names=["pre_mtype", "soma_distance"]))\
                    .fillna(0.)\
                    .xs(pre_mtype, level="pre_mtype")
                max_prob=\
                    np.nanmax(
                        afferent_probs["mean"])
                if max_prob == 0.:
                    continue
                label=\
                    "{}-->{}".format(pre_mtype, post_mtype)\
                    if max_prob > 0.01 else\
                       "_nolegend_"
                plt.step(
                    x_positions,
                    afferent_probs["mean"],
                    #width=delta_x,
                    #yerr=efferent_counts["std"],
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
                "Region {} {} Afferent View".format(
                    region,
                    post_mtype),
                fontsize=24)
            axes.set_ylabel(
                "Probability that two cells are connected.",
                fontsize=16)
            axes.set_ylim(
                0.,
                np.nanmax(post_mtype_data["mean"]) + 0.1)
            axes.set_xlabel(
                "Soma Distance",
                fontsize=16)
            plt.tight_layout()
            return figure
        post_mtypes={
            post_mtype for _, post_mtype in self.pathways_to_analyze}
        return {
            "{}: AFF".format(post_mtype): __get_plot(post_mtype)
            for post_mtype in post_mtypes}

    def plot(self,
            model_measurement,
            region=None,
            *args, **kwargs):
        """Override to consider distance dependence."""
        self.logger.debug(
            self.logger.get_source_info(),
            "plot conn prob from data {}".format(model_measurement.data))
        if not self._by_distance:
            return\
                super().plot(
                    model_measurement,
                    region=region,
                    *args, **kwargs)
        measurement_data=\
            model_measurement\
            .data\
            [model_measurement.label]\
            .sort_values(by="soma_distance")\
            [["mean", "std"]]
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

        figures_efferent=\
            lambda: self.__plot_efferent_view(
                measurement_data,
                region,
                soma_distances)
        figures_afferent=\
            lambda: self.__plot_afferent_view(
                measurement_data,
                region,
                soma_distances)
        if self._plot_view == "EFF":
            figures=\
                figures_efferent()
        elif self._plot_view == "AFF":
            figures=\
                figures_afferent()
        else:
            figures=\
                figures_efferent()
            figures.udpate(
                figures_afferent())
        return figures

    # def plot(self,
    #         model_measurement,
    #         *args, **kwargs):
    #     """Override to consider distance dependence."""
    #     if not self._by_distance:
    #         # data=\
    #         #     model_measurement.data
    #         # index_tuples=[
    #         #     (region, pre_mtype, post_mtype)
    #         #     for region, pre_mtype, post_mtype,_ in data.index.values]
    #         # model_measurement.data=\
    #         #     pd.DataFrame(
    #         #         data.values,
    #         #         columns=data.columns,
    #         #         index=pd.MultiIndex.from_tuples(
    #         #             tuples=index_tuples,
    #         #             names=["region", "pre_mtype", "post_mtype"]))
    #         return\
    #             super().plot(
    #                 model_measurement,
    #                 *args, **kwargs)
    #     yvar=\
    #         model_measurement.phenomenon.label
    #     title_common=\
    #         model_measurement.phenomenon.name
    #     def __get_plot(
    #             region,
    #             pre_mtype,
    #             post_mtype):
    #         """assuming that there is only one region in model_measurement"""
    #         return\
    #             LinePlot(
    #                 model_measurement
    #             ).plotting(
    #                 "Connection Probability"
    #             ).versus(
    #                 "Soma Distance"
    #             ).given(
    #                 region=region,
    #                 pre_mtype=pre_mtype,
    #                 post_mtype=post_mtype
    #             ).with_customization(
    #                 title="Pathway {}-->{} in region".format(
    #                     pre_mtype,
    #                     post_mtype,
    #                     region),
    #                 ylabel="Connection Probability",
    #                 axis={
    #                     "ymin": 0.,
    #                     "ymax": 1.},
    #                 **kwargs
    #             ).plot()
    #     measurement_index=\
    #         model_measurement\
    #           .data\
    #           .index\
    #           .to_frame()[
    #               ["region", "pre_mtype", "post_mtype"]]\
    #           .values
    #     figure_parameters=[
    #         tuple(xs) for xs in measurement_index] 
    #     return {
    #         parameters: __get_plot(*parameters)
    #         for parameters in figure_parameters}

    def get_measurement(self,
            circuit_model,
            *args, **kwargs):
        """Get a (statistical) measurement  of the phenomenon analyzed."""
        if not self._by_distance:
            kwargs["upper_bound_soma_distance"]=\
                kwargs.get(
                    "upper_bound_soma_distance",
                    self._upper_bound_soma_distance)
        return\
            self.adapter\
                .get_pathway_connection_probability(
                    circuit_model,
                    parameters=self.measurement_parameters,
                    pathways=self.pathways_to_analyze,
                    *args, **kwargs)
