"""Measure a circuit's connectome grouping cells by their mtypes."""

from dmt.analysis\
    import OfSinglePhenomenon
from dmt.vtk.utils.collections\
    import Record
from dmt.vtk.utils.descriptor\
    import  Field, document_fields
from dmt.vtk.measurement.parameter.group\
    import ParameterGroup
from dmt.vtk.plotting\
    import Plot\
    ,      BarPlot\
    ,      HeatMap
from neuro_dmt.measurement.parameter\
    import BrainCircuitConnectomeParameter
from neuro_dmt.analysis.circuit.connectome\
    import ConnectomeAnalysis
from neuro_dmt.analysis.report.single_phenomenon\
    import AnalysisReport


class ByMtypeConnectomeAnalysis(
        OfSinglePhenomenon,
        ConnectomeAnalysis):
    """Measure a circuit's connectome grouping cells by their mtypes.
    """
    cell_group_parameters = Field(
            __name__ = "cell_group_parameters",
            __typecheck__ = Field.typecheck.collection(
                BrainCircuitConnectomeParameter),
            __doc__ = """A connectome phenomenon must be measured as a
            function of either cell-type (for example mtype) or a
            cell-type --> cell-type pathway. Most often we will use mtype
            as cell-type.""")
    Plotter = Field(
            __name__="Plotter",
            __typecheck__=Field.typecheck.subtype(Plot),
            __default__=BarPlot,
            __doc__="""Plot results...""")

    def __init__(self,
            phenomenon,
            *args, **kwargs):
        """..."""
        if "ReportType" not in kwargs:
            kwargs["ReportType"]=\
                AnalysisReport
        super().__init__(
            phenomenon,
            *args, **kwargs)


class ByMtypePathwayConnectomeAnalysis(
        OfSinglePhenomenon,
        ConnectomeAnalysis):
    """Measure a circuit's connectome's pathway properties using
    mtypes to group pathways (pre-mtype --> post-mtype).
    """
    pathway_parameters = Field(
            __name__ = "pathway_parameters",
            __typecheck__ = Field.typecheck.collection(
                BrainCircuitConnectomeParameter),
            __doc__ = """A connectome phenomenon must be measured as a
            function of either cell-type (for example mtype) or a
            cell-type --> cell-type pathway. Most often we will use mtype
            as cell-type.""")
    pathways_to_analyze = Field(
            __name__="pathways_to_analyze",
            __type__=set,
            __typecheck__=Field.typecheck.collection(tuple),
            __default__=set(),
            __doc__="""Set of pathways as pre/post mtype pairs to be analyzed.
            Empty set will be interpreted as all possible pathways.""")
    Plotter = Field(
            __name__ = "Plotter",
            __typecheck__ = Field.typecheck.subtype(Plot),
            __default__ = HeatMap,
            __doc__ = """Plot results""".format(Plot))

    def __init__(self,
            phenomenon,
            *args, **kwargs):
        """..."""
        if "ReportType" not in kwargs:
            kwargs["ReportType"]=\
                AnalysisReport
        super().__init__(
            phenomenon,
            *args, **kwargs)

    def _get_pathways(self,
            model_measurement):
        """..."""
        data=\
            getattr(
                model_measurement,
                "data",
                model_measurement)
        pre_index=\
            data.index.names.index("pre_mtype")
        post_index=\
            post.index.names.index("post_mtype")
        return[
            (index_value[pre_index], index_value[post_index])
            for index_value in data.index.values]

    def _get_aggregated_pathways(self,
            model_measurement,
            direction="EFF"): #or "AFF"
        """..."""
        pathways=\
            self.pathways_to_analyze if self.pathways_to_analyze else\
            self._get_pathways(model_measurement)
        efferent_pathways = lambda: {
            mtype: sorted(list({
                post_mtype for pre_mtype, post_mtype in pathways
                if pre_mtype == mtype}))
            for mtype in sorted(list({
                    pre_mtype for pre_mtype, _ in pathways}))}
        afferent_pathways = lambda: {
            mtype: sorted(list({
                pre_mtype for pre_mtype, _ in pathways
                if post_mtype == mtype}))
            for mtype in sorted(list({
                    post_mtype for _, post_mtype in pathways}))}
        return\
            efferent_pathways()\
            if direction == "EFF" else\
               afferent_pathways()

    def plot(self,
            model_measurement,
            *args, **kwargs):
        """Override to get pre_mtype and post_mtype
        along the y and x axis respectively."""
        kwargs.update({
            "xvar": "post_mtype" ,
            "yvar": "pre_mtype"})
        return\
            super().plot(
                model_measurement,
                *args, **kwargs)


from neuro_dmt.analysis.circuit.connectome.by_mtype.synapse_count\
    import PairSynapseCountAnalysis
from neuro_dmt.analysis.circuit.connectome.by_mtype.pair_connection\
    import PairConnectionAnalysis
from neuro_dmt.analysis.circuit.connectome.by_mtype.connection_probability\
    import PathwayConnectionProbabilityAnalysis
from neuro_dmt.analysis.circuit.connectome.by_mtype.bouton_density\
    import CellBoutonDensityAnalysis
